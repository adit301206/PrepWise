import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print(f"Connecting to: {DATABASE_URL}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connection successful!")
    
    # Create a cursor object
    cur = conn.cursor()
    
    # Execute a query
    cur.execute("SELECT version();")
    
    # Retrieve query results
    db_version = cur.fetchone()
    print(f"PostgreSQL database version: {db_version}")
    
    # Close communication with the database
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Connection failed: {e}")
