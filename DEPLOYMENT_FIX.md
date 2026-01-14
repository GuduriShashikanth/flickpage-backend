# CineLibre - Deployment Fix Guide

## Current Status

Your API is deployed at: `https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app`

### What's Working ✅
- Health check
- List movies
- Database connection

### What's Broken ❌
- User registration (500 error)
- Semantic search (401 error - fixed in code, needs redeploy)
- Popular items (500 error)
- All recommendation endpoints

## Root Cause

The **database schema hasn't been set up**. The `users` table and RPC functions don't exist in your Supabase database.

---

## Fix Steps

### Step 1: Setup Database Schema (CRITICAL)

1. **Open Supabase Dashboard**
   - Go to https://supabase.com/dashboard
   - Select your project

2. **Open SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New query"

3. **Copy & Execute Schema**
   - Open the file `database_schema.sql` in your project
   - Copy the ENTIRE contents (all 300+ lines)
   - Paste into Supabase SQL Editor
   - Click "Run" or press Ctrl+Enter

4. **Verify Tables Created**
   - Go to "Table Editor" in Supabase
   - You should see these tables:
     - ✅ users
     - ✅ movies (already exists)
     - ✅ books (already exists)
     - ✅ ratings
     - ✅ interactions

5. **Verify RPC Functions**
   - In SQL Editor, run:
   ```sql
   SELECT routine_name 
   FROM information_schema.routines 
   WHERE routine_schema = 'public' 
   AND routine_type = 'FUNCTION';
   ```
   - You should see:
     - ✅ match_movies
     - ✅ match_books
     - ✅ get_popular_items
     - ✅ get_collaborative_recommendations

---

### Step 2: Redeploy API (Optional but Recommended)

The search endpoint fix needs to be deployed.

**Option A: Git Push (Recommended)**
```bash
git add .
git commit -m "Fix: Remove auth requirement from search endpoint"
git push origin main
```
Koyeb will auto-deploy.

**Option B: Manual Redeploy in Koyeb**
1. Go to Koyeb dashboard
2. Select your service
3. Click "Redeploy"

---

### Step 3: Test Again

Run the diagnostic script:
```bash
python diagnose_api.py
```

Expected output:
```
✅ Health Check - 200
✅ List Movies - 200
✅ Semantic Search - 200
✅ User Registration - 200 or 400 (if user exists)
✅ Popular Items - 200 (might be empty if no ratings yet)
```

---

## Quick Test Commands

### Test Search (Should work after redeploy)
```bash
curl "https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app/search/semantic?q=action&limit=5"
```

### Test Registration (Should work after DB setup)
```bash
curl -X POST https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
```

### Test Popular Items (Should work after DB setup)
```bash
curl "https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app/recommendations/popular?limit=5"
```

---

## Common Issues

### Issue 1: "relation 'users' does not exist"
**Solution:** Run `database_schema.sql` in Supabase SQL Editor

### Issue 2: "function get_popular_items does not exist"
**Solution:** Run `database_schema.sql` in Supabase SQL Editor

### Issue 3: Search still returns 401
**Solution:** Redeploy the API (git push or manual redeploy in Koyeb)

### Issue 4: Popular items returns empty array
**Solution:** This is normal! No ratings exist yet. Add some ratings first:
```bash
# 1. Register a user
# 2. Login to get token
# 3. Rate some movies
curl -X POST https://your-api.koyeb.app/ratings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"item_id":1,"item_type":"movie","rating":4.5}'
```

---

## After Fix - Full Test

Once both steps are complete, run the full test suite:

```bash
python test_deployed_api.py
```

Enter your API URL and choose "Run all tests".

Expected results:
- ✅ Health Check
- ✅ User Registration
- ✅ Get Profile
- ✅ Semantic Search
- ✅ Rate Movie
- ✅ Get My Ratings
- ✅ Similar Items
- ✅ Popular Items (might be empty)
- ✅ Personalized Recommendations (needs multiple users)
- ✅ List Movies

---

## Database Schema Summary

The schema creates:

### Tables
1. **users** - User accounts (email, password_hash, name)
2. **movies** - Movie metadata + embeddings (already exists)
3. **books** - Book metadata + embeddings (already exists)
4. **ratings** - User ratings (user_id, item_id, rating)
5. **interactions** - User behavior tracking

### RPC Functions
1. **match_movies(vector, threshold, count)** - Semantic search for movies
2. **match_books(vector, threshold, count)** - Semantic search for books
3. **get_popular_items(limit)** - Get trending items by ratings
4. **get_collaborative_recommendations(user_id, count)** - User-based CF

### Indexes
- Vector indexes on movies.embedding and books.embedding
- B-tree indexes on user_id, item_id
- Unique constraints on email, tmdb_id, google_id

---

## Verification Checklist

After running the schema:

- [ ] `users` table exists
- [ ] `ratings` table exists
- [ ] `interactions` table exists
- [ ] `match_movies` function exists
- [ ] `match_books` function exists
- [ ] `get_popular_items` function exists
- [ ] `get_collaborative_recommendations` function exists
- [ ] API redeployed
- [ ] Search endpoint works without auth
- [ ] Registration works
- [ ] Can create ratings

---

## Next Steps After Fix

1. **Create test users**
   ```bash
   python test_deployed_api.py
   ```

2. **Add ratings**
   - Register multiple users
   - Have them rate movies
   - This enables collaborative filtering

3. **Test recommendations**
   - After 3+ ratings per user
   - Personalized recommendations will work

4. **Monitor performance**
   - Check Koyeb metrics
   - Verify memory usage < 400MB
   - Check response times

---

## Support

If issues persist:
1. Check Koyeb logs for errors
2. Check Supabase logs
3. Verify environment variables are set
4. Run `diagnose_api.py` for detailed diagnostics

---

**TL;DR:**
1. Run `database_schema.sql` in Supabase SQL Editor
2. Redeploy API (git push)
3. Run `python diagnose_api.py` to verify
4. Run `python test_deployed_api.py` for full test
