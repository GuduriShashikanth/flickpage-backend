"""
Interactive API Testing Script for Deployed CineLibre API
"""
import requests
import json
from datetime import datetime

# Configuration
API_URL = input("Enter your deployed API URL (e.g., https://your-app.koyeb.app): ").strip()
if not API_URL:
    API_URL = "http://localhost:8000"

print(f"\n{'='*60}")
print(f"Testing CineLibre API at: {API_URL}")
print(f"{'='*60}\n")

# Store token globally
TOKEN = None

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
    
    try:
        data = response.json()
        print(f"\nResponse Body:")
        print(json.dumps(data, indent=2))
    except:
        print(f"\nResponse Text:")
        print(response.text)
    
    print(f"{'='*60}\n")
    return response

def test_1_health_check():
    """Test 1: Health Check"""
    print("\n🔍 TEST 1: Health Check")
    response = requests.get(f"{API_URL}/")
    print_response("Health Check Result", response)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "online" and data.get("ready"):
            print("✅ API is online and ready!")
            return True
        else:
            print("⚠️  API is online but not fully ready")
            return False
    else:
        print("❌ API health check failed!")
        return False

def test_2_register():
    """Test 2: User Registration"""
    global TOKEN
    print("\n🔍 TEST 2: User Registration")
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"testuser_{timestamp}@example.com"
    
    payload = {
        "email": email,
        "password": "testpass123",
        "name": "Test User"
    }
    
    print(f"Registering user: {email}")
    response = requests.post(f"{API_URL}/auth/register", json=payload)
    print_response("Registration Result", response)
    
    if response.status_code == 200:
        data = response.json()
        TOKEN = data.get("access_token")
        print(f"✅ User registered successfully!")
        print(f"📝 Token saved: {TOKEN[:50]}...")
        return True
    elif response.status_code == 400:
        print("⚠️  User might already exist, trying login...")
        return test_2b_login(email)
    else:
        print("❌ Registration failed!")
        return False

def test_2b_login(email=None):
    """Test 2b: User Login (fallback)"""
    global TOKEN
    print("\n🔍 TEST 2b: User Login")
    
    if not email:
        email = input("Enter email to login: ").strip()
    
    payload = {
        "email": email,
        "password": "testpass123"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=payload)
    print_response("Login Result", response)
    
    if response.status_code == 200:
        data = response.json()
        TOKEN = data.get("access_token")
        print(f"✅ Login successful!")
        print(f"📝 Token saved: {TOKEN[:50]}...")
        return True
    else:
        print("❌ Login failed!")
        return False

def test_3_get_profile():
    """Test 3: Get User Profile"""
    print("\n🔍 TEST 3: Get User Profile")
    
    if not TOKEN:
        print("❌ No token available. Please login first.")
        return False
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{API_URL}/auth/me", headers=headers)
    print_response("Profile Result", response)
    
    if response.status_code == 200:
        print("✅ Profile retrieved successfully!")
        return True
    else:
        print("❌ Failed to get profile!")
        return False

def test_4_semantic_search():
    """Test 4: Semantic Search"""
    print("\n🔍 TEST 4: Semantic Search")
    
    queries = [
        "action thriller",
        "romantic comedy",
        "space adventure"
    ]
    
    query = queries[0]
    print(f"Searching for: '{query}'")
    
    params = {
        "q": query,
        "type": "movie",
        "limit": 5
    }
    
    response = requests.get(f"{API_URL}/search/semantic", params=params)
    print_response("Search Result", response)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        print(f"✅ Found {len(results)} movies!")
        
        if results:
            print("\nTop 3 Results:")
            for i, movie in enumerate(results[:3], 1):
                print(f"{i}. {movie.get('title')} (Similarity: {movie.get('similarity', 0):.2f})")
            return results
        else:
            print("⚠️  No results found. Database might be empty.")
            return []
    else:
        print("❌ Search failed!")
        return []

