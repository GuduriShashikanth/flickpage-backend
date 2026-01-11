import os
import requests
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

# 1. Load Configuration from Environment Variables
# These should be added to your GitHub Repository Secrets
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 2. Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Load ML Model
# 'all-MiniLM-L6-v2' is a state-of-the-art model that is small enough 
# to run in GitHub's free environment while producing high-quality vectors.
print("Loading ML Embedding Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_indian_movies():
    """Fetch recent Indian movies from TMDB API"""
    print("Fetching Indian movies from TMDB...")
    # Parameters: Region IN (India), Original Language hi/te/ta (Hindi/Telugu/Tamil)
    # We fetch the latest releases to keep the database fresh.
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&region=IN&with_origin_country=IN&sort_by=release_date.desc&include_adult=false"
    response = requests.get(url).json()
    return response.get('results', [])

def get_global_books(query="popular fiction"):
    """Fetch global books from Google Books API"""
    print(f"Fetching books for: {query}...")
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&orderBy=newest&maxResults=20"
    response = requests.get(url).json()
    return response.get('items', [])

def run_sync():
    # --- Process Movies ---
    movies = get_indian_movies()
    for m in movies:
        # Create a text string for the ML model to "understand" the movie
        text_content = f"{m['title']}. {m.get('overview', '')}"
        # Generate 384-dimensional embedding
        embedding = model.encode(text_content).tolist()
        
        movie_payload = {
            "tmdb_id": m['id'],
            "title": m['title'],
            "overview": m['overview'],
            "release_date": m.get('release_date'),
            "poster_url": f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get('poster_path') else None,
            "language": m.get('original_language'),
            "origin_country": [m.get('origin_country')] if isinstance(m.get('origin_country'), str) else m.get('origin_country'),
            "embedding": embedding
        }
        
        # 'upsert' prevents duplicates by updating existing records based on tmdb_id
        supabase.table("movies").upsert(movie_payload, on_conflict="tmdb_id").execute()
    
    print(f"Synced {len(movies)} Indian movies.")

    # --- Process Books ---
    book_items = get_global_books()
    for b in book_items:
        vol = b.get('volumeInfo', {})
        description = vol.get('description', '')
        text_content = f"{vol.get('title')}. {description}"
        embedding = model.encode(text_content).tolist()
        
        book_payload = {
            "google_id": b['id'],
            "title": vol.get('title'),
            "authors": vol.get('authors', []),
            "description": description,
            "thumbnail_url": vol.get('imageLinks', {}).get('thumbnail'),
            "categories": vol.get('categories', []),
            "embedding": embedding
        }
        
        supabase.table("books").upsert(book_payload, on_conflict="google_id").execute()
    
    print(f"Synced {len(book_items)} global books.")

if __name__ == "__main__":
    if not all([TMDB_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        print("CRITICAL ERROR: API Keys or Supabase URL missing in environment.")
    else:
        run_sync()