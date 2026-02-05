import os
from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"URL: {url}")
print(f"KEY: {key}")

if not url or not key:
    print("Error: Missing URL or KEY")
    exit(1)

try:
    supabase: Client = create_client(url, key)
    print("Supabase client initialized successfully")
    
    # Try a simple unauthenticated request if possible, or just checking init
    # Note: create_client might verify the key format immediately
    
except Exception as e:
    print(f"Supabase Init Error: {e}")
