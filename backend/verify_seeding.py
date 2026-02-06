import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("DATABASE_URL")
if url.startswith("postgres://"): url = url.replace("postgres://", "postgresql://", 1)

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    
    # Check Subject
    cur.execute("SELECT subject_id, subject_name FROM subjects WHERE subject_name = 'Effective Technical Communication'")
    subj = cur.fetchone()
    print(f"Subject: {subj}")
    
    if subj:
        # Check Topics
        cur.execute("SELECT topic_name, topic_id FROM topics WHERE subject_id = %s", (subj[0],))
        topics = cur.fetchall()
        print(f"Topics ({len(topics)}):")
        for t in topics:
            cur.execute("SELECT COUNT(*) FROM questions WHERE topic_id = %s", (t[1],))
            count = cur.fetchone()[0]
            print(f" - {t[0]}: {count} questions")
            
        with open("verification_results.txt", "w") as f:
            f.write(f"Subject: {subj}\n")
            f.write(f"Topics ({len(topics)}):\n")
            for t in topics:
                cur.execute("SELECT COUNT(*) FROM questions WHERE topic_id = %s", (t[1],))
                count = cur.fetchone()[0]
                f.write(f" - {t[0]}: {count} questions\n")
            
            # Total Questions
            cur.execute("SELECT COUNT(*) FROM questions")
            total = cur.fetchone()[0]
            f.write(f"Total Questions in DB: {total}\n")
            print("Verification logged to verification_results.txt")
            
    if conn: conn.close()
except Exception as e:
    print(f"Error: {e}")
