import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

def check_counts():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        print("\n📊 Current Question Counts per Topic:\n")
        cur.execute("""
            SELECT s.subject_name, t.topic_name, COUNT(q.question_id)
            FROM topics t
            JOIN subjects s ON t.subject_id = s.subject_id
            LEFT JOIN questions q ON t.topic_id = q.topic_id
            GROUP BY s.subject_name, t.topic_name
            ORDER BY s.subject_name, t.topic_name;
        """)
        
        rows = cur.fetchall()
        for subject, topic, count in rows:
            print(f"{subject} - {topic}: {count}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_counts()
