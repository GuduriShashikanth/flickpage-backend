import os
import requests
import time
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Configuration
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") 
HF_TOKEN = os.getenv("HF_TOKEN", "") 

# Initialize Supabase with a safety check to prevent startup crash if envs are missing
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized.")
    except Exception as e:
        print(f"Supabase Initialization Error: {e}")
else:
    print("CRITICAL: SUPABASE_URL or SUPABASE_KEY is missing from environment variables.")

# 2. Initialize FastAPI
app = FastAPI(title="CineLibre ML API - Production Ready")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_embedding(text: str):
    """
    Calls Hugging Face Inference API for embeddings.
    This saves ~500MB of RAM compared to loading a local model.
    """
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    
    # Retry logic for the HF API (it sleeps when not in use)
    for i in range(3):
        try:
            response = requests.post(api_url, headers=headers, json={"inputs": text}, timeout=15)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 503: # Model is currently loading
                print("Hugging Face model is warming up, retrying in 5s...")
                time.sleep(5)
                continue
            else:
                print(f"HF API Error: {response.status_code} - {response.text}")
                break
        except Exception as e:
            print(f"Embedding Request Error: {e}")
            time.sleep(1)
    return None

@app.get("/")
async def health_check():
    """Health status endpoint for Koyeb monitoring"""
    return {
        "status": "online", 
        "database": "connected" if supabase else "error",
        "environment": "production"
    }

@app.get("/search/semantic")
async def semantic_search(
    q: str = Query(..., min_length=3), 
    type: str = "movie", 
    limit: int = 12,
    threshold: float = 0.4 
):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase connection not established.")
    
    try:
        # Step 1: Get semantic vector
        query_vector = get_embedding(q)
        if not query_vector:
            raise HTTPException(status_code=503, detail="AI Engine is busy. Please try again.")

        # Step 2: Query Supabase
        rpc_function = "match_movies" if type == "movie" else "match_books"
        response = supabase.rpc(rpc_function, {
            "query_embedding": query_vector,
            "match_threshold": threshold,
            "match_count": limit
        }).execute()
        
        return {"query": q, "type": type, "results": response.data}
    except Exception as e:
        print(f"Search Error: {e}")
        raise HTTPException(status_code=500, detail="Internal search error.")

@app.get("/recommendations/content/{item_id}")
async def get_content_recommendations(item_id: str, type: str = "movie", limit: int = 10):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not connected.")
    try:
        table = "movies" if type == "movie" else "books"
        rpc_function = "match_movies" if type == "movie" else "match_books"
        
        item = supabase.table(table).select("embedding").eq("id", item_id).single().execute()
        if not item.data:
            raise HTTPException(status_code=404, detail="Item not found.")
            
        response = supabase.rpc(rpc_function, {
            "query_embedding": item.data['embedding'],
            "match_threshold": 0.5,
            "match_count": limit + 1
        }).execute()
        
        results = [r for r in response.data if str(r['id']) != item_id]
        return {"source_id": item_id, "recommendations": results[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    # Crucial: Using the import string "api.main:app" instead of the app object
    # This resolves the "WARNING: You must pass the application as an import string" error
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, log_level="info")