import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

EXCEL_PATH = r'e:\PrepWise\QB_CI_SEM-III (1).xlsx'
SUBJECT_NAME = "Constitution of India"

def get_db_connection():
    return psycopg2.connect(DB_URL)

def normalize_option(opt):
    """Normalize option text: remove NaN, convert to string, strip whitespace."""
    if pd.isna(opt):
        return None
    return str(opt).strip()

def normalize_answer(ans):
    """Normalize answer key: 'a' -> 'A', etc."""
    if pd.isna(ans):
        return None
    ans = str(ans).strip().upper()
    if ans in ['A', 'B', 'C', 'D']:
        return ans
    return None

def seed_constitution_questions():
    print(f"🚀 Starting seeding for '{SUBJECT_NAME}'...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Ensure Subject Exists
        cur.execute("SELECT subject_id FROM subjects WHERE subject_name = %s;", (SUBJECT_NAME,))
        res = cur.fetchone()
        if res:
            subject_id = res[0]
            print(f"   ✅ Subject '{SUBJECT_NAME}' found (ID: {subject_id}).")
        else:
            cur.execute("INSERT INTO subjects (subject_name) VALUES (%s) RETURNING subject_id;", (SUBJECT_NAME,))
            subject_id = cur.fetchone()[0]
            conn.commit()
            print(f"   ✅ Subject '{SUBJECT_NAME}' created (ID: {subject_id}).")

        # 2. Read Excel
        # Based on analysis, header extraction was messy, but we mapped columns by index using data row 19.
        # However, we need to skip the messy header rows.
        # We'll read with header=None and iterate, checking for valid data.
        df = pd.read_excel(EXCEL_PATH, header=None)
        
        questions_added = 0
        batch_size = 50
        
        # We start iterating. We know valid data starts around row 18 (0-indexed in code inspection was 18, 19...).
        # We will look for rows where Col 1 (Unit ID) is a number.
        
        print("   📂 Reading Excel file...")
        
        for index, row in df.iterrows():
            # Check if this looks like a data row
            # Col 1 should be the Unit No (e.g., 1, 2, 3...)
            # Col 2 should be Question Text
            
            unit_val = row[1]
            q_text = row[2]
            
            # Simple validation: Unit must be numeric-ish, Question must be string
            if pd.isna(unit_val) or pd.isna(q_text):
                continue
                
            try:
                unit_no = int(unit_val)
            except ValueError:
                # pass if header row or garbage
                continue
            
            # Valid Row Found
            topic_name = f"Unit {unit_no}"
            
            # 3. Ensure Topic Exists
            cur.execute("SELECT topic_id FROM topics WHERE topic_name = %s AND subject_id = %s;", (topic_name, subject_id))
            res = cur.fetchone()
            if res:
                topic_id = res[0]
            else:
                cur.execute("INSERT INTO topics (topic_name, subject_id) VALUES (%s, %s) RETURNING topic_id;", (topic_name, subject_id))
                topic_id = cur.fetchone()[0]
                # maintain dictionary cache if needed, but simple query is fine for now
            
            # 4. Prepare Question Data
            col_q_text = str(q_text).strip()
            col_ans = normalize_answer(row[3]) # Col 3 is Answer
            col_opt_a = normalize_option(row[5]) # Col 5
            col_opt_b = normalize_option(row[6]) # Col 6
            col_opt_c = normalize_option(row[7]) # Col 7
            col_opt_d = normalize_option(row[8]) # Col 8
            
            if not col_q_text or not col_ans:
                print(f"   ⚠️ Skipping Row {index}: Missing text or answer.")
                continue

            # 5. Insert Question
            # Check for generic duplicate (topic_id + q_text) to avoid double seeding if run twice
            cur.execute("""
                INSERT INTO questions 
                (topic_id, question_text, option_a, option_b, option_c, option_d, correct_option, difficulty)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)
                ON CONFLICT (topic_id, question_text) DO NOTHING
            """, (topic_id, col_q_text, col_opt_a, col_opt_b, col_opt_c, col_opt_d, col_ans))
            
            questions_added += 1
            
            # Batch Commit
            if questions_added % batch_size == 0:
                conn.commit()
                print(f"   COMMIT: Added {questions_added} questions total...")

        # Final Commit
        conn.commit()
        print(f"\n🎉 Finished! Total Questions Added: {questions_added}")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during seeding: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_constitution_questions()
