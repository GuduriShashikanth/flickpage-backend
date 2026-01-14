"""
Quick setup script for CineLibre backend
"""
import os
import sys
import secrets

def generate_jwt_secret():
    """Generate a secure JWT secret"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create .env file with prompts"""
    print("=" * 60)
    print("CineLibre Backend Setup")
    print("=" * 60)
    
    env_path = "api/.env"
    
    if os.path.exists(env_path):
        response = input(f"\n{env_path} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("\nPlease provide the following information:")
    print("(Press Enter to use default values where applicable)\n")
    
    # Supabase
    supabase_url = input("Supabase URL: ").strip()
    if not supabase_url:
        print("❌ Supabase URL is required!")
        sys.exit(1)
    
    supabase_key = input("Supabase Service Role Key: ").strip()
    if not supabase_key:
        print("❌ Supabase Key is required!")
        sys.exit(1)
    
    # TMDB
    tmdb_key = input("TMDB API Key (optional for now): ").strip()
    
    # JWT
    print(f"\nGenerating secure JWT secret...")
    jwt_secret = generate_jwt_secret()
    print(f"Generated: {jwt_secret[:20]}...")
    
    # Port
    port = input("Port (default: 8000): ").strip() or "8000"
    
    # Write .env file
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# TMDB API (required for sync engine)
TMDB_API_KEY={tmdb_key}

# JWT Secret
JWT_SECRET_KEY={jwt_secret}

# Server Configuration
PORT={port}
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Created {env_path}")
    print("\nNext steps:")
    print("1. Run the database schema: Copy database_schema.sql to Supabase SQL Editor")
    print("2. Sync initial data: python api/sync_engine.py")
    print("3. Start the server: python api/main.py")
    print("4. Test the API: python test_api.py")

if __name__ == "__main__":
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)
