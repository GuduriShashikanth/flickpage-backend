# CineLibre 🎬📚

**AI-Powered Semantic Search for Movies & Books**

CineLibre bridges Indian regional cinema with global literature through intelligent semantic search. Instead of keyword matching, it understands the *meaning* behind your queries—search for "gritty crime thriller in a rainy city" and discover content that matches the vibe, not just the words.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Features

- **Semantic Search**: Natural language queries powered by sentence-transformers
- **Cross-Domain Discovery**: Find connections between movies and books
- **Regional Focus**: 2000+ Indian movies across 8 languages (Hindi, Telugu, Tamil, Kannada, Malayalam, Bengali, Marathi, Punjabi)
- **Global Literature**: Hundreds of books across 30+ categories
- **Real-Time Inference**: Sub-50ms embedding generation with FastEmbed
- **Auto-Sync**: Daily data refresh via GitHub Actions
- **Resource Optimized**: Runs on 512MB RAM with <400MB disk footprint

---

## 🏗️ Architecture

```
┌─────────────────┐
│  GitHub Actions │  Daily sync (TMDB + Google Books)
│   Sync Engine   │  → Generate embeddings → Upsert to DB
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Supabase     │  PostgreSQL + pgvector
│   (Database)    │  Cosine similarity search
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI API   │  Local inference (FastEmbed)
│   (Koyeb)       │  /search/semantic endpoint
└─────────────────┘
```

