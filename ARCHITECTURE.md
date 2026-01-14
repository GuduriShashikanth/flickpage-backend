# CineLibre - System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Browser    │  │  Mobile App  │  │   API Client │      │
│  │   (React)    │  │   (Future)   │  │   (cURL)     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    HTTP/HTTPS + JWT
                             │
┌────────────────────────────┴─────────────────────────────────┐
│                    API GATEWAY (Koyeb)                        │
│                   FastAPI Backend (512MB)                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  AUTHENTICATION                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  JWT Token Management                           │  │  │
│  │  │  - Register/Login                               │  │  │
│  │  │  - Token validation                             │  │  │
│  │  │  - Password hashing (bcrypt)                    │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              RECOMMENDATION ENGINE                     │  │
│  │  ┌──────────────────┐  ┌──────────────────┐          │  │
│  │  │ Collaborative    │  │  Content-Based   │          │  │
│  │  │   Filtering      │  │  Filtering       │          │  │
│  │  │                  │  │                  │          │  │
│  │  │ • User-based CF  │  │ • Vector search  │          │  │
│  │  │ • Pearson corr.  │  │ • Cosine sim.    │          │  │
│  │  │ • SQL-based      │  │ • pgvector       │          │  │
│  │  └──────────────────┘  └──────────────────┘          │  │
│  │                                                        │  │
│  │  ┌──────────────────┐  ┌──────────────────┐          │  │
│  │  │  Popularity      │  │  Hybrid Strategy │          │  │
│  │  │  Based           │  │                  │          │  │
│  │  │                  │  │ • CF primary     │          │  │
│  │  │ • Aggregated     │  │ • CB fallback    │          │  │
│  │  │ • Trending       │  │ • Popular cold   │          │  │
│  │  └──────────────────┘  └──────────────────┘          │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              SEMANTIC SEARCH ENGINE                    │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  FastEmbed (ONNX Runtime)                       │  │  │
│  │  │  - Model: all-MiniLM-L6-v2                      │  │  │
│  │  │  - 384-dimensional embeddings                   │  │  │
│  │  │  - 50ms inference time                          │  │  │
│  │  │  - 80MB memory footprint                        │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              DATA MANAGEMENT                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │   Ratings    │  │ Interactions │  │   Movies   │  │  │
│  │  │   CRUD       │  │  Tracking    │  │   Books    │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────┘
                            │
                    PostgreSQL Protocol
                            │
┌───────────────────────────┴───────────────────────────────────┐
│                  DATABASE LAYER (Supabase)                     │
│                PostgreSQL + pgvector Extension                 │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                      TABLES                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │  users   │  │  movies  │  │  books   │           │   │
│  │  │          │  │ +vectors │  │ +vectors │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  │  ┌──────────┐  ┌──────────────────────┐             │   │
│  │  │ ratings  │  │   interactions       │             │   │
│  │  └──────────┘  └──────────────────────┘             │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                  RPC FUNCTIONS                         │   │
│  │  • match_movies(vector, threshold, count)             │   │
│  │  • match_books(vector, threshold, count)              │   │
│  │  • get_popular_items(limit)                           │   │
│  │  • get_collaborative_recommendations(user_id, count)  │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                     INDEXES                            │   │
│  │  • IVFFlat vector indexes (cosine similarity)         │   │
│  │  • B-tree indexes (user_id, item_id)                  │   │
│  │  • Unique constraints (email, tmdb_id, google_id)     │   │
│  └───────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
                            │
                            │
┌───────────────────────────┴───────────────────────────────────┐
│                   DATA INGESTION LAYER                         │
│                   (GitHub Actions - Daily)                     │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              SYNC ENGINE (sync_engine.py)             │   │
│  │  ┌─────────────────┐         ┌─────────────────┐     │   │
│  │  │   TMDB API      │         │ Google Books    │     │   │
│  │  │   Crawler       │         │    Crawler      │     │   │
│  │  │                 │         │                 │     │   │
│  │  │ • 8 languages   │         │ • 30+ genres    │     │   │
│  │  │ • 2000+ movies  │         │ • Hundreds      │     │   │
│  │  └────────┬────────┘         └────────┬────────┘     │   │
│  │           │                           │              │   │
│  │           └───────────┬───────────────┘              │   │
│  │                       ▼                              │   │
│  │           ┌───────────────────────┐                  │   │
│  │           │  Embedding Generator  │                  │   │
│  │           │  (FastEmbed)          │                  │   │
│  │           └───────────┬───────────┘                  │   │
│  │                       ▼                              │   │
│  │           ┌───────────────────────┐                  │   │
│  │           │  Upsert to Database   │                  │   │
│  │           │  (Deduplication)      │                  │   │
│  │           └───────────────────────┘                  │   │
│  └───────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

