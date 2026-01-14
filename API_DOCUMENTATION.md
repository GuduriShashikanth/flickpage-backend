# CineLibre API Documentation

**Base URL:** `https://your-app.koyeb.app` (or `http://localhost:8000` for local)  
**Version:** 2.0.0  
**Authentication:** JWT Bearer Token

---

## Table of Contents

1. [Authentication](#authentication)
2. [Ratings](#ratings)
3. [Recommendations](#recommendations)
4. [Search](#search)
5. [Content](#content)
6. [Interactions](#interactions)
7. [System](#system)
8. [Error Codes](#error-codes)

---

## Authentication

### Register User

Create a new user account.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-01-14T12:00:00Z"
  }
}
```

**Errors:**
- `400` - Email already registered
- `422` - Validation error (invalid email, password too short)

---

### Login

Authenticate and receive JWT token.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-01-14T12:00:00Z"
  }
}
```

**Errors:**
- `401` - Invalid credentials

---

### Get Current User

Get authenticated user's profile.

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-01-14T12:00:00Z"
}
```

**Errors:**
- `401` - Invalid or expired token
- `404` - User not found

---

## Ratings

### Create or Update Rating

Rate a movie or book (0.5 to 5.0 stars).

**Endpoint:** `POST /ratings`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "item_id": 123,
  "item_type": "movie",
  "rating": 4.5
}
```

**Parameters:**
- `item_id` (integer, required) - Movie or book ID
- `item_type` (string, required) - Either "movie" or "book"
- `rating` (float, required) - Rating between 0.5 and 5.0

**Response:** `200 OK`
```json
{
  "id": 456,
  "user_id": 1,
  "item_id": 123,
  "item_type": "movie",
  "rating": 4.5,
  "created_at": "2026-01-14T12:00:00Z"
}
```

**Errors:**
- `401` - Not authenticated
- `422` - Invalid rating value

---

### Get My Ratings

Retrieve all ratings by the authenticated user.

**Endpoint:** `GET /ratings/my`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `item_type` (string, optional) - Filter by "movie" or "book"

**Response:** `200 OK`
```json
[
  {
    "id": 456,
    "user_id": 1,
    "item_id": 123,
    "item_type": "movie",
    "rating": 4.5,
    "created_at": "2026-01-14T12:00:00Z"
  },
  {
    "id": 457,
    "user_id": 1,
    "item_id": 124,
    "item_type": "movie",
    "rating": 3.0,
    "created_at": "2026-01-14T11:00:00Z"
  }
]
```

---

### Delete Rating

Remove a rating.

**Endpoint:** `DELETE /ratings/{rating_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "message": "Rating deleted"
}
```

**Errors:**
- `401` - Not authenticated
- `404` - Rating not found or not owned by user

---

## Recommendations

### Personalized Recommendations

Get personalized recommendations using collaborative filtering.

**Endpoint:** `GET /recommendations/personalized`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (integer, optional, default: 20) - Number of recommendations

**Response:** `200 OK`
```json
{
  "recommendations": [
    {
      "item_id": 789,
      "item_type": "movie",
      "title": "Inception",
      "predicted_rating": 4.7,
      "poster_url": "https://image.tmdb.org/t/p/w500/..."
    },
    {
      "item_id": 790,
      "item_type": "movie",
      "title": "Interstellar",
      "predicted_rating": 4.5,
      "poster_url": "https://image.tmdb.org/t/p/w500/..."
    }
  ],
  "method": "collaborative_filtering"
}
```

**Notes:**
- Requires at least 3 ratings from the user
- Falls back to popular items for new users
- Uses Pearson correlation to find similar users

---

### Similar Items

Get items similar to a specific movie or book (content-based).

**Endpoint:** `GET /recommendations/similar/{item_type}/{item_id}`

**Path Parameters:**
- `item_type` (string) - Either "movie" or "book"
- `item_id` (integer) - ID of the item

**Query Parameters:**
- `limit` (integer, optional, default: 12) - Number of similar items

**Response:** `200 OK`
```json
{
  "item_id": 123,
  "similar_items": [
    {
      "id": 456,
      "title": "The Dark Knight",
      "overview": "Batman faces the Joker...",
      "poster_url": "https://image.tmdb.org/t/p/w500/...",
      "similarity": 0.89
    },
    {
      "id": 457,
      "title": "Inception",
      "overview": "A thief who steals secrets...",
      "poster_url": "https://image.tmdb.org/t/p/w500/...",
      "similarity": 0.85
    }
  ],
  "method": "content_based"
}
```

**Errors:**
- `404` - Item not found

---

### Popular Items

Get trending items based on ratings.

**Endpoint:** `GET /recommendations/popular`

**Query Parameters:**
- `limit` (integer, optional, default: 20) - Number of items

**Response:** `200 OK`
```json
{
  "popular_items": [
    {
      "item_id": 123,
      "item_type": "movie",
      "title": "The Shawshank Redemption",
      "avg_rating": 4.8,
      "rating_count": 150,
      "poster_url": "https://image.tmdb.org/t/p/w500/..."
    },
    {
      "item_id": 124,
      "item_type": "movie",
      "title": "The Godfather",
      "avg_rating": 4.7,
      "rating_count": 142,
      "poster_url": "https://image.tmdb.org/t/p/w500/..."
    }
  ],
  "method": "popularity_based"
}
```

**Notes:**
- Only includes items with 5+ ratings
- Sorted by average rating, then rating count

---

## Search

### Semantic Search

Search for movies or books using natural language.

**Endpoint:** `GET /search/semantic`

**Query Parameters:**
- `q` (string, required, min 3 chars) - Search query
- `type` (string, optional, default: "movie") - Either "movie" or "book"
- `limit` (integer, optional, default: 12) - Number of results
- `threshold` (float, optional, default: 0.4) - Similarity threshold (0-1)

**Examples:**
```
/search/semantic?q=space adventure with robots
/search/semantic?q=mystery in a small town&type=book
/search/semantic?q=action thriller&limit=20&threshold=0.5
```

**Response:** `200 OK`
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
      "language": "en",
      "similarity": 0.87
    },
    {
      "id": 124,
      "tmdb_id": 551,
      "title": "The Martian",
      "overview": "An astronaut becomes stranded on Mars...",
      "release_date": "2015-10-02",
      "poster_url": "https://image.tmdb.org/t/p/w500/...",
      "language": "en",
      "similarity": 0.82
    }
  ]
}
```

**Notes:**
- Uses semantic understanding, not keyword matching
- Query: "gritty crime thriller" matches movies with dark, noir themes
- Supports natural language: "movies like Inception"

---

## Content

### Get Movie

Retrieve movie details by ID.

**Endpoint:** `GET /movies/{movie_id}`

**Response:** `200 OK`
```json
{
  "id": 123,
  "tmdb_id": 550,
  "title": "Fight Club",
  "overview": "An insomniac office worker...",
  "release_date": "1999-10-15",
  "poster_url": "https://image.tmdb.org/t/p/w500/...",
  "language": "en",
  "created_at": "2026-01-14T12:00:00Z"
}
```

**Errors:**
- `404` - Movie not found

---

### List Movies

Get paginated list of movies.

**Endpoint:** `GET /movies`

**Query Parameters:**
- `skip` (integer, optional, default: 0) - Number of items to skip
- `limit` (integer, optional, default: 20) - Number of items to return

**Response:** `200 OK`
```json
{
  "movies": [
    {
      "id": 123,
      "tmdb_id": 550,
      "title": "Fight Club",
      "overview": "An insomniac office worker...",
      "release_date": "1999-10-15",
      "poster_url": "https://image.tmdb.org/t/p/w500/...",
      "language": "en"
    }
  ],
  "skip": 0,
  "limit": 20
}
```

---

### Get Book

Retrieve book details by ID.

**Endpoint:** `GET /books/{book_id}`

**Response:** `200 OK`
```json
{
  "id": 456,
  "google_id": "abc123",
  "title": "The Great Gatsby",
  "description": "The story of the mysteriously wealthy Jay Gatsby...",
  "thumbnail_url": "https://books.google.com/...",
  "created_at": "2026-01-14T12:00:00Z"
}
```

**Errors:**
- `404` - Book not found

---

## Interactions

### Track Interaction

Track user behavior (views, clicks, searches).

**Endpoint:** `POST /interactions`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "item_id": 123,
  "item_type": "movie",
  "interaction_type": "view"
}
```

**Parameters:**
- `item_id` (integer, required) - Movie or book ID
- `item_type` (string, required) - Either "movie" or "book"
- `interaction_type` (string, required) - One of: "view", "click", "search"

**Response:** `200 OK`
```json
{
  "message": "Interaction tracked"
}
```

**Notes:**
- Used for analytics and future ML models
- Does not affect current recommendations

---

## System

### Health Check

Check API status and readiness.

**Endpoint:** `GET /`

**Response:** `200 OK`
```json
{
  "status": "online",
  "engine": "FastEmbed",
  "ready": true,
  "database": "connected",
  "version": "2.0.0"
}
```

---

### API Documentation

Interactive API documentation (Swagger UI).

**Endpoint:** `GET /docs`

Opens interactive API explorer in browser.

---

### OpenAPI Schema

Get OpenAPI 3.0 schema.

**Endpoint:** `GET /openapi.json`

Returns JSON schema for API.

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

**Authentication Errors:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**Validation Errors:**
```json
{
  "detail": [
    {
      "loc": ["body", "rating"],
      "msg": "ensure this value is less than or equal to 5.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. Future versions will implement:
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## Best Practices

### Authentication
- Store JWT token securely (httpOnly cookies or secure localStorage)
- Include token in Authorization header: `Bearer <token>`
- Tokens expire after 7 days - implement refresh logic

### Search
- Debounce search queries (wait 300ms after user stops typing)
- Cache search results client-side
- Use threshold parameter to filter low-quality matches

### Recommendations
- Cache personalized recommendations for 1 hour
- Refresh after user adds new ratings
- Show loading state while fetching

### Error Handling
- Always check response status code
- Display user-friendly error messages
- Implement retry logic for 500 errors

---

## Code Examples

### JavaScript (Fetch API)

```javascript
// Register
const register = async (email, password, name) => {
  const response = await fetch('https://api.cinelibre.com/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name })
  });
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  return data.user;
};

// Search
const search = async (query) => {
  const response = await fetch(
    `https://api.cinelibre.com/search/semantic?q=${encodeURIComponent(query)}&limit=12`
  );
  return await response.json();
};

// Rate movie
const rateMovie = async (movieId, rating) => {
  const token = localStorage.getItem('token');
  const response = await fetch('https://api.cinelibre.com/ratings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      item_id: movieId,
      item_type: 'movie',
      rating
    })
  });
  return await response.json();
};

