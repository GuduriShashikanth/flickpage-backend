import os
import requests
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

# 1. Load Configuration from Environment Variables
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 2. Initialize Clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Loading ML Embedding Model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_indian_movies(pages=20):
    """Fetch many pages of Indian movies, including various regional languages"""
    print(f"Fetching {pages} pages of Indian movies from TMDB...")
    all_movies = []
    
    # We use multiple languages to ensure we get a diverse set of regional content
    languages = ['hi', 'te', 'ta', 'kn', 'ml', 'pa']
    
    for lang in languages:
        for page in range(1, (pages // len(languages)) + 2):
            try:
                url = (
                    f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}"
                    f"&region=IN&with_origin_country=IN&with_original_language={lang}"
                    f"&sort_by=popularity.desc&include_adult=false&page={page}"
                )
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                all_movies.extend(data.get('results', []))
            except Exception as e:
                print(f"Error fetching {lang} movies page {page}: {e}")
                continue
    
    return all_movies

def get_global_books():
    """Fetch books from 12 diverse categories to maximize row count"""
    queries = [
        "fiction", "mystery", "history", "science", "biography", "thriller",
        "philosophy", "technology", "romance", "fantasy", "business", "travel"
    ]
    all_books = []
    
    for query in queries:
        try:
            print(f"Fetching books for category: {query}...")
            # Google Books max is 40 per request
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&orderBy=newest&maxResults=40"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            all_books.extend(items)
        except Exception as e:
            print(f"Error fetching books for {query}: {e}")
            continue
    
    return all_books

def run_sync():
    # --- Process Movies ---
    # We are now aiming for ~300-400 movies
    movies = get_indian_movies(pages=25) 
    synced_movies = 0
    print(f"Total movie candidates fetched: {len(movies)}. Starting processing...")
    
    for m in movies:
        try:
            if not m.get('overview') or not m.get('title'):
                continue
                
            text_content = f"{m['title']}. {m.get('overview', '')}"
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
            supabase.table("movies").upsert(movie_payload, on_conflict="tmdb_id").execute()
            synced_movies += 1
            if synced_movies % 20 == 0:
                print(f"Progress: {synced_movies} movies synced...")
        except Exception as e:
            pass # Silent skip for malformed data

    print(f"Successfully finished movie sync. Total: {synced_movies}")

    # --- Process Books ---
    # Aiming for ~400+ books
    book_items = get_global_books()
    synced_books = 0
    print(f"Total book candidates fetched: {len(book_items)}. Starting processing...")
    
    for b in book_items:
        try:
            vol = b.get('volumeInfo', {})
            description = vol.get('description', '')
            if not description or not vol.get('title'):
                continue

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
            synced_books += 1
            if synced_books % 20 == 0:
                print(f"Progress: {synced_books} books synced...")
        except Exception as e:
            pass

    print(f"Successfully finished book sync. Total: {synced_books}")
    print("Full database update completed.")

if __name__ == "__main__":
    if not all([TMDB_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        print("CRITICAL ERROR: Environment variables missing.")
    else:
        run_sync()
