import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check for tables in the public schema
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    tables = cur.fetchall()
    print("Tables found in database:")
    for table in tables:
        print(f"- {table[0]}")
        
    cur.close()
    conn.close()

except Exception as e:
    print(f"Error checking schema: {e}")
