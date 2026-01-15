-- Fix Recommendations: Update ratings table and functions
-- Run this in Supabase SQL Editor

-- Step 1: Change item_id from BIGINT to UUID in ratings table
ALTER TABLE ratings ALTER COLUMN item_id TYPE UUID USING item_id::text::uuid;

-- Step 2: Change item_id from BIGINT to UUID in interactions table
ALTER TABLE interactions ALTER COLUMN item_id TYPE UUID USING item_id::text::uuid;

-- Step 3: Drop and recreate get_popular_items function with correct types and lower threshold
DROP FUNCTION IF EXISTS get_popular_items(integer);

CREATE OR REPLACE FUNCTION get_popular_items(
  item_limit int DEFAULT 20
)
RETURNS TABLE (
  item_id uuid,
  item_type text,
  title text,
  avg_rating float,
  rating_count bigint,
  poster_url text
)
LANGUAGE sql STABLE
AS $$
  WITH movie_ratings AS (
    SELECT 
      r.item_id,
      'movie' as item_type,
      m.title,
      AVG(r.rating) as avg_rating,
      COUNT(*) as rating_count,
      m.poster_url
    FROM ratings r
    JOIN movies m ON r.item_id = m.id
    WHERE r.item_type = 'movie'
    GROUP BY r.item_id, m.title, m.poster_url
    HAVING COUNT(*) >= 1  -- Changed from 5 to 1
  ),
  book_ratings AS (
    SELECT 
      r.item_id,
      'book' as item_type,
      b.title,
      AVG(r.rating) as avg_rating,
      COUNT(*) as rating_count,
      b.thumbnail_url as poster_url
    FROM ratings r
    JOIN books b ON r.item_id = b.id
    WHERE r.item_type = 'book'
    GROUP BY r.item_id, b.title, b.thumbnail_url
    HAVING COUNT(*) >= 1  -- Changed from 5 to 1
  )
  SELECT * FROM (
    SELECT * FROM movie_ratings
    UNION ALL
    SELECT * FROM book_ratings
  ) combined
  ORDER BY avg_rating DESC, rating_count DESC
  LIMIT item_limit;
$$;

-- Step 4: Drop and recreate get_collaborative_recommendations with correct types
DROP FUNCTION IF EXISTS get_collaborative_recommendations(bigint, integer);

CREATE OR REPLACE FUNCTION get_collaborative_recommendations(
  target_user_id bigint,
  recommendation_count int DEFAULT 20
)
RETURNS TABLE (
  item_id uuid,
  item_type text,
  title text,
  predicted_rating float,
  poster_url text
)
LANGUAGE plpgsql STABLE
AS $$
BEGIN
  RETURN QUERY
  WITH user_ratings AS (
    -- Get target user's ratings
    SELECT item_id, item_type, rating
    FROM ratings
    WHERE user_id = target_user_id
  ),
  similar_users AS (
    -- Find users with similar taste (Pearson correlation)
    SELECT 
      r2.user_id,
      COUNT(*) as common_items,
      CORR(r1.rating, r2.rating) as similarity
    FROM ratings r1
    JOIN ratings r2 ON r1.item_id = r2.item_id AND r1.item_type = r2.item_type
    WHERE r1.user_id = target_user_id 
      AND r2.user_id != target_user_id
    GROUP BY r2.user_id
    HAVING COUNT(*) >= 2 AND CORR(r1.rating, r2.rating) > 0.2  -- Lowered thresholds
    ORDER BY similarity DESC
    LIMIT 50
  ),
  candidate_items AS (
    -- Get items liked by similar users that target user hasn't rated
    SELECT 
      r.item_id,
      r.item_type,
      AVG(r.rating * su.similarity) / AVG(su.similarity) as predicted_rating
    FROM ratings r
    JOIN similar_users su ON r.user_id = su.user_id
    WHERE NOT EXISTS (
      SELECT 1 FROM user_ratings ur 
      WHERE ur.item_id = r.item_id AND ur.item_type = r.item_type
    )
    GROUP BY r.item_id, r.item_type
    HAVING AVG(r.rating) >= 3.0  -- Lowered from 3.5
  )
  SELECT 
    ci.item_id,
    ci.item_type,
    COALESCE(m.title, b.title) as title,
    ci.predicted_rating,
    COALESCE(m.poster_url, b.thumbnail_url) as poster_url
  FROM candidate_items ci
  LEFT JOIN movies m ON ci.item_type = 'movie' AND ci.item_id = m.id
  LEFT JOIN books b ON ci.item_type = 'book' AND ci.item_id = b.id
  ORDER BY ci.predicted_rating DESC
  LIMIT recommendation_count;
END;
$$;

-- Verify the changes
SELECT 
  'ratings' as table_name,
  column_name, 
  data_type 
FROM information_schema.columns 
WHERE table_name = 'ratings' AND column_name = 'item_id'
UNION ALL
SELECT 
  'interactions' as table_name,
  column_name, 
  data_type 
FROM information_schema.columns 
WHERE table_name = 'interactions' AND column_name = 'item_id';
