import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

def add_column():
    try:
        print("🛠 Altering 'questions' table...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        cur.execute("""
            ALTER TABLE questions 
            ADD COLUMN IF NOT EXISTS explanation TEXT;
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Column 'explanation' added successfully.")

    except Exception as e:
        print(f"❌ Error updating schema: {e}")

if __name__ == "__main__":
    add_column()