// Get recommendations
const getRecommendations = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch(
    'https://api.cinelibre.com/recommendations/personalized?limit=20',
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return await response.json();
};
```

### Python (Requests)

```python
import requests

BASE_URL = "https://api.cinelibre.com"

# Register
def register(email, password, name):
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "name": name
    })
    data = response.json()
    return data["access_token"], data["user"]

# Search
def search(query, limit=12):
    response = requests.get(f"{BASE_URL}/search/semantic", params={
        "q": query,
        "limit": limit
    })
    return response.json()

# Rate movie
def rate_movie(token, movie_id, rating):
    response = requests.post(f"{BASE_URL}/ratings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "item_id": movie_id,
            "item_type": "movie",
            "rating": rating
        }
    )
    return response.json()

# Get recommendations
def get_recommendations(token, limit=20):
    response = requests.get(
        f"{BASE_URL}/recommendations/personalized",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": limit}
    )
    return response.json()
```

---

## Changelog

### v2.0.0 (2026-01-14)
- Added user authentication (JWT)
- Added rating system
- Added collaborative filtering
- Added interaction tracking
- Added personalized recommendations
- Optimized for 512MB RAM

### v1.0.0 (2025-11-01)
- Initial release
- Semantic search
- Content-based recommendations
- Movie and book data

---

**API Version:** 2.0.0  
**Last Updated:** January 14, 2026  
**Support:** GitHub Issues