---

## Request Flow Diagrams

### 1. User Registration Flow

```
Client                  API                    Database
  │                      │                        │
  │  POST /auth/register │                        │
  ├─────────────────────>│                        │
  │                      │  Check email exists    │
  │                      ├───────────────────────>│
  │                      │<───────────────────────┤
  │                      │  (not found)           │
  │                      │                        │
  │                      │  Hash password         │
  │                      │  (bcrypt)              │
  │                      │                        │
  │                      │  Insert user           │
  │                      ├───────────────────────>│
  │                      │<───────────────────────┤
  │                      │  (user created)        │
  │                      │                        │
  │                      │  Generate JWT          │
  │                      │  (7-day expiry)        │
  │                      │                        │
  │  {token, user}       │                        │
  │<─────────────────────┤                        │
  │                      │                        │
```

### 2. Semantic Search Flow

```
Client                  API                    ML Model              Database
  │                      │                        │                     │
  │  GET /search/semantic│                        │                     │
  │  ?q="action thriller"│                        │                     │
  ├─────────────────────>│                        │                     │
  │                      │  Load model (cached)   │                     │
  │                      ├───────────────────────>│                     │
  │                      │                        │                     │
  │                      │  Generate embedding    │                     │
  │                      │  [0.23, -0.45, ...]    │                     │
  │                      │<───────────────────────┤                     │
  │                      │                        │                     │
  │                      │  RPC: match_movies(vector, 0.4, 12)          │
  │                      ├─────────────────────────────────────────────>│
  │                      │                        │  Vector search      │
  │                      │                        │  (cosine similarity)│
  │                      │<─────────────────────────────────────────────┤
  │                      │  [{movie1}, {movie2}, ...]                   │
  │                      │                        │                     │
  │  {results: [...]}    │                        │                     │
  │<─────────────────────┤                        │                     │
  │                      │                        │                     │
```

### 3. Personalized Recommendations Flow

```
Client                  API                    Database
  │                      │                        │
  │  GET /recommendations│                        │
  │  /personalized       │                        │
  │  Authorization: JWT  │                        │
  ├─────────────────────>│                        │
  │                      │  Validate JWT          │
  │                      │  Extract user_id       │
  │                      │                        │
  │                      │  RPC: get_collaborative_recommendations()    │
  │                      ├─────────────────────────────────────────────>│
  │                      │                        │                     │
  │                      │  1. Find similar users (Pearson correlation) │
  │                      │  2. Get their ratings                        │
  │                      │  3. Predict ratings                          │
  │                      │  4. Filter unrated items                     │
  │                      │  5. Sort by predicted rating                 │
  │                      │                        │                     │
  │                      │<─────────────────────────────────────────────┤
  │                      │  [{item1, score}, {item2, score}, ...]       │
  │                      │                        │                     │
  │  {recommendations}   │                        │                     │
  │<─────────────────────┤                        │                     │
  │                      │                        │                     │
```

### 4. Rating Creation Flow

```
Client                  API                    Database
  │                      │                        │
  │  POST /ratings       │                        │
  │  {item_id, rating}   │                        │
  │  Authorization: JWT  │                        │
  ├─────────────────────>│                        │
  │                      │  Validate JWT          │
  │                      │  Extract user_id       │
  │                      │                        │
  │                      │  Validate rating       │
  │                      │  (0.5 <= r <= 5.0)     │
  │                      │                        │
  │                      │  Upsert rating         │
  │                      │  (user_id, item_id)    │
  │                      ├───────────────────────>│
  │                      │<───────────────────────┤
  │                      │  (rating saved)        │
  │                      │                        │
  │  {rating_id, ...}    │                        │
  │<─────────────────────┤                        │
  │                      │                        │
```

---

## Data Flow

### Movie Data Pipeline

```
TMDB API
    │
    │ Fetch metadata
    │ (title, overview, poster, etc.)
    ▼
Sync Engine
    │
    │ Generate embedding
    │ text = f"{title}. {overview}"
    │ embedding = model.embed(text)
    ▼
Supabase
    │
    │ Upsert (deduplicate by tmdb_id)
    │ Store: metadata + 384-dim vector
    ▼
Available for:
    • Semantic search
    • Content-based recommendations
    • User ratings
```

