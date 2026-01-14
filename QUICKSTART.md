# CineLibre - Quick Start Guide

Get your MovieLens-style recommendation system running in 10 minutes.

## Prerequisites

- Python 3.11+
- Supabase account (free tier)
- TMDB API key (optional for initial testing)

## 1. Clone & Install

```bash
git clone <your-repo>
cd cinelibre
pip install -r requirements.txt
```

## 2. Setup Environment

### Option A: Interactive Setup (Recommended)
```bash
python scripts/setup.py
```

### Option B: Manual Setup
Copy `api/.env.example` to `api/.env` and fill in:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
TMDB_API_KEY=your_tmdb_key
JWT_SECRET_KEY=generate-a-secure-random-string
PORT=8000
```

## 3. Setup Database

1. Open Supabase SQL Editor
2. Copy entire contents of `database_schema.sql`
3. Execute

This creates all tables, indexes, and RPC functions.

## 4. Sync Initial Data

```bash
python api/sync_engine.py
```

This fetches and processes 2000+ movies. Takes 10-30 minutes.

## 5. Start the Server

```bash
python api/main.py
```

Server runs at `http://localhost:8000`

## 6. Test the API

```bash
python test_api.py
```

Or manually:

```bash
# Health check
curl http://localhost:8000/

# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'

# Search
curl "http://localhost:8000/search/semantic?q=action%20thriller&limit=5"
```

## 7. Check Memory Usage (Optional)

```bash
python scripts/check_memory.py
```

Verifies you're under the 512MB Koyeb limit.

---

## API Endpoints Overview

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - Get profile

### Ratings
- `POST /ratings` - Rate a movie/book
- `GET /ratings/my` - Get your ratings
- `DELETE /ratings/{id}` - Remove rating

### Recommendations
- `GET /recommendations/personalized` - Collaborative filtering
- `GET /recommendations/similar/{type}/{id}` - Content-based
- `GET /recommendations/popular` - Trending items

### Search
- `GET /search/semantic` - Natural language search

### Content
- `GET /movies` - List movies
- `GET /movies/{id}` - Movie details
- `GET /books/{id}` - Book details

---

## Deploy to Koyeb

1. Push to GitHub
2. Create Koyeb service from repo
3. Set environment variables
4. Choose Nano instance (512MB)
5. Deploy!

See `BACKEND_SETUP.md` for detailed deployment guide.

---

## Troubleshooting

**"Database not initialized"**
- Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Verify you ran `database_schema.sql`

**"Model Load Failed"**
- Ensure `fastembed` is installed
- Check internet connection (downloads model on first run)

**Out of Memory**
- Verify `OMP_NUM_THREADS=1` is set
- Use single worker: `gunicorn -w 1`

**No recommendations**
- Need at least 3 users with overlapping ratings
- Falls back to popular items for new users

---

## What's Next?

- ✅ Backend complete
- ⏳ Build React frontend
- ⏳ Add caching layer
- ⏳ Implement A/B testing
- ⏳ Add monitoring

See `BACKEND_SETUP.md` for architecture details and advanced configuration.
