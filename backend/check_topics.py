import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

def check_data():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        print("Checking Subjects:")
        cur.execute("SELECT * FROM subjects;")
        subjects = cur.fetchall()
        for s in subjects:
            print(f" - {s}")

        print("\nChecking Topics:")
        cur.execute("SELECT * FROM topics LIMIT 10;")
        topics = cur.fetchall()
        for t in topics:
            print(f" - {t}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
