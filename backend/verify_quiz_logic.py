import os
import psycopg2
import random
from dotenv import load_dotenv

# Load logic from app.py essentially
load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

def verify_quiz_logic():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print("--- Verifying Quiz Logic for Constitution of India ---")
    
    # 1. Get Topics
    cur.execute("""
        SELECT topic_id FROM topics t
        JOIN subjects s ON t.subject_id = s.subject_id
        WHERE s.subject_name = 'Constitution of India'
        LIMIT 5;
    """)
    topic_rows = cur.fetchall()
    if not topic_rows:
        print("❌ No topics found for Constitution of India")
        return

    topic_ids = [r[0] for r in topic_rows]
    print(f"Using Topics: {topic_ids}")
    
    # 2. Fetch Questions
    # Simulate fetching questions like app.py
    # app.py logic:
    # cur.execute(f"SELECT ... FROM questions WHERE topic_id IN ...")
    
    placeholders = ','.join(['%s'] * len(topic_ids))
    query = f"SELECT question_text, difficulty FROM questions WHERE topic_id IN ({placeholders})"
    cur.execute(query, tuple(topic_ids))
    all_questions = [{'text': r[0], 'difficulty': r[1]} for r in cur.fetchall()]
    
    print(f"Fetched {len(all_questions)} questions from DB.")
    
    # 3. Apply Logic (Copied from app.py)
    total_questions = 10
    
    easy_q = [q for q in all_questions if q['difficulty'] == 'Easy']
    medium_q = [q for q in all_questions if q['difficulty'] == 'Medium']
    hard_q = [q for q in all_questions if q['difficulty'] == 'Hard']
    uncategorized_q = [q for q in all_questions if not q['difficulty']]

    print(f"Counts -> Easy: {len(easy_q)}, Med: {len(medium_q)}, Hard: {len(hard_q)}, Uncategorized: {len(uncategorized_q)}")

    random.shuffle(easy_q)
    random.shuffle(medium_q)
    random.shuffle(hard_q)
    random.shuffle(uncategorized_q)

    n_easy_target = int(total_questions * 0.5)
    n_med_target = int(total_questions * 0.3)
    n_hard_target = total_questions - (n_easy_target + n_med_target)

    final_questions = []

    # Step A: Fill Easy
    taken_easy = easy_q[:n_easy_target]
    final_questions.extend(taken_easy)
    missing_from_easy = n_easy_target - len(taken_easy)

    # Step B: Fill Medium
    needed_med = n_med_target + missing_from_easy
    taken_med = medium_q[:needed_med]
    final_questions.extend(taken_med)
    missing_from_med = needed_med - len(taken_med)

    # Step C: Fill Hard
    needed_hard = n_hard_target + missing_from_med
    taken_hard = hard_q[:needed_hard]
    final_questions.extend(taken_hard)

    # Step D: Overflow
    current_count = len(final_questions)
    if current_count < total_questions:
        needed = total_questions - current_count
        print(f"Need {needed} more from leftovers...")
        
        leftovers = []
        if len(easy_q) > len(taken_easy): leftovers.extend(easy_q[len(taken_easy):])
        if len(medium_q) > len(taken_med): leftovers.extend(medium_q[len(taken_med):])
        if len(hard_q) > len(taken_hard): leftovers.extend(hard_q[len(taken_hard):])
        
        # KEY PART: Include Uncategorized
        leftovers.extend(uncategorized_q)
        
        random.shuffle(leftovers)
        final_questions.extend(leftovers[:needed])

    print(f"Final Selection Size: {len(final_questions)}")
    
    if len(final_questions) == 10:
        print("✅ SUCCESS: Correctly generated 10 questions using fallback logic.")
    else:
        print(f"❌ FAILURE: Expected 10, got {len(final_questions)}")

if __name__ == "__main__":
    verify_quiz_logic()
