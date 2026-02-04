
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# This email was used in the previous run (from logs)
# But since I don't know the exact email (it was random), I'll try to find it via check_users or just creating a NEW one manually via SQL script and then logging in.

# Let's create a specific known user via SQL first to be sure.
# Actually, let's just try to login with the one from the valid test run if I knew the email.
# The log didn't show the email, but it showed the ID.

# Let's use check_users.py to find the latest user.
import psycopg2
from psycopg2.extras import RealDictCursor
conn = psycopg2.connect(os.environ.get("DATABASE_URL"), cursor_factory=RealDictCursor)
cur = conn.cursor()
cur.execute("SELECT email, encrypted_password FROM auth.users ORDER BY created_at DESC LIMIT 1;")
user = cur.fetchone()
cur.close()
conn.close()

if user:
    print(f"Testing login for: {user['email']}")
    try:
        # We know the password is "testpassword123" from the test script
        response = supabase.auth.sign_in_with_password({
            "email": user['email'],
            "password": "testpassword123"
        })
        print("Login Successful!")
        print(f"Session Token: {response.session.access_token[:20]}...")
    except Exception as e:
        print(f"Login Failed: {e}")
else:
    print("No user found in DB")
