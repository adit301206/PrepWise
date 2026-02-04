import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users';")
    columns = [row[0] for row in cur.fetchall()]
    print(f"Columns in public.users: {columns}")
    conn.close()
except Exception as e:
    print(e)
