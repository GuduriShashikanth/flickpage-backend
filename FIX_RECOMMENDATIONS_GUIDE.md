# Fix Recommendations Guide

## Problem
Recommendations returning empty arrays even when users have 5+ ratings.

## Root Causes
1. **Schema Mismatch**: `ratings.item_id` was `BIGINT` but `movies.id` and `books.id` are `UUID`
2. **Too Strict Thresholds**: Functions required 5+ ratings per item
3. **No Fallback Logic**: When collaborative filtering failed, no alternatives

## Solution

### Step 1: Run Database Migration (REQUIRED)

Go to Supabase SQL Editor and run `fix_recommendations.sql`:

```sql
-- This will:
-- 1. Change item_id from BIGINT to UUID in ratings table
-- 2. Change item_id from BIGINT to UUID in interactions table
-- 3. Update get_popular_items function (lower threshold to 1 rating)
-- 4. Update get_collaborative_recommendations function (lower thresholds)
```

**Important**: This migration will fix the data type mismatch!

### Step 2: Deploy Updated API

The updated `api/main.py` includes:

1. **Better Fallback Chain**:
   - Try collaborative filtering first
   - If empty, try content-based (similar to user's top-rated items)
   - If still empty, return popular items
   - If no popular items, return recent movies

2. **Content-Based Recommendations**:
   - Finds items similar to user's highly-rated items (4.0+)
   - Uses semantic similarity
   - Deduplicates results

3. **Improved Popular Items**:
   - Returns recent movies if no popular items exist
   - Never returns empty array

### Step 3: Verify

After deployment, test the endpoints:

```bash
# Test personalized recommendations
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app/recommendations/personalized

# Test popular items
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app/recommendations/popular

# Test similar items
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app/recommendations/similar/movie/MOVIE_UUID
```

## How It Works Now

### Personalized Recommendations Flow

```
1. Try Collaborative Filtering
   ↓ (if empty or error)
2. Try Content-Based (similar to user's top-rated items)
   ↓ (if empty or error)
3. Return Popular Items
   ↓ (if empty)
4. Return Recent Movies
```

### Popular Items Flow

```
1. Try get_popular_items() function
   ↓ (if empty)
2. Return Recent Movies (fallback)
```

### Similar Items Flow

```
1. Get item embedding
   ↓
2. Find similar items using semantic search
   ↓
3. Filter out the original item
   ↓
4. Return top N similar items
```

## Expected Results

After the fix:

- **With 1+ ratings**: Users get content-based recommendations
- **With 3+ ratings**: Users get collaborative filtering recommendations
- **With 0 ratings**: Users get popular/recent items
- **Always**: Never returns empty array

## Thresholds (Adjustable)

In `fix_recommendations.sql`:

```sql
-- Collaborative filtering
HAVING COUNT(*) >= 2  -- Min common items between users
AND CORR(r1.rating, r2.rating) > 0.2  -- Min similarity score
HAVING AVG(r.rating) >= 3.0  -- Min average rating

-- Popular items
HAVING COUNT(*) >= 1  -- Min ratings per item
```

In `api/main.py`:

```python
# Content-based recommendations
.gte("rating", 4.0)  # Min rating to consider
"match_threshold": 0.4  # Min similarity score
```

## Troubleshooting

### Still Getting Empty Arrays?

1. **Check migration ran successfully**:
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'ratings' AND column_name = 'item_id';
   -- Should return: uuid
   ```

2. **Check if ratings exist**:
   ```sql
   SELECT COUNT(*) FROM ratings;
   SELECT user_id, COUNT(*) as rating_count 
   FROM ratings 
   GROUP BY user_id;
   ```

3. **Check API logs** for error messages

4. **Verify item_id format** when creating ratings:
   - Should be UUID string, not integer
   - Example: `"ff0b9d75-3b2f-403a-ab5b-1f18ab5e108f"`

### Migration Fails?

If the migration fails because of existing data:

```sql
-- Option 1: Clear ratings and start fresh
TRUNCATE TABLE ratings CASCADE;
TRUNCATE TABLE interactions CASCADE;
-- Then run fix_recommendations.sql

-- Option 2: Manual conversion (if you have important data)
-- Contact for help with data migration
```

## Testing Locally

```python
# test_recommendations.py
import requests

BASE_URL = "https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app"
TOKEN = "your_token_here"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Test personalized
response = requests.get(f"{BASE_URL}/recommendations/personalized", headers=headers)
print("Personalized:", response.json())

# Test popular
response = requests.get(f"{BASE_URL}/recommendations/popular", headers=headers)
print("Popular:", response.json())
```

## Summary

✅ Fixed schema mismatch (BIGINT → UUID)
✅ Lowered thresholds for recommendations
✅ Added content-based fallback
✅ Added recent items fallback
✅ Never returns empty arrays
✅ Better error handling and logging

Run the migration, deploy, and test!