def test_5_rate_movie(movies):
    """Test 5: Rate a Movie"""
    print("\n🔍 TEST 5: Rate a Movie")
    
    if not TOKEN:
        print("❌ No token available. Please login first.")
        return False
    
    if not movies:
        print("❌ No movies available to rate.")
        return False
    
    movie = movies[0]
    movie_id = movie.get("id")
    movie_title = movie.get("title")
    
    print(f"Rating movie: {movie_title} (ID: {movie_id})")
    
    payload = {
        "item_id": movie_id,
        "item_type": "movie",
        "rating": 4.5
    }
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.post(f"{API_URL}/ratings", json=payload, headers=headers)
    print_response("Rating Result", response)
    
    if response.status_code == 200:
        print("✅ Movie rated successfully!")
        return True
    else:
        print("❌ Rating failed!")
        return False

def test_6_get_my_ratings():
    """Test 6: Get My Ratings"""
    print("\n🔍 TEST 6: Get My Ratings")
    
    if not TOKEN:
        print("❌ No token available. Please login first.")
        return False
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{API_URL}/ratings/my", headers=headers)
    print_response("My Ratings Result", response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} ratings!")
        return True
    else:
        print("❌ Failed to get ratings!")
        return False

def test_7_similar_items(movies):
    """Test 7: Get Similar Items"""
    print("\n🔍 TEST 7: Get Similar Items")
    
    if not movies:
        print("❌ No movies available.")
        return False
    
    movie = movies[0]
    movie_id = movie.get("id")
    movie_title = movie.get("title")
    
    print(f"Finding movies similar to: {movie_title}")
    
    response = requests.get(f"{API_URL}/recommendations/similar/movie/{movie_id}?limit=5")
    print_response("Similar Items Result", response)
    
    if response.status_code == 200:
        data = response.json()
        similar = data.get("similar_items", [])
        print(f"✅ Found {len(similar)} similar movies!")
        
        if similar:
            print("\nTop 3 Similar:")
            for i, item in enumerate(similar[:3], 1):
                print(f"{i}. {item.get('title')} (Similarity: {item.get('similarity', 0):.2f})")
        return True
    else:
        print("❌ Failed to get similar items!")
        return False

def test_8_popular_items():
    """Test 8: Get Popular Items"""
    print("\n🔍 TEST 8: Get Popular Items")
    
    response = requests.get(f"{API_URL}/recommendations/popular?limit=5")
    print_response("Popular Items Result", response)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("popular_items", [])
        print(f"✅ Found {len(items)} popular items!")
        
        if items:
            print("\nTop 3 Popular:")
            for i, item in enumerate(items[:3], 1):
                print(f"{i}. {item.get('title')} (Avg: {item.get('avg_rating', 0):.1f}, Count: {item.get('rating_count', 0)})")
        else:
            print("⚠️  No popular items yet. Need more ratings in the system.")
        return True
    else:
        print("❌ Failed to get popular items!")
        return False

def test_9_personalized_recommendations():
    """Test 9: Get Personalized Recommendations"""
    print("\n🔍 TEST 9: Get Personalized Recommendations")
    
    if not TOKEN:
        print("❌ No token available. Please login first.")
        return False
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{API_URL}/recommendations/personalized?limit=5", headers=headers)
    print_response("Personalized Recommendations Result", response)
    
    if response.status_code == 200:
        data = response.json()
        recs = data.get("recommendations", [])
        method = data.get("method", "unknown")
        
        print(f"✅ Got recommendations using: {method}")
        
        if recs:
            print(f"Found {len(recs)} recommendations!")
            print("\nTop 3 Recommendations:")
            for i, rec in enumerate(recs[:3], 1):
                score = rec.get("predicted_rating") or rec.get("avg_rating", 0)
                print(f"{i}. {rec.get('title')} (Score: {score:.2f})")
        else:
            print("⚠️  No recommendations yet. Need more user data for collaborative filtering.")
        return True
    else:
        print("❌ Failed to get recommendations!")
        return False

