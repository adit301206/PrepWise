import psycopg2
import os
import random
import difflib
from dotenv import load_dotenv

load_dotenv()

# Import the split dataset to avoid large file issues
try:
    # from seed_data_part1 import data_part1
    # from seed_data_part2 import data_part2
    # raw_questions = data_part1 + data_part2
    
    # NEW: Import directly from extracted PDF data (Part 3)
    from seed_data_extracted import extracted_data as raw_questions
    print(f"Loaded {len(raw_questions)} questions from extracted PDF data.")

except ImportError as e:
    print(f"CRITICAL: Error importing seed data: {e}")
    raw_questions = []

def seed_db():
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("Error: DATABASE_URL not found.")
        return
    
    # Fix for Render/Heroku (postgres:// -> postgresql://)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        print(f"Connected to database. Seeding {len(raw_questions)} questions...")
        
        # 0. Ensure Subject Exists
        subject_name = "Effective Technical Communication"
        cur.execute("SELECT subject_id FROM subjects WHERE subject_name = %s", (subject_name,))
        sub_res = cur.fetchone()
        
        if not sub_res:
            cur.execute("INSERT INTO subjects (subject_name) VALUES (%s) RETURNING subject_id", (subject_name,))
            subject_id = cur.fetchone()[0]
            print(f"✅ Created Subject: {subject_name}")
        else:
            subject_id = sub_res[0]
            print(f"ℹ️  Found Subject: {subject_name} (ID: {subject_id})")

        count_added = 0
        count_skipped = 0

        for unit, question, ans_text, opt1, opt2, opt3, opt4 in raw_questions:
            
            # 1. Create/Get Topic
            topic_name = f"Unit {unit}"
            cur.execute("SELECT topic_id FROM topics WHERE topic_name = %s AND subject_id = %s", (topic_name, subject_id))
            res = cur.fetchone()
            if not res:
                cur.execute("INSERT INTO topics (topic_name, subject_id) VALUES (%s, %s) RETURNING topic_id", (topic_name, subject_id))
                topic_id = cur.fetchone()[0]
                print(f"   Created Topic: {topic_name}")
            else:
                topic_id = res[0]

            # 2. Shuffle Options
            options = [opt1, opt2, opt3, opt4]
            # Remove any empty/None options just in case
            options = [o for o in options if o and o.strip() != '']
            random.shuffle(options)

            # 3. Find Correct Answer (Fuzzy Match)
            # Try exact match first
            try:
                # Clean up text for matching
                clean_ans = ans_text.strip().lower()
                clean_opts = [o.strip().lower() for o in options]
                
                if clean_ans in clean_opts:
                    match_index = clean_opts.index(clean_ans)
                else:
                    # Fuzzy match
                    matches = difflib.get_close_matches(ans_text, options, n=1, cutoff=0.6) # Lowered cutoff slightly
                    if matches:
                        match_index = options.index(matches[0])
                    else:
                        print(f"⚠️ SKIPPING: '{question[:30]}...' -> Could not find answer '{ans_text}' in options {options}")
                        count_skipped += 1
                        continue
                
                correct_char = ['A', 'B', 'C', 'D'][match_index]
                
                # 4. Insert Question
                # Check if exists first to avoid duplicates
                cur.execute("SELECT question_id FROM questions WHERE question_text = %s AND topic_id = %s", (question, topic_id))
                if not cur.fetchone():
                    # Ensure we have 4 options for the DB schema
                    while len(options) < 4: options.append("") 
                    
                    cur.execute("""
                        INSERT INTO questions (topic_id, question_text, option_a, option_b, option_c, option_d, correct_option, difficulty)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Medium')
                    """, (topic_id, question, options[0], options[1], options[2], options[3], correct_char))
                    if count_added % 20 == 0:
                        print(f"✅ Added: {question[:30]}... (Ans: {correct_char})")
                    count_added += 1
                else:
                    # print(f"ℹ️ Exists: {question[:30]}...")
                    pass

            except Exception as e:
                print(f"❌ Error processing question '{question[:20]}...': {e}")
                count_skipped += 1

        conn.commit()
        print(f"\n🎉 Database seeding complete! Added: {count_added}, Skipped: {count_skipped}, Total Scanned: {len(raw_questions)}")

    except Exception as e:
        print(f"Database Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals() and conn: conn.close()

if __name__ == "__main__":
    seed_db()
