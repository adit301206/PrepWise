import os
import psycopg2
from dotenv import load_dotenv

# 1. Force load the .env file
load_dotenv()

# 2. Get the URL
url = os.environ.get("DATABASE_URL")

print("\n--- DEBUGGING DATABASE CONNECTION ---")

if not url:
    print("❌ ERROR: Could not find DATABASE_URL in .env file.")
    print("   Make sure the file is named '.env' (not .env.txt)")
else:
    print("✅ Found DATABASE_URL.")
    # Print the first few characters to verify it's the right one (hiding password)
    print(f"   URL starts with: {url[:15]}...") 

    try:
        print("   Attempting to connect...")
        conn = psycopg2.connect(url)
        print("✅ SUCCESS! Connected to Supabase.")
        conn.close()
    except Exception as e:
        print("\n❌ CONNECTION FAILED. Here is the exact error:")
        print("------------------------------------------------")
        print(e)
        print("------------------------------------------------")