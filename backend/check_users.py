
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    print("No DATABASE_URL")
    exit(1)

try:
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    # Check if our test user exists
    # Note: accessing auth.users requires permissions. The 'postgres' user should have them.
    cur.execute("SELECT * FROM auth.users WHERE email LIKE 'test_debug_%';")
    users = cur.fetchall()
    
    print(f"Found {len(users)} test users.")
    for u in users:
        print(f"User: {u['email']}, Confirmed: {u['email_confirmed_at']}")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
