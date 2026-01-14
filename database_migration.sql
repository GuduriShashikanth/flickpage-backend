-- CineLibre Database Migration Script
-- Run this to update existing database with new schema

-- ==================== DROP EXISTING FUNCTIONS ====================
-- Drop old functions if they exist

DROP FUNCTION IF EXISTS match_movies(vector, double precision, integer);
DROP FUNCTION IF EXISTS match_books(vector, double precision, integer);
DROP FUNCTION IF EXISTS get_popular_items(integer);
DROP FUNCTION IF EXISTS get_collaborative_recommendations(bigint, integer);

-- ==================== CREATE/UPDATE TABLES ====================

-- Users table (create if not exists)
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Ratings table (create if not exists)
-- Note: item_id is stored as UUID (matching movies/books tables)
CREATE TABLE IF NOT EXISTS ratings (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  item_id UUID NOT NULL,
  item_type TEXT NOT NULL CHECK (item_type IN ('movie', 'book')),
  rating FLOAT NOT NULL CHECK (rating >= 0.5 AND rating <= 5.0),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, item_id, item_type)
);

CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_item ON ratings(item_id, item_type);
CREATE INDEX IF NOT EXISTS idx_ratings_created ON ratings(created_at DESC);

-- Interactions table (create if not exists)
-- Note: item_id is stored as UUID (matching movies/books tables)
CREATE TABLE IF NOT EXISTS interactions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  item_id UUID NOT NULL,
  item_type TEXT NOT NULL CHECK (item_type IN ('movie', 'book')),
  interaction_type TEXT NOT NULL CHECK (interaction_type IN ('view', 'click', 'search')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_item ON interactions(item_id, item_type);
CREATE INDEX IF NOT EXISTS idx_interactions_created ON interactions(created_at DESC);

-- Add language column to movies if it doesn't exist
DO $$ 
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='movies' AND column_name='language') THEN
    ALTER TABLE movies ADD COLUMN language TEXT;
  END IF;
END $$;

-- ==================== CREATE NEW RPC FUNCTIONS ====================

-- Function: Match Movies (Semantic Search)
CREATE OR REPLACE FUNCTION match_movies(
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  tmdb_id integer,
  title text,
  overview text,
  release_date date,
  poster_url text,
  language text,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    id,
    tmdb_id,
    title,
    overview,
    release_date,
    poster_url,
    language,
    1 - (embedding <=> query_embedding) AS similarity
  FROM movies
  WHERE 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
$$;

-- Function: Match Books (Semantic Search)
CREATE OR REPLACE FUNCTION match_books(
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  google_id text,
  title text,
  description text,
  thumbnail_url text,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    id,
    google_id,
    title,
    description,
    thumbnail_url,
    1 - (embedding <=> query_embedding) AS similarity
  FROM books
  WHERE 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
$$;

-- Function: Get Popular Items (Based on ratings)
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
    JOIN movies m ON r.item_id::uuid = m.id
    WHERE r.item_type = 'movie'
    GROUP BY r.item_id, m.title, m.poster_url
    HAVING COUNT(*) >= 5
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
    JOIN books b ON r.item_id::uuid = b.id
    WHERE r.item_type = 'book'
    GROUP BY r.item_id, b.title, b.thumbnail_url
    HAVING COUNT(*) >= 5
  )
  SELECT * FROM (
    SELECT * FROM movie_ratings
    UNION ALL
    SELECT * FROM book_ratings
  ) combined
  ORDER BY avg_rating DESC, rating_count DESC
  LIMIT item_limit;
$$;

-- Function: Collaborative Filtering Recommendations
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
    HAVING COUNT(*) >= 3 AND CORR(r1.rating, r2.rating) > 0.3
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
    HAVING AVG(r.rating) >= 3.5
  )
  SELECT 
    ci.item_id,
    ci.item_type,
    COALESCE(m.title, b.title) as title,
    ci.predicted_rating,
    COALESCE(m.poster_url, b.thumbnail_url) as poster_url
  FROM candidate_items ci
  LEFT JOIN movies m ON ci.item_type = 'movie' AND ci.item_id::uuid = m.id
  LEFT JOIN books b ON ci.item_type = 'book' AND ci.item_id::uuid = b.id
  ORDER BY ci.predicted_rating DESC
  LIMIT recommendation_count;
END;
$$;

-- ==================== TRIGGERS ====================

-- Function: Update timestamp on row update
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_ratings_updated_at ON ratings;

-- Create triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ratings_updated_at BEFORE UPDATE ON ratings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== VERIFICATION ====================

-- Verify tables exist
DO $$
DECLARE
  table_count int;
BEGIN
  SELECT COUNT(*) INTO table_count
  FROM information_schema.tables
  WHERE table_schema = 'public'
  AND table_name IN ('users', 'movies', 'books', 'ratings', 'interactions');
  
  RAISE NOTICE 'Tables created: %', table_count;
END $$;

-- Verify functions exist
DO $$
DECLARE
  function_count int;
BEGIN
  SELECT COUNT(*) INTO function_count
  FROM information_schema.routines
  WHERE routine_schema = 'public'
  AND routine_name IN ('match_movies', 'match_books', 'get_popular_items', 'get_collaborative_recommendations');
  
  RAISE NOTICE 'Functions created: %', function_count;
END $$;

-- Success message
DO $$
BEGIN
  RAISE NOTICE '✅ Migration completed successfully!';
  RAISE NOTICE 'Tables: users, movies, books, ratings, interactions';
  RAISE NOTICE 'Functions: match_movies, match_books, get_popular_items, get_collaborative_recommendations';
END $$;
