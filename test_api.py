"""
Test script for CineLibre API
Run after starting the server: python api/main.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_register():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    data = {
        "email": "testuser@example.com",
        "password": "testpass123",
        "name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"User created: {result['user']['name']}")
        print(f"Token: {result['access_token'][:50]}...")
        return result['access_token']
    else:
        print(f"Error: {response.json()}")
        return None

def test_login():
    """Test user login"""
    print("\n=== Testing User Login ===")
    data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Login successful: {result['user']['name']}")
        return result['access_token']
    else:
        print(f"Error: {response.json()}")
        return None

def test_search(query="action thriller"):
    """Test semantic search"""
    print(f"\n=== Testing Semantic Search: '{query}' ===")
    response = requests.get(
        f"{BASE_URL}/search/semantic",
        params={"q": query, "type": "movie", "limit": 5}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {len(result['results'])} movies:")
        for movie in result['results'][:3]:
            print(f"  - {movie['title']} (Similarity: {movie.get('similarity', 0):.2f})")
        return result['results']
    else:
        print(f"Error: {response.json()}")
        return []

def test_rate_movie(token, movie_id, rating):
    """Test rating a movie"""
    print(f"\n=== Testing Rating Movie {movie_id} with {rating} stars ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "item_id": movie_id,
        "item_type": "movie",
        "rating": rating
    }
    response = requests.post(f"{BASE_URL}/ratings", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Rating saved successfully")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_get_my_ratings(token):
    """Test getting user's ratings"""
    print("\n=== Testing Get My Ratings ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/ratings/my", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        ratings = response.json()
        print(f"Found {len(ratings)} ratings")
        for rating in ratings[:3]:
            print(f"  - Item {rating['item_id']}: {rating['rating']} stars")
        return ratings
    else:
        print(f"Error: {response.json()}")
        return []

def test_popular_items():
    """Test getting popular items"""
    print("\n=== Testing Popular Items ===")
    response = requests.get(f"{BASE_URL}/recommendations/popular", params={"limit": 5})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        items = result.get('popular_items', [])
        print(f"Found {len(items)} popular items:")
        for item in items[:3]:
            print(f"  - {item['title']} (Avg: {item.get('avg_rating', 0):.1f}, Count: {item.get('rating_count', 0)})")
        return items
    else:
        print(f"Error: {response.json()}")
        return []

def test_personalized_recommendations(token):
    """Test personalized recommendations"""
    print("\n=== Testing Personalized Recommendations ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/recommendations/personalized",
        params={"limit": 5},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        recs = result.get('recommendations', [])
        print(f"Method: {result.get('method')}")
        print(f"Found {len(recs)} recommendations:")
        for rec in recs[:3]:
            print(f"  - {rec.get('title')} (Score: {rec.get('predicted_rating', 0):.2f})")
        return recs
    else:
        print(f"Error: {response.json()}")
        return []

def test_similar_items(item_id):
    """Test similar items"""
    print(f"\n=== Testing Similar Items to Movie {item_id} ===")
    response = requests.get(
        f"{BASE_URL}/recommendations/similar/movie/{item_id}",
        params={"limit": 5}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        similar = result.get('similar_items', [])
        print(f"Found {len(similar)} similar items:")
        for item in similar[:3]:
            print(f"  - {item['title']} (Similarity: {item.get('similarity', 0):.2f})")
        return similar
    else:
        print(f"Error: {response.json()}")
        return []

def run_all_tests():
    """Run all tests in sequence"""
    print("=" * 60)
    print("CineLibre API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Is the server running?")
        return
    
    # Test 2: Register (or skip if user exists)
    token = test_register()
    if not token:
        print("\nUser might already exist, trying login...")
        token = test_login()
    
    if not token:
        print("\n❌ Authentication failed")
        return
    
    # Test 3: Search
    movies = test_search("space adventure")
    
    if movies:
        # Test 4: Rate some movies
        test_rate_movie(token, movies[0]['id'], 4.5)
        if len(movies) > 1:
            test_rate_movie(token, movies[1]['id'], 3.5)
        
        # Test 5: Get my ratings
        test_get_my_ratings(token)
        
        # Test 6: Similar items
        test_similar_items(movies[0]['id'])
    
    # Test 7: Popular items
    test_popular_items()
    
    # Test 8: Personalized recommendations
    test_personalized_recommendations(token)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
