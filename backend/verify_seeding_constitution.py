import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print("--- Database Verification ---")
    
    # 1. Subjects
    cur.execute("SELECT subject_id, subject_name FROM subjects WHERE subject_name='Constitution of India';")
    print(f"Subject: {cur.fetchall()}")
    
    # 2. Topic Counts
    cur.execute("""
        SELECT t.topic_name, COUNT(q.question_id) 
        FROM topics t 
        JOIN subjects s ON t.subject_id = s.subject_id
        LEFT JOIN questions q ON t.topic_id = q.topic_id
        WHERE s.subject_name = 'Constitution of India'
        GROUP BY t.topic_name
        ORDER BY t.topic_name;
    """)
    print("\nTopic Question Counts:")
    rows = cur.fetchall()
    total = 0
    for row in rows:
        print(f"  {row[0]}: {row[1]}")
        total += row[1]
        
    print(f"\nTotal Questions: {total}")
    
    # 3. Sample Question
    cur.execute("""
        SELECT q.question_text, q.correct_option, q.option_a, q.option_b, q.option_c, q.option_d, q.difficulty 
        FROM questions q 
        JOIN topics t ON q.topic_id = t.topic_id 
        JOIN subjects s ON t.subject_id = s.subject_id
        WHERE s.subject_name = 'Constitution of India'
        LIMIT 1;
    """)
    print("\nSample Question:")
    print(cur.fetchone())

except Exception as e:
    print(e)
finally:
    if conn: conn.close()
