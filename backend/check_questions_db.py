import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load env vars
load_dotenv()

DB_URL = os.environ.get("DATABASE_URL")
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

def check_db():
    if not DB_URL:
        print("❌ DATABASE_URL not set.")
        return

    try:
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        cur = conn.cursor()

        print("🔍 Checking 'questions' table for non-standard 'correct_option' values...")
        
        # Query 1: Find rows where correct_option is NOT a single letter A-D
        # Using length check > 1 or not in set
        cur.execute("""
            SELECT question_id, difficulty, correct_option, substring(question_text from 1 for 30) as q_snippet
            FROM questions
            WHERE length(correct_option) > 1 
               OR correct_option NOT IN ('A', 'B', 'C', 'D', 'a', 'b', 'c', 'd');
        """)
        
        issues = cur.fetchall()
        
        if not issues:
            print("✅ All correct_option values are standard single letters (A, B, C, D).")
        else:
            print(f"⚠️ Found {len(issues)} questions with non-standard correct_option values:")
            print("-" * 60)
            print(f"{'ID':<5} | {'Diff':<8} | {'Correct Option (Raw)':<25} | {'Question Snippet'}")
            print("-" * 60)
            for row in issues:
                print(f"{row['question_id']:<5} | {row['difficulty']:<8} | {row['correct_option']:<25} | {row['q_snippet']}...")
            print("-" * 60)
            print("These values might be causing the quiz validation bug if JS expects 'A', 'B' etc.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error connecting or querying DB: {e}")

if __name__ == "__main__":
    check_db()