**Tech Stack:**
- **Backend**: FastAPI (Python 3.11)
- **Database**: Supabase (PostgreSQL + pgvector)
- **ML Model**: sentence-transformers/all-MiniLM-L6-v2 (384-dim embeddings)
- **Inference**: FastEmbed (ONNX runtime)
- **Deployment**: Koyeb (serverless)
- **CI/CD**: GitHub Actions
- **Data Sources**: TMDB API, Google Books API

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- Supabase account (free tier works)
- TMDB API key ([get one here](https://www.themoviedb.org/settings/api))

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/cinelibre.git
cd cinelibre
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create `api/.env`:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_role_key
TMDB_API_KEY=your_tmdb_key
PORT=8000
```

5. **Set up Supabase database**

Run these SQL commands in your Supabase SQL editor:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Movies table
CREATE TABLE movies (
  id BIGSERIAL PRIMARY KEY,
  tmdb_id INTEGER UNIQUE NOT NULL,
  title TEXT NOT NULL,
  overview TEXT,
  release_date DATE,
  poster_url TEXT,
  embedding vector(384),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Books table
CREATE TABLE books (
  id BIGSERIAL PRIMARY KEY,
  google_id TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  thumbnail_url TEXT,
  embedding vector(384),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for vector search
CREATE INDEX ON movies USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON books USING ivfflat (embedding vector_cosine_ops);

-- RPC function for movie search
CREATE OR REPLACE FUNCTION match_movies(
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id bigint,
  tmdb_id integer,
  title text,
  overview text,
  release_date date,
  poster_url text,
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
    1 - (embedding <=> query_embedding) AS similarity
  FROM movies
  WHERE 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
$$;

-- RPC function for book search
CREATE OR REPLACE FUNCTION match_books(
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id bigint,
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
```

6. **Run initial data sync**
```bash
python api/sync_engine.py
```

7. **Start the API server**
```bash
python api/main.py
```

The API will be available at `http://localhost:8000`

---

## 🔌 API Usage

### Health Check
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "status": "online",
  "engine": "FastEmbed",
  "ready": true,
  "database": "connected"
}
```

### Semantic Search

**Movies:**
```bash
curl "http://localhost:8000/search/semantic?q=space%20adventure%20with%20robots&type=movie&limit=5"
```

**Books:**
```bash
curl "http://localhost:8000/search/semantic?q=mystery%20in%20a%20small%20town&type=book&limit=5"
```

**Parameters:**
- `q` (required): Natural language query
- `type` (optional): `movie` or `book` (default: `movie`)
- `limit` (optional): Number of results (default: 12)
- `threshold` (optional): Similarity threshold 0-1 (default: 0.4)

**Response:**
```json
{
  "query": "space adventure with robots",
  "results": [
    {
      "id": 123,
      "tmdb_id": 550,
      "title": "Interstellar",
      "overview": "A team of explorers travel through a wormhole...",
      "release_date": "2014-11-07",
      "poster_url": "https://image.tmdb.org/t/p/w500/...",
      "similarity": 0.87
    }
  ]
}
```

---

## 🚢 Deployment

### Koyeb (Recommended)

1. Fork this repository
2. Connect your GitHub account to Koyeb
3. Create a new service from the repository
4. Set environment variables in Koyeb dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `PORT` (auto-set by Koyeb)
5. Deploy!

The `Procfile` is already configured for Gunicorn + Uvicorn workers.

### GitHub Actions Setup

Add these secrets to your repository (Settings → Secrets):
- `TMDB_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `HF_TOKEN` (optional, for Hugging Face models)

The workflow in `.github/workflows/sync.yml` will run daily at midnight UTC.

---

## 🎯 Design Decisions

### Why Local Inference?
External AI APIs (Hugging Face Inference) suffer from cold starts and 503 errors. Local inference ensures consistent sub-50ms response times.

### Why FastEmbed over PyTorch?
Standard ML libraries consume 2GB+ space and 1GB+ RAM. FastEmbed uses ONNX runtime for the same models with only 80MB RAM and 400MB disk.

### Why Separate Sync Engine?
Data ingestion is I/O-heavy and slow. Running it as a background job (GitHub Actions) keeps the API responsive.

### Why pgvector?
Traditional SQL `LIKE` queries can't understand context. Vector similarity search calculates mathematical "distance" between query meaning and content.

---

## 🧪 Performance

- **Embedding Generation**: ~50ms per query
- **Database Search**: ~100-200ms for 2000+ items
- **Total Latency**: <300ms end-to-end
- **Memory Footprint**: 512MB RAM (including OS)
- **Docker Image**: <400MB

---

## 🛠️ Challenges Overcome

**512MB RAM Barrier**
- Set `OMP_NUM_THREADS=1` to prevent thread spawning
- Single worker configuration
- ONNX runtime instead of PyTorch

**2GB Image Limit**
- Removed torch/transformers dependencies
- Switched to fastembed (compressed models)
- Reduced from 4.4GB → 400MB

**Cold Start Issues**
- Moved AI model inside server code
- Singleton pattern for model loading
- Always-warm inference

---

## 🗺️ Roadmap

- [ ] **Phase 4**: User interaction tracking (clicks, ratings, views)
- [ ] **Phase 5**: Collaborative filtering (Surprise/LightFM)
- [ ] **Phase 6**: Hybrid recommendations (CF + content-based)
- [ ] **Phase 7**: React frontend with Tailwind CSS
- [ ] **Phase 8**: A/B testing framework
- [ ] **Phase 9**: Prometheus + Grafana monitoring
- [ ] **Phase 10**: SaaS features (Stripe integration, user accounts)

---

## 📊 Current Status

✅ Semantic search API (content-based)  
✅ 2000+ Indian regional movies  
✅ Global book catalog  
✅ Automated daily sync  
✅ Production deployment (Koyeb)  
⏳ User interaction tracking  
⏳ Collaborative filtering  
⏳ Frontend application  

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [TMDB](https://www.themoviedb.org/) for movie data
- [Google Books API](https://developers.google.com/books) for book data
- [Sentence Transformers](https://www.sbert.net/) for embedding models
- [Qdrant](https://qdrant.tech/) for FastEmbed library
- [Supabase](https://supabase.com/) for managed PostgreSQL + pgvector

---

## 📧 Contact

For questions or feedback, reach out via [GitHub Issues](https://github.com/yourusername/cinelibre/issues).

---

**Built with ❤️ for discovering the perfect movie or book**
