"""
Quick diagnostic script for deployed API
"""
import requests
import json

API_URL = "https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app"

print("="*60)
print("CineLibre API Diagnostics")
print("="*60)

# Test 1: Health
print("\n1. Testing Health Check...")
try:
    r = requests.get(f"{API_URL}/")
    print(f"✅ Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: List Movies (no auth needed)
print("\n2. Testing List Movies...")
try:
    r = requests.get(f"{API_URL}/movies?limit=3")
    print(f"✅ Status: {r.status_code}")
    data = r.json()
    print(f"Found {len(data.get('movies', []))} movies")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Search (should work without auth now)
print("\n3. Testing Semantic Search...")
try:
    r = requests.get(f"{API_URL}/search/semantic?q=action&limit=3")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Found {len(data.get('results', []))} results")
        for movie in data.get('results', [])[:2]:
            print(f"  - {movie.get('title')}")
    else:
        print(f"❌ Error: {r.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Check if users table exists (will fail if not)
print("\n4. Testing User Registration...")
try:
    r = requests.post(f"{API_URL}/auth/register", json={
        "email": "test@example.com",
        "password": "test123",
        "name": "Test"
    })
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("✅ Registration works!")
    elif r.status_code == 400:
        print("⚠️  User already exists (table exists)")
    else:
        print(f"❌ Error: {r.text}")
        print("\n💡 Likely cause: 'users' table doesn't exist in database")
        print("   Solution: Run database_schema.sql in Supabase SQL Editor")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Popular items
print("\n5. Testing Popular Items...")
try:
    r = requests.get(f"{API_URL}/recommendations/popular?limit=5")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        items = data.get('popular_items', [])
        print(f"✅ Found {len(items)} popular items")
    else:
        print(f"❌ Error: {r.text}")
        print("\n💡 Likely cause: RPC function 'get_popular_items' doesn't exist")
        print("   Solution: Run database_schema.sql in Supabase SQL Editor")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)
print("\nIf you see errors about missing tables or functions:")
print("1. Go to Supabase SQL Editor")
print("2. Copy the entire database_schema.sql file")
print("3. Execute it")
print("4. Re-run this diagnostic")
