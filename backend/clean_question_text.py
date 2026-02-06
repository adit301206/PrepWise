import psycopg2
import os
import re
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("DATABASE_URL")
if url and url.startswith("postgres://"): url = url.replace("postgres://", "postgresql://", 1)

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    
    print("🧹 Normalizing Question Text...")
    
    # regex to match "1 . ", "10 ", "5. ", etc at start
    # Pattern: Start -> digits -> optional space -> optional dot/paren -> space
    clean_pattern = re.compile(r'^(\d+[\.\)\s]\s*)')
    
    cur.execute("SELECT question_id, question_text FROM questions")
    rows = cur.fetchall()
    
    updates = 0
    for q_id, text in rows:
        match = clean_pattern.match(text)
        if match:
            # Check if it looks like a real numbering (e.g. "1. ") vs "3D printing" (starts with number but not numbering)
            # Heuristic: mostly small numbers or follows distinct pattern.
            # Our extraction produced "1 Question..." or "1. Question"
            
            clean_text = clean_pattern.sub('', text).strip()
            
            # Additional check: If clean_text becomes empty, don't do it.
            if clean_text and clean_text != text:
                # Update DB
                cur.execute("UPDATE questions SET question_text = %s WHERE question_id = %s", (clean_text, q_id))
                updates += 1
                if updates % 50 == 0:
                     print(f"cleaned: {text[:30]}... -> {clean_text[:30]}...")

    conn.commit()
    print(f"✅ Normalized {updates} questions.")
    conn.close()

except Exception as e:
    print(f"Error: {e}")
