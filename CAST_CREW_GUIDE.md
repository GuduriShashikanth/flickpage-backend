# Cast & Crew Implementation Guide

## Overview
Added cast, crew, director, and genres information to movies.

## Database Changes

### New Columns in `movies` table:
- `cast` (JSONB) - Array of top 10 actors with character names
- `crew` (JSONB) - Array of key crew members (directors, writers, producers)
- `director` (TEXT) - Primary director name (for easy filtering)
- `genres` (TEXT[]) - Array of genre names

### Migration

Run `add_cast_crew.sql` in Supabase SQL Editor:

```sql
ALTER TABLE movies 
ADD COLUMN IF NOT EXISTS cast JSONB,
ADD COLUMN IF NOT EXISTS crew JSONB,
ADD COLUMN IF NOT EXISTS director TEXT,
ADD COLUMN IF NOT EXISTS genres TEXT[];
```

## Data Structure

### Cast Format
```json
[
  {
    "name": "Actor Name",
    "character": "Character Name",
    "profile_path": "/path/to/image.jpg"
  }
]
```

### Crew Format
```json
[
  {
    "name": "Person Name",
    "job": "Director",
    "department": "Directing"
  }
]
```

### Example Movie Record
```json
{
  "id": "uuid",
  "tmdb_id": 123456,
  "title": "Movie Title",
  "overview": "Description...",
  "release_date": "2024-01-01",
  "poster_url": "https://...",
  "language": "en",
  "director": "Director Name",
  "genres": ["Action", "Thriller"],
  "cast": [
    {
      "name": "Lead Actor",
      "character": "Main Character",
      "profile_path": "/abc123.jpg"
    }
  ],
  "crew": [
    {
      "name": "Director Name",
      "job": "Director",
      "department": "Directing"
    },
    {
      "name": "Writer Name",
      "job": "Screenplay",
      "department": "Writing"
    }
  ]
}
```

## Sync Engine Updates

The sync engine now:
1. Fetches basic movie info from discover endpoint
2. For each movie, makes additional API call to get credits
3. Extracts top 10 cast members
4. Extracts key crew (directors, writers, producers)
5. Stores everything in database

### Rate Limiting
- Added 0.3s delay between movie syncs
- Handles TMDB rate limits (429 errors)
- Total sync time will increase due to additional API calls

## API Endpoints

### Get Movie with Cast/Crew
```
GET /movies/{movie_id}
```

Response includes all fields:
```json
{
  "id": "uuid",
  "title": "Movie Title",
  "director": "Director Name",
  "genres": ["Action", "Thriller"],
  "cast": [...],
  "crew": [...]
}
```

### List Movies
```
GET /movies?limit=20
```

Returns all movies with cast/crew data.

### Search Movies
```
GET /search/semantic?q=action&item_type=movie
```

Search results include cast/crew information.

## Frontend Usage

### Display Cast
```javascript
// Get movie details
const movie = await fetch(`/movies/${movieId}`);

// Display cast
movie.cast.forEach(actor => {
  console.log(`${actor.name} as ${actor.character}`);
  // Profile image: https://image.tmdb.org/t/p/w185${actor.profile_path}
});
```

### Display Director
```javascript
console.log(`Directed by: ${movie.director}`);
```

### Display Genres
```javascript
console.log(`Genres: ${movie.genres.join(', ')}`);
```

### Filter by Director
```sql
-- In Supabase
SELECT * FROM movies WHERE director = 'Christopher Nolan';
```

### Filter by Genre
```sql
-- In Supabase
SELECT * FROM movies WHERE 'Action' = ANY(genres);
```

## Querying Cast/Crew

### Find movies by actor
```sql
SELECT * FROM movies 
WHERE cast @> '[{"name": "Actor Name"}]'::jsonb;
```

### Find movies by director
```sql
SELECT * FROM movies 
WHERE director = 'Director Name';
```

### Find movies by genre
```sql
SELECT * FROM movies 
WHERE 'Action' = ANY(genres);
```

### Find movies with specific crew member
```sql
SELECT * FROM movies 
WHERE crew @> '[{"name": "Person Name"}]'::jsonb;
```

## Performance Considerations

### Sync Time
- **Before**: ~30-60 minutes for 10,000 movies
- **After**: ~60-90 minutes (due to additional API calls)

### Storage
- Cast/Crew data adds ~2-5KB per movie
- 10,000 movies = ~20-50MB additional storage

### API Rate Limits
- TMDB allows 40 requests per 10 seconds
- Sync engine respects this with delays
- If rate limited, automatically waits and retries

## Running the Sync

### Full Sync (with cast/crew)
```bash
# Via GitHub Actions
# Go to Actions → Daily Content Sync → Run workflow

# Or locally
python api/sync_engine.py
```

### Update Existing Movies
To add cast/crew to existing movies without cast data:

```python
# update_cast_crew.py
from api.sync_engine import get_movie_details, supabase
from api.database import get_db
import time

db = get_db()

# Get movies without cast data
movies = db.table("movies").select("id, tmdb_id").is_("cast", "null").limit(100).execute()

for movie in movies.data:
    details = get_movie_details(movie['tmdb_id'])
    if details:
        db.table("movies").update({
            'cast': details.get('cast'),
            'crew': details.get('crew'),
            'director': details.get('director'),
            'genres': details.get('genres')
        }).eq('id', movie['id']).execute()
        print(f"Updated {movie['id']}")
    time.sleep(0.3)
```

## Troubleshooting

### Cast/Crew Not Showing
1. Check if migration ran: `SELECT cast FROM movies LIMIT 1;`
2. Check if sync completed: Look for cast data in database
3. Re-run sync for specific movies

### Slow Sync
- Normal due to additional API calls
- Can reduce by syncing fewer movies
- Or sync in batches

### Missing Cast/Crew
- Some movies don't have cast/crew data in TMDB
- This is normal, fields will be null

## Next Steps

1. Run `add_cast_crew.sql` migration
2. Commit and push changes
3. Trigger sync workflow
4. Wait for sync to complete
5. Verify cast/crew data in database
6. Update frontend to display cast/crew

## Example Frontend Component

```jsx
function MovieDetails({ movieId }) {
  const [movie, setMovie] = useState(null);
  
  useEffect(() => {
    fetch(`/movies/${movieId}`)
      .then(res => res.json())
      .then(setMovie);
  }, [movieId]);
  
  if (!movie) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>{movie.title}</h1>
      <p>Directed by: {movie.director}</p>
      <p>Genres: {movie.genres?.join(', ')}</p>
      
      <h2>Cast</h2>
      <div className="cast-grid">
        {movie.cast?.map((actor, i) => (
          <div key={i}>
            {actor.profile_path && (
              <img 
                src={`https://image.tmdb.org/t/p/w185${actor.profile_path}`}
                alt={actor.name}
              />
            )}
            <p>{actor.name}</p>
            <p className="character">{actor.character}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Summary

✅ Added cast, crew, director, genres columns
✅ Updated sync engine to fetch from TMDB
✅ Created migration script
✅ Added rate limiting
✅ Documented querying and usage

Run the migration and sync to populate the data!