def test_10_list_movies():
    """Test 10: List Movies"""
    print("\n🔍 TEST 10: List Movies")
    
    response = requests.get(f"{API_URL}/movies?limit=5")
    print_response("List Movies Result", response)
    
    if response.status_code == 200:
        data = response.json()
        movies = data.get("movies", [])
        print(f"✅ Found {len(movies)} movies!")
        
        if movies:
            print("\nFirst 3 Movies:")
            for i, movie in enumerate(movies[:3], 1):
                print(f"{i}. {movie.get('title')} ({movie.get('release_date', 'N/A')})")
        return True
    else:
        print("❌ Failed to list movies!")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*60)
    print("🚀 CineLibre API Test Suite")
    print("="*60)
    
    results = {}
    movies = []
    
    # Test 1: Health Check
    results["health"] = test_1_health_check()
    if not results["health"]:
        print("\n❌ API is not accessible. Please check the URL and try again.")
        return
    
    input("\nPress Enter to continue with authentication tests...")
    
    # Test 2: Register/Login
    results["auth"] = test_2_register()
    if not results["auth"]:
        print("\n⚠️  Authentication failed. Some tests will be skipped.")
    
    # Test 3: Get Profile
    if results["auth"]:
        input("\nPress Enter to test profile retrieval...")
        results["profile"] = test_3_get_profile()
    
    input("\nPress Enter to test search functionality...")
    
    # Test 4: Search
    movies = test_4_semantic_search()
    results["search"] = len(movies) > 0
    
    # Test 5: Rate Movie
    if results["auth"] and movies:
        input("\nPress Enter to rate a movie...")
        results["rating"] = test_5_rate_movie(movies)
    
    # Test 6: Get My Ratings
    if results["auth"]:
        input("\nPress Enter to get your ratings...")
        results["my_ratings"] = test_6_get_my_ratings()
    
    # Test 7: Similar Items
    if movies:
        input("\nPress Enter to find similar movies...")
        results["similar"] = test_7_similar_items(movies)
    
    input("\nPress Enter to test recommendation endpoints...")
    
    # Test 8: Popular Items
    results["popular"] = test_8_popular_items()
    
    # Test 9: Personalized Recommendations
    if results["auth"]:
        results["personalized"] = test_9_personalized_recommendations()
    
    # Test 10: List Movies
    input("\nPress Enter to list movies...")
    results["list_movies"] = test_10_list_movies()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working perfectly!")
    elif passed >= total * 0.7:
        print("✅ Most tests passed! API is functional.")
    else:
        print("⚠️  Several tests failed. Check the errors above.")

def interactive_mode():
    """Interactive testing mode"""
    print("\n" + "="*60)
    print("🎮 Interactive Mode")
    print("="*60)
    print("\nAvailable tests:")
    print("1. Health Check")
    print("2. Register/Login")
    print("3. Get Profile")
    print("4. Semantic Search")
    print("5. Rate Movie")
    print("6. Get My Ratings")
    print("7. Similar Items")
    print("8. Popular Items")
    print("9. Personalized Recommendations")
    print("10. List Movies")
    print("11. Run All Tests")
    print("0. Exit")
    
    while True:
        choice = input("\nEnter test number (0-11): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            test_1_health_check()
        elif choice == "2":
            test_2_register()
        elif choice == "3":
            test_3_get_profile()
        elif choice == "4":
            movies = test_4_semantic_search()
        elif choice == "5":
            movies = test_4_semantic_search()
            test_5_rate_movie(movies)
        elif choice == "6":
            test_6_get_my_ratings()
        elif choice == "7":
            movies = test_4_semantic_search()
            test_7_similar_items(movies)
        elif choice == "8":
            test_8_popular_items()
        elif choice == "9":
            test_9_personalized_recommendations()
        elif choice == "10":
            test_10_list_movies()
        elif choice == "11":
            run_all_tests()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        mode = input("\nChoose mode:\n1. Run all tests\n2. Interactive mode\n\nEnter choice (1 or 2): ").strip()
        
        if mode == "2":
            interactive_mode()
        else:
            run_all_tests()
            
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