### User Interaction Pipeline

```
User Action (rate, click, view)
    │
    ▼
API Endpoint
    │
    ├─> ratings table (explicit feedback)
    │   • Used for collaborative filtering
    │   • Used for popularity ranking
    │
    └─> interactions table (implicit feedback)
        • Used for future ML models
        • Used for analytics
```

---

## Memory Layout (512MB Total)

```
┌─────────────────────────────────────────────┐
│         Koyeb Nano Instance (512MB)         │
├─────────────────────────────────────────────┤
│                                             │
│  Python Runtime              ~50MB          │
│  ├─ Interpreter                             │
│  └─ Standard library                        │
│                                             │
│  FastAPI + Dependencies      ~80MB          │
│  ├─ FastAPI framework                       │
│  ├─ Uvicorn ASGI server                     │
│  ├─ Pydantic validation                     │
│  └─ Other dependencies                      │
│                                             │
│  FastEmbed Model (ONNX)      ~80MB          │
│  ├─ Model weights                           │
│  ├─ ONNX runtime                            │
│  └─ Tokenizer                               │
│                                             │
│  Supabase Client             ~20MB          │
│  └─ PostgreSQL driver                       │
│                                             │
│  Request Processing          ~50MB          │
│  ├─ Active requests                         │
│  ├─ Response buffers                        │
│  └─ Temporary data                          │
│                                             │
│  ─────────────────────────────────────────  │
│  TOTAL USAGE:               ~280MB          │
│                                             │
│  ═════════════════════════════════════════  │
│  AVAILABLE HEADROOM:        ~230MB (45%)    │
│  ─────────────────────────────────────────  │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────┐
│              Security Layers                │
├─────────────────────────────────────────────┤
│                                             │
│  1. Transport Layer                         │
│     • HTTPS (Koyeb provides SSL)            │
│     • TLS 1.2+                              │
│                                             │
│  2. Authentication Layer                    │
│     • JWT tokens (HS256)                    │
│     • 7-day expiration                      │
│     • Bearer token format                   │
│                                             │
│  3. Authorization Layer                     │
│     • User-scoped operations                │
│     • Token validation on protected routes  │
│     • No privilege escalation               │
│                                             │
│  4. Data Layer                              │
│     • Bcrypt password hashing (cost 12)     │
│     • No plaintext passwords                │
│     • Parameterized SQL queries             │
│     • Input validation (Pydantic)           │
│                                             │
│  5. Application Layer                       │
│     • CORS configuration                    │
│     • Rate limiting (future)                │
│     • Error message sanitization            │
│     • No sensitive data in logs             │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Scalability Considerations

### Current Architecture (Single Instance)
- **Capacity:** ~10-20 req/sec
- **Users:** ~1,000 concurrent
- **Bottleneck:** Single worker process

### Horizontal Scaling (Future)

```
                    Load Balancer
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Instance 1       Instance 2       Instance 3
    (512MB)          (512MB)          (512MB)
        │                │                │
        └────────────────┴────────────────┘
                         │
                   Supabase DB
                   (Shared State)
```

### Caching Layer (Future)

```
Client Request
    │
    ▼
Redis Cache
    │
    ├─> Cache Hit ──> Return cached result
    │
    └─> Cache Miss
            │
            ▼
        API Backend
            │
            ▼
        Database
            │
            ▼
        Update Cache
```

---

## Monitoring & Observability

### Metrics to Track

```
┌─────────────────────────────────────────────┐
│              System Metrics                 │
├─────────────────────────────────────────────┤
│  • CPU usage (%)                            │
│  • Memory usage (MB)                        │
│  • Request rate (req/sec)                   │
│  • Response time (ms)                       │
│  • Error rate (%)                           │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│           Application Metrics               │
├─────────────────────────────────────────────┤
│  • Active users                             │
│  • Ratings per day                          │
│  • Search queries per day                   │
│  • Recommendation requests                  │
│  • Cache hit rate (future)                  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│              ML Metrics                     │
├─────────────────────────────────────────────┤
│  • Embedding generation time                │
│  • Search relevance (NDCG)                  │
│  • Recommendation accuracy                  │
│  • Cold start rate                          │
└─────────────────────────────────────────────┘
```

---

This architecture is designed for:
- ✅ Resource efficiency (512MB RAM)
- ✅ Low latency (<500ms)
- ✅ High availability (stateless design)
- ✅ Security (JWT + bcrypt)
- ✅ Scalability (horizontal scaling ready)
