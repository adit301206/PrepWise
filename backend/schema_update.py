import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

def update_schema():
    try:
        print("🛠 Checking Database Schema...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Create test_sessions table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_sessions (
                session_id SERIAL PRIMARY KEY,
                user_id UUID, 
                topic_id INTEGER REFERENCES topics(topic_id),
                score INTEGER,
                total_questions INTEGER,
                difficulty_level VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Schema updated: 'test_sessions' table verified.")

    except Exception as e:
        print(f"❌ Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
