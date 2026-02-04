import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

def initialize_database():
    try:
        print("🚀 Connecting to Supabase...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        print("🔥 DROPPING Existing Tables (Clean Slate)...")
        tables = [
            "difficulty_history", "topic_performance", "responses", "attempts", 
            "test_questions", "tests", "questions", "topics", "subjects", "users"
        ]
        for table in tables:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"   🗑️ Dropped table '{table}'")

        print("🏗️ Building New UUID-Based Schema...")

        # --- 1. USERS (Base Entity) ---
        # Changed user_id to UUID to match Supabase Auth
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                role VARCHAR(20) DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ [1/10] Table 'users' created (UUID support).")

        # --- 2. SUBJECTS ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id SERIAL PRIMARY KEY,
                subject_name VARCHAR(50) UNIQUE NOT NULL
            );
        """)
        print("   ✅ [2/10] Table 'subjects' created.")

        # --- 3. TOPICS ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                topic_id SERIAL PRIMARY KEY,
                topic_name VARCHAR(100) NOT NULL,
                subject_id INT REFERENCES subjects(subject_id) ON DELETE CASCADE,
                UNIQUE (topic_name, subject_id)
            );
        """)
        print("   ✅ [3/10] Table 'topics' created.")

        # --- 4. QUESTIONS ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                question_id SERIAL PRIMARY KEY,
                topic_id INT REFERENCES topics(topic_id) ON DELETE CASCADE,
                difficulty VARCHAR(10) CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
                question_text TEXT NOT NULL,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                correct_option CHAR(1),
                explanation TEXT,
                UNIQUE (topic_id, question_text)
            );
        """)
        print("   ✅ [4/10] Table 'questions' created.")

        # --- 5. TESTS (The "Paper" Template) ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                test_id SERIAL PRIMARY KEY,
                selected_difficulty VARCHAR(10),
                total_questions INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ [5/10] Table 'tests' created.")

        # --- 6. TEST_QUESTIONS (Linking Questions to a Test) ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_questions (
                test_question_id SERIAL PRIMARY KEY,
                test_id INT REFERENCES tests(test_id) ON DELETE CASCADE,
                question_id INT REFERENCES questions(question_id)
            );
        """)
        print("   ✅ [6/10] Table 'test_questions' created.")

        # --- 7. ATTEMPTS (Who took which test) ---
        # user_id is now UUID
        cur.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                attempt_id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                topic_id INT REFERENCES topics(topic_id),
                score INT,
                total_questions INT,
                percentage INT,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ [7/10] Table 'attempts' created.")

        # --- 8. RESPONSES (Detailed Answers) ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                response_id SERIAL PRIMARY KEY,
                attempt_id INT REFERENCES attempts(attempt_id) ON DELETE CASCADE,
                question_id INT REFERENCES questions(question_id),
                selected_option CHAR(1),
                is_correct BOOLEAN
            );
        """)
        print("   ✅ [8/10] Table 'responses' created.")

        # --- 9. TOPIC_PERFORMANCE (Analytics) ---
        # user_id is now UUID
        cur.execute("""
            CREATE TABLE IF NOT EXISTS topic_performance (
                performance_id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                topic_id INT REFERENCES topics(topic_id) ON DELETE CASCADE,
                accuracy DECIMAL(5,2)
            );
        """)
        print("   ✅ [9/10] Table 'topic_performance' created.")

        # --- 10. DIFFICULTY_HISTORY (Analytics) ---
        # user_id is now UUID
        cur.execute("""
            CREATE TABLE IF NOT EXISTS difficulty_history (
                history_id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                difficulty VARCHAR(10),
                accuracy DECIMAL(5,2)
            );
        """)
        print("   ✅ [10/10] Table 'difficulty_history' created.")

        conn.commit()
        cur.close()
        conn.close()
        print("\n✨ NEW DATABASE SCHEMA IS READY! ✨")

    except Exception as e:
        print("\n❌ Error Creating Tables:")
        print(e)

if __name__ == "__main__":
    initialize_database()
