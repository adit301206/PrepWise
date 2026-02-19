import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from supabase import create_client, Client
import random
import requests
from psycopg2.extras import RealDictCursor
from datetime import date
import uuid
from models import User, HistoryStack
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # USE THE NEW LITE MODEL FOR THE FREE TIER TO PREVENT 404 AND 429 ERRORS
    model = genai.GenerativeModel('gemini-2.5-flash-lite') 
else:
    print("WARNING: GEMINI_API_KEY not found in .env")

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

# File Upload Config
UPLOAD_FOLDER = 'static/uploads/avatars'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

print("------------------------------------------------")
print("DEBUG: Checking .env file...")
db_url = os.environ.get("DATABASE_URL")

if db_url:
    print(f"DEBUG: Success! Found Database URL: {db_url[:15]}...")
else:
    print("DEBUG: ERROR! DATABASE_URL is EMPTY or None.")
    print("DEBUG: Make sure .env is in the same folder as app.py")
print("------------------------------------------------")

# Fix for Render/Heroku (postgres:// -> postgresql://)
# Fix for Render/Heroku (postgres:// -> postgresql://)
DB_URL = os.environ.get("DATABASE_URL")
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

# --- DATABASE HELPER FUNCTIONS ---

def get_db():
    """Opens a new database connection if one doesn't exist for the current request."""
    if 'db' not in g:
        try:
            g.db = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"Database Connection Error: {e}")
            return None
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- PAGE ROUTES (Serves your HTML files) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')



@app.route('/student-dashboard')
def student_dashboard():
    # 1. OOP & DSA Integration
    from models import User, HistoryStack
    
    # AUTH CHECK
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    print("Dashboard accessed by:", user_id)
    
    conn = get_db()
    
    # Initialize defaults (Safe Fallback)
    daily_count = 0
    daily_percentage = 0
    history_list = []
    analytics_data = {}
    leaderboard_data = [] # Safe Fallback
    
    try:
        if user_id and conn:
            # OOP: Create User Object
            current_user = User(conn, user_id)
            
            # OOP: Fetch Data through methods
            raw_history = current_user.get_attempt_history()
            # Safety check for history
            if raw_history is None:
                raw_history = []
                
            analytics_data = current_user.get_analytics()
            
            # DSA: Use Stack to reverse order (LIFO)
            history_stack = HistoryStack()
            history_stack.load_history(raw_history)
            history_list = history_stack.pop_all() # Most recent attempts first
            
            # --- DAILY PROGRESS FEATURE (SQL) ---
            today = date.today()
            # Using RealDictCursor, COUNT(*) will be in a key usually named 'count'
            with conn.cursor() as cur:
                 cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM attempts 
                    WHERE user_id = %s AND attempted_at::date = %s;
                 """, (user_id, today))
                 res = cur.fetchone()
                 daily_count = res['count'] if res else 0
                 
            # Safety Check: Ensure daily_count is not None
            if daily_count is None:
                daily_count = 0
                 
            daily_goal = 5
            # Prevent Division by Zero just in case daily_goal is 0 (though unlikely here)
            if daily_goal > 0:
                daily_percentage = int((daily_count / daily_goal) * 100)
            else:
                daily_percentage = 0
                
            if daily_percentage > 100: daily_percentage = 100

            # --- Leaderboard DSA Integration ---
            try:
                from models import LeaderboardDSA
                lb_engine = LeaderboardDSA(conn)
                leaderboard_data = lb_engine.get_top_students(limit=5)
            except Exception as e:
                print(f"Leaderboard Error: {e}")
                import traceback
                traceback.print_exc()
                leaderboard_data = []

        return render_template('student_dashboard.html', 
                             history=history_list, 
                             user_stats=analytics_data,
                             daily_count=daily_count,
                             daily_percentage=daily_percentage,
                             leaderboard=leaderboard_data,  # <--- NEW VARIABLE
                             user=current_user)

    except Exception as e:
        print(f"DASHBOARD ERROR: {e}")
        import traceback
        traceback.print_exc() # Print full stack trace to terminal
        return f"An internal error occurred: {e}", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Redirects to the appropriate dashboard based on user role."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role', 'student')
    if role in ['teacher', 'admin']:
        return redirect(url_for('teacher_console'))
    else:
        return redirect(url_for('student_dashboard'))

@app.route('/teacher-console')
def teacher_console():
    """Renders the teacher console with dynamic data."""
    # 1. Auth Check
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role', 'student')
    if role != 'teacher' and role != 'admin':
        return redirect(url_for('student_dashboard'))

    conn = get_db()
    if not conn:
        return "Database Error", 500
        
    try:
        cur = conn.cursor()

        # 2. Fetch Stats (Fix: RealDictCursor returns dicts, use keys or alias)
        cur.execute("SELECT COUNT(*) as c FROM users")
        user_count = cur.fetchone()['c']
        
        cur.execute("SELECT COUNT(*) as c FROM subjects")
        subject_count = cur.fetchone()['c']
        
        cur.execute("SELECT COUNT(*) as c FROM topics")
        topic_count = cur.fetchone()['c']
        
        cur.execute("SELECT COUNT(*) as c FROM questions")
        question_count = cur.fetchone()['c']
        
        stats = {
            'users': user_count,
            'subjects': subject_count,
            'topics': topic_count,
            'questions': question_count
        }

        # 3. Fetch Recent Activity (Last 5 Users)
        cur.execute("SELECT name, email, role, to_char(created_at, 'MM/DD/YYYY') as created_at FROM users ORDER BY created_at DESC LIMIT 5")
        recent_activity = cur.fetchall()

        # 4. Fetch All Users
        cur.execute("SELECT user_id, email, role, to_char(created_at, 'MM/DD/YYYY') as created_at FROM users ORDER BY created_at DESC")
        all_users = cur.fetchall()

        # 5. Fetch Curriculum
        cur.execute("SELECT * FROM subjects ORDER BY subject_name")
        subjects = cur.fetchall()
        
        cur.execute("""
            SELECT t.topic_id, t.topic_name, s.subject_name 
            FROM topics t 
            JOIN subjects s ON t.subject_id = s.subject_id 
            ORDER BY s.subject_name, t.topic_name
        """)
        topics = cur.fetchall()

        # 6. Fetch Questions (Limit 20 for performance)
        cur.execute("""
            SELECT q.question_id, q.question_text, q.difficulty, t.topic_name 
            FROM questions q
            JOIN topics t ON q.topic_id = t.topic_id
            ORDER BY q.question_id DESC LIMIT 20
        """)
        questions = cur.fetchall()
        
        cur.close()

        # 7. Generate Global Analytics Charts
        from analytics_engine import GlobalAnalyticsEngine
        # Re-use connection or get a fresh one if needed. 
        # Since cur.close() only closes the cursor, conn is still open if it wasn't closed.
        # However, to be safe and clean, let's just pass the existing 'conn' 
        # (Assuming it is still valid. get_db() returns g.db which is valid for request duration)
        
        analytics_engine = GlobalAnalyticsEngine(conn)
        charts = analytics_engine.generate_global_charts()

        return render_template('teacher_console.html', 
                             stats=stats, 
                             recent_users=recent_activity, 
                             users=all_users, 
                             subjects=subjects, 
                             topics=topics, 
                             questions=questions,
                             charts=charts)
                             
    except Exception as e:
        print(f"Error loading teacher console: {e}")
        return "Server Error calling DB", 500

# --- ADMIN API ENDPOINTS ---

@app.route('/api/admin/subject/add', methods=['POST'])
def add_subject_api():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    name = data.get('subject_name')
    if not name: return jsonify({"error": "Missing name"}), 400
    
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO subjects (subject_name) VALUES (%s) RETURNING subject_id", (name,))
        conn.commit()
        cur.close()
        return jsonify({"message": "Subject added"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/topic/add', methods=['POST'])
def add_topic_api():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    subject_id = data.get('subject_id')
    name = data.get('topic_name')
    
    if not subject_id or not name: return jsonify({"error": "Missing data"}), 400
    
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO topics (subject_id, topic_name) VALUES (%s, %s)", (subject_id, name))
        conn.commit()
        cur.close()
        return jsonify({"message": "Topic added"})
    except Exception as e:
        conn.rollback() # Good practice to rollback
        if hasattr(e, 'pgcode') and e.pgcode == '23505': # Unique Violation
            return jsonify({"error": "Topic already exists for this subject"}), 409
        print(f"Error adding topic: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/user/delete', methods=['POST'])
def delete_user_api():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    user_id = data.get('user_id')
    
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        cur.close()
        return jsonify({"message": "User deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/user/role', methods=['POST'])
def update_user_role_api():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    user_id = data.get('user_id')
    new_role = data.get('new_role')
    
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET role = %s WHERE user_id = %s", (new_role, user_id))
        conn.commit()
        cur.close()
        return jsonify({"message": "Role updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/question/add', methods=['POST'])
def add_question_api():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    # Expected: topic_id, text, options (JSON array), correct_option (index usually), difficulty, explanation
    
    topic_id = data.get('topic_id')
    text = data.get('text')
    options = data.get('options') # List of strings
    correct_idx = data.get('correct_index') # Integer 0-3
    difficulty = data.get('difficulty', 'medium')
    explanation = data.get('explanation', '')
    
    if not topic_id or not text or not options:
        return jsonify({"error": "Missing required fields"}), 400
        
    # Map options list to columns
    opt_a = options[0] if len(options) > 0 else None
    opt_b = options[1] if len(options) > 1 else None
    opt_c = options[2] if len(options) > 2 else None
    opt_d = options[3] if len(options) > 3 else None
    
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO questions (topic_id, question_text, option_a, option_b, option_c, option_d, correct_option, difficulty, explanation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (topic_id, text, opt_a, opt_b, opt_c, opt_d, correct_idx, difficulty, explanation))
        conn.commit()
        cur.close()
        return jsonify({"message": "Question added"})
    except Exception as e:
        print(f"Add Question Failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/question/delete', methods=['POST'])
def delete_question_api():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    question_id = data.get('question_id')
    
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM questions WHERE question_id = %s", (question_id,))
        conn.commit()
        cur.close()
        return jsonify({"message": "Question deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analytics')
def analytics():
    from analytics_engine import AnalyticsEngine
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = get_db()
                
    if not conn:
        return "Please log in or ensure database is connected", 401

    # OOP: Instantiate Engine
    engine = AnalyticsEngine(user_id, conn)
    
    # OOP: Fetch Data via Methods
    topic_stats = engine.process_topic_performance()
    subject_stats = engine.get_subject_performance() # NEW: Fetch by Subject
    weakest_topics = engine.get_weakest_areas()
    strongest_topics = engine.get_strongest_areas()
    overall_stats = engine.get_overall_stats()
    
    # Backend Rendering: Generate Matplotlib Charts
    charts = engine.generate_charts()
    
    return render_template('analytics.html', 
                         overall=overall_stats,
                         topic_stats=topic_stats,
                         subject_stats=subject_stats, # NEW: Pass by Subject
                         weakest_topics=weakest_topics,
                         strongest_topics=strongest_topics,
                         charts=charts)

@app.route('/api/analytics/progress-chart', methods=['POST'])
def update_progress_chart():
    from analytics_engine import AnalyticsEngine
    
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user_id']
    conn = get_db()
    
    if not conn:
        return jsonify({"error": "DB Connection Error"}), 500
        
    data = request.json
    time_filter = data.get('time_filter', '7d')
    
    try:
        engine = AnalyticsEngine(user_id, conn)
        chart_b64 = engine.generate_progress_chart_img(time_filter)
        return jsonify({"chart": chart_b64})
    except Exception as e:
        print(f"Chart Update Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/start-quiz', methods=['GET', 'POST'])
def start_quiz():
    """
    Adaptive Quiz Algorithm (Bucket Filling)
    1. Fetches ALL questions for selected topics.
    2. Filters into Easy/Medium/Hard lists.
    3. Fills buckets (50/30/20) with overflow handling.
    4. Ensures user gets 'total_questions' if enough exist in DB.
    """
    import random
    try:
        # 1. Get Data from Form
        if 'user_id' not in session:
            return redirect(url_for('login'))

        topic_ids_str = request.args.get('topic_ids')
        if request.method == 'POST':
             # Check form for IDs if POST
             # (Frontend redirection might largely rely on GET parameters currently, but handling form input is robust)
             pass 
        
        if not topic_ids_str:
            topic_ids_str = request.form.get('topic_ids_hidden')

        if not topic_ids_str:
             return "No topics selected", 400
             
        topic_ids = [int(tid) for tid in topic_ids_str.split(',') if tid.isdigit()]
        
        conn = get_db()
        cur = conn.cursor()

        # 2. Get Total Questions Requested
        try:
             total_questions = int(request.form.get('num_questions', 10))
        except ValueError:
             total_questions = 10

        print(f"DEBUG: User requested {total_questions} questions from topics {topic_ids}")

        # 3. Fetch ALL Questions for these topics
        # We fetch everything first to handle the mixing logic in Python
        topic_placeholders = ','.join(['%s'] * len(topic_ids))
        cur.execute(f"""
            SELECT question_id, topic_id, question_text, option_a, option_b, option_c, option_d, correct_option, difficulty, explanation 
            FROM questions 
            WHERE topic_id IN ({topic_placeholders});
        """, tuple(topic_ids))
        all_questions = cur.fetchall()
        cur.close()

        if not all_questions:
            return render_template('quiz.html', questions=[])

        # 4. Categorize & Shuffle
        easy_q = [q for q in all_questions if q['difficulty'] == 'Easy']
        medium_q = [q for q in all_questions if q['difficulty'] == 'Medium']
        hard_q = [q for q in all_questions if q['difficulty'] == 'Hard']
        
        # New: Handle Uncategorized (NULL difficulty)
        uncategorized_q = [q for q in all_questions if not q['difficulty']]

        random.shuffle(easy_q)
        random.shuffle(medium_q)
        random.shuffle(hard_q)
        random.shuffle(uncategorized_q)

        # 5. Calculate Selection Targets
        n_easy_target = int(total_questions * 0.5)  # 50%
        n_med_target = int(total_questions * 0.3)   # 30%
        n_hard_target = total_questions - (n_easy_target + n_med_target) # Remainder (approx 20%)

        print(f"DEBUG: Targets -> Easy: {n_easy_target}, Med: {n_med_target}, Hard: {n_hard_target}")

        final_questions = []

        # Step A: Fill Easy
        # Take up to target, or whatever we have
        taken_easy = easy_q[:n_easy_target]
        final_questions.extend(taken_easy)
        
        # Calculate overflow (if we wanted 5 but got 3, we need 2 more)
        missing_from_easy = n_easy_target - len(taken_easy)
        
        # Step B: Fill Medium (Target + Overflow from Easy)
        needed_med = n_med_target + missing_from_easy
        taken_med = medium_q[:needed_med]
        final_questions.extend(taken_med)

        # Calculate overflow
        missing_from_med = needed_med - len(taken_med)

        # Step C: Fill Hard (Target + Overflow from prev)
        needed_hard = n_hard_target + missing_from_med
        taken_hard = hard_q[:needed_hard]
        final_questions.extend(taken_hard)

        # Step D: Final Overflow (If Hard is also empty/short)
        # We might still be short if Hard list was small OR if we only have uncategorized questions.
        # Grab from any remaining leftovers in Easy/Medium/Hard lists AND uncategorized.
        
        current_count = len(final_questions)
        if current_count < total_questions:
            needed = total_questions - current_count
            print(f"DEBUG: Still need {needed} questions. Checking leftovers...")
            
            # Identify leftovers (questions that weren't picked)
            leftovers = []
            if len(easy_q) > len(taken_easy): leftovers.extend(easy_q[len(taken_easy):])
            if len(medium_q) > len(taken_med): leftovers.extend(medium_q[len(taken_med):])
            if len(hard_q) > len(taken_hard): leftovers.extend(hard_q[len(taken_hard):])
            
            # Add all uncategorized to leftovers
            leftovers.extend(uncategorized_q)
            
            random.shuffle(leftovers)
            final_questions.extend(leftovers[:needed])

        # Final Shuffle to mix difficulties
        random.shuffle(final_questions)
        
        print(f"DEBUG: Generated {len(final_questions)} questions.")

        return render_template('quiz.html', questions=final_questions)

    except Exception as e:
        print(f"QUIZ FACTORY ERROR: {e}")
        return f"Error generating quiz: {str(e)}", 500

@app.route('/quiz')
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # If accessed directly via GET with params, we can proxy to start_quiz
    if request.args.get('topic_ids'):
        return start_quiz()
    return render_template('quiz.html', questions=[])

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/quiz/result')
def quiz_result():
    try:
        score = int(request.args.get('score', 0))
        total = int(request.args.get('total', 10))
        skipped = int(request.args.get('skipped', 0))
        
        percentage = (score / total) * 100 if total > 0 else 0
        degree = (percentage / 100) * 360  # For Conic Gradient

        if percentage >= 80:
            msg = "Excellent work! You're mastering this."
        elif percentage >= 50:
            msg = "Good effort! Keep practicing to improve."
        else:
            msg = "Don't give up! Review the topics and try again."

        return render_template('result.html', 
                             score=score, 
                             total=total, 
                             skipped=skipped, 
                             score_percent=int(percentage), 
                             percentage=f"{degree:.1f}", # Passing degrees for CSS
                             feedback_message=msg)
    except Exception as e:
        return f"Error loading result: {str(e)}", 500

@app.route('/api/save-quiz-result', methods=['POST'])
def save_quiz_result():
    from models import User
    
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    user_id = session['user_id'] # Use Trusted Session ID
    score = data.get('score')
    total = data.get('total')
    topic_id = data.get('topic_id') 
    
    if not user_id:
        # Fallback if we want to support demo users who haven't logged in? 
        # Or error out. For now, let's error if logic relies on user.
        return jsonify({"error": "User ID required"}), 400

    conn = get_db()
    if conn:
        user = User(conn, user_id)
        # If topic_id is missing, find a fallback or just pass None (DB might fail if not nullable)
        # Let's verify DB schema. attempts table has topic_id.
        # If we don't have it, we might grab the first one from DB or just fail safely.
        
        # FIX: The seed script created topics. We need a valid topic_id.
        # If frontend doesn't send it, lets default to a known one for safety or fix frontend to send it.
        # Assuming frontend will send it.
        
        success = user.save_attempt(topic_id, score, total)
        
        # 2. Save Detailed Analysis to Session (Temporary)
        # We do this regardless of DB success to allow review even if DB fails
        detailed_history = data.get('detailed_history', [])
        session['latest_quiz_analysis'] = {
            'score': score,
            'total': total,
            'topic_id': topic_id,
            'history': detailed_history
        }
        
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Database insert failed"}), 500
            
    return jsonify({"error": "DB Connection failed"}), 500

@app.route('/quiz/review')
def quiz_review():
    """Displays detailed analysis of the last taken quiz."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    analysis = session.get('latest_quiz_analysis')
    
    if not analysis:
        # Fallback or redirect if no recent quiz found
        return redirect(url_for('student_dashboard'))
        
    return render_template('review.html', 
                         analysis=analysis,
                         questions=analysis.get('history', []))

    return render_template('review.html', 
                         analysis=analysis,
                         questions=analysis.get('history', []))

@app.route('/api/analyze-performance', methods=['POST'])
def analyze_performance():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    analysis = session.get('latest_quiz_analysis')
    if not analysis:
        return jsonify({"error": "No recent quiz found"}), 404
        
    history = analysis.get('history', [])
    score = analysis.get('score')
    total = analysis.get('total')
    
    # Construct Prompt
    prompt = f"""
    You are an AI Tutor. Analyze the student's quiz performance.
    Score: {score}/{total}
    
    Questions & Answers:
    """
    
    for q in history:
        status = "Correct" if q['is_correct'] else "Skipped" if q['is_skipped'] else "Incorrect"
        prompt += f"- Q: {q['question_text']}\n  Status: {status}\n"
        if not q['is_correct'] and not q['is_skipped']:
             prompt += f"  Student Chose: {q['user_selected_text']}\n  Correct: {q['correct_option_text']}\n"
             
    prompt += """
    
    Provide a concise analysis in Markdown:
    1. **Strengths**: What did they do well?
    2. **Weaknesses**: Which concepts need review?
    3. **Actionable Tips**: specific advice to improve.
    Keep it encouraging but constructive. Max 200 words.
    """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"analysis": response.text})
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return jsonify({"error": "AI Service Unavailable"}), 500

@app.route('/api/review/ai-insight', methods=['POST'])
def review_ai_insight():
    import re
    
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    analysis = session.get('latest_quiz_analysis')
    if not analysis:
        return jsonify({'error': 'No quiz data found in session.'}), 400
        
    score = analysis.get('score')
    total = analysis.get('total')
    history = analysis.get('history', [])
    
    # Isolate mistakes for AI Analysis
    wrong_skipped = [q for q in history if not q.get('is_correct')]
    
    prompt = f"The student scored {score} out of {total} on their recent quiz.\n"
    
    if wrong_skipped:
        prompt += "They struggled with the following questions:\n"
        for q in wrong_skipped:
            status = "Skipped" if q.get('is_skipped') else "Incorrect"
            prompt += f"- Question: '{q.get('question_text')}' | Status: {status} | Correct Answer: '{q.get('correct_option_text')}'\n"
        
        # NEW STRUCTURED PROMPT
        prompt += """
        Act as an encouraging, expert AI tutor. Provide a very concise, visually attractive performance summary.
        Format your response STRICTLY using this exact HTML template structure with Bootstrap classes. Replace the bracketed [ ] info with your brief, punchy text:
        
        <h5 style="color: #4f46e5;" class="mb-2 fw-bold"><i class="fa-solid fa-bolt text-warning me-2"></i>Quick Insight</h5>
        <p class="mb-4" style="color: #475569; font-weight: 500;">[1 short sentence of encouragement, and 1 short sentence summarizing their overall performance]</p>
        
        <div class="row g-4">
            <div class="col-md-6">
                <div class="p-3 rounded-3" style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2);">
                    <h6 class="text-danger fw-bold mb-2"><i class="fa-solid fa-circle-xmark me-2"></i>Areas to Review</h6>
                    <ul style="color: #7f1d1d; font-size: 0.95rem; margin-bottom: 0; padding-left: 1.2rem;">
                        <li>[Identify a specific concept they missed in max 10 words]</li>
                        <li>[Identify another concept if applicable, otherwise remove this list item]</li>
                    </ul>
                </div>
            </div>
            <div class="col-md-6">
                <div class="p-3 rounded-3" style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.2);">
                    <h6 class="text-success fw-bold mb-2"><i class="fa-solid fa-bullseye me-2"></i>Action Plan</h6>
                    <ul style="color: #14532d; font-size: 0.95rem; margin-bottom: 0; padding-left: 1.2rem;">
                        <li>[Give a highly specific, actionable study tip based on their mistakes]</li>
                        <li>[Give a second tip if applicable, otherwise remove]</li>
                    </ul>
                </div>
            </div>
        </div>

        CRITICAL RULES:
        1. Keep the text extremely brief and scannable. No paragraphs.
        2. Output ONLY the HTML structure requested above.
        3. ABSOLUTELY NO <style>, <script>, <html>, <head>, or <body> tags.
        4. Do NOT wrap your response in markdown code blocks (like ```html).
        """
    else:
        # PERFECT SCORE PROMPT
        prompt += """
        They got a perfect score! Output exactly this HTML:
        <div class="text-center py-3">
            <div class="display-1 mb-3">🎉</div>
            <h4 class="text-success fw-bold mb-2"><i class="fa-solid fa-trophy text-warning me-2"></i>Flawless Victory!</h4>
            <p class="text-muted mb-0" style="font-size: 1.1rem;">Outstanding job! You demonstrated complete mastery of these topics. Keep up the excellent momentum!</p>
        </div>
        """
        
    try:
        # Generate content using the initialized model
        chat = model.start_chat()
        response = chat.send_message(prompt)
        
        # AGGRESSIVE SANITIZATION
        clean_text = response.text.strip()
        
        # 1. Strip markdown backticks
        import re
        clean_text = re.sub(r'^```(html)?|```$', '', clean_text, flags=re.IGNORECASE | re.MULTILINE).strip()
        # 2. Strip ALL <style> blocks and their contents
        clean_text = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', clean_text, flags=re.IGNORECASE)
        # 3. Strip structural HTML tags that break the DOM
        clean_text = re.sub(r'</?(html|head|body|meta|title|!doctype)[^>]*>', '', clean_text, flags=re.IGNORECASE)
        
        return jsonify({'insight': clean_text.strip()})
        
    except Exception as e:
        print(f"AI Insight Error: {e}")
        return jsonify({'error': "The AI is currently resting. Please try again later."}), 500


# --- API ROUTES (Backend Logic) ---

@app.route('/api/test-db')
def test_db_connection():
    """Test route to check if Supabase connection is working."""
    conn = get_db()
    if not conn:
        return jsonify({"status": "error", "message": "Could not connect to DB"}), 500
    
    try:
        cur = conn.cursor()
        # Simple query to check connection
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        
        # Check if our tables exist
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        
        cur.close()
        return jsonify({
            "status": "success", 
            "version": db_version['version'],
            "tables": tables
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/subjects')
def get_subjects():
    """Fetches all subjects from the database."""
    conn = get_db()
    if not conn: 
        # Check if DB_URL was actually set, for better error message
        if not DB_URL:
             return jsonify({"error": "DB Connection failed: DATABASE_URL not set in environment."}), 500
        return jsonify({"error": "DB Connection failed"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT subject_name FROM subjects ORDER BY subject_id;")
        subjects = [row['subject_name'] for row in cur.fetchall()]
        cur.close()
        return jsonify(subjects)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/topics')
def get_topics():
    """Fetches topics for a given subject."""
    subject = request.args.get('subject')
    if not subject:
        return jsonify({"error": "Subject parameter is required"}), 400

    conn = get_db()
    if not conn: return jsonify({"error": "DB Connection failed"}), 500
    
    try:
        cur = conn.cursor()
        # Find subject_id first
        cur.execute("SELECT subject_id FROM subjects WHERE subject_name = %s;", (subject,))
        res = cur.fetchone()
        
        if not res:
            return jsonify([]) # Return empty list if subject not found
            
        subject_id = res['subject_id']
        
        cur.execute("SELECT topic_id, topic_name FROM topics WHERE subject_id = %s ORDER BY topic_name;", (subject_id,))
        topics = [{'id': row['topic_id'], 'name': row['topic_name']} for row in cur.fetchall()]
        
        cur.close()
        return jsonify(topics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- AUTH ROUTES (Supabase) ---

# Initialize Supabase Client
from supabase import create_client, Client
from gotrue.errors import AuthApiError

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = None
if url and key:
    try:
        supabase = create_client(url, key)
    except Exception as e:
        print(f"Supabase Init Error: {e}")
else:
    print("WARNING: SUPABASE_URL or SUPABASE_KEY missing. Auth will not work.")

@app.route('/api/signup', methods=['POST'])
def signup_api():
    """Initiates signup by sending an OTP to the user's email."""
    if not supabase:
        return jsonify({"error": "Server misconfiguration: Missing Supabase credentials"}), 500

    data = request.json
    email = data.get('email')
    password = data.get('password')
    metadata = data.get('data', {}) # e.g. { "full_name": "...", "role": "student" }

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        # standard Supabase Auth signup
        print(f"DEBUG: Attempting signup for {email}")
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": metadata
            }
        })
        
        print(f"DEBUG: Signup Response: {auth_response}")
        
        # Check if we got a user back (successful signup)
        if auth_response.user:
             # Check if user already exists (identities is empty array usually means duplicate)
             if auth_response.user.identities == []:
                 print("DEBUG: User already exists (empty identities).")
                 return jsonify({"message": "User already exists. Please login or check your email."}), 200

             return jsonify({
                "message": "Signup successful! Please check your email for the verification code.",
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email
                }
            })
        else:
             # Should practically not happen if no exception was raised, but safety check
            print("DEBUG: No user returned in response.")
            return jsonify({"error": "Signup failed. No user returned."}), 400

    except Exception as e:
        print(f"Signup Error: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Step 2: Verify OTP and SYNC user to public.users table."""
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    try:
        # 1. Verify the OTP with Supabase Auth
        print(f"🔐 Verifying OTP for {email}...")
        res = supabase.auth.verify_otp({
            "email": email,
            "token": otp,
            "type": "signup"
        })

        # 2. Extract User Details from the Auth Response
        user = res.user
        user_id = user.id
        # Safely get metadata (defaults to empty dict if missing)
        meta = user.user_metadata or {} 
        full_name = meta.get('full_name', 'Student') # Default to 'Student' if name missing
        role = meta.get('role', 'student') # Default to 'student'

        print(f"✅ Auth Verified! Syncing User ID {user_id} to database...")

        # 3. SYNC: Insert this user into our 'public.users' table
        conn = get_db()
        if conn:
            cur = conn.cursor()
            # We use ON CONFLICT DO NOTHING so it doesn't crash if they verify twice
            cur.execute("""
                INSERT INTO users (user_id, email, name, role)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING;
            """, (user_id, email, full_name, role))
            conn.commit()
            cur.close()
            print("✨ User synced to public database successfully.")
            
            # 4. CREATE SESSION
            session['user_id'] = user_id
            session['user_name'] = full_name
            session['role'] = role
            session.permanent = True
            print("🔐 Session Created For:", user_id)
            
        else:
            print("⚠️ Database connection failed during sync.")

        return jsonify({
            "status": "success", 
            "message": "Email verified and account created!",
            "session": {
                "access_token": res.session.access_token,
                "user": {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name
                }
            }
        })

    except AuthApiError as e:
        print(f"❌ Supabase Auth Error: {e}")
        return jsonify({"status": "error", "message": "Invalid OTP or expired."}), 400
    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login_api():
    """Logs the user in with email and password."""
    if not supabase:
        return jsonify({"error": "Server misconfiguration"}), 500

    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        # Sign in with Supabase
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        # Get session and role from metadata
        user = res.user
        meta = user.user_metadata or {}
        role = meta.get('role', 'student') 
        access_token = res.session.access_token
        
        # 1. CLEAR OLD SESSION to prevent data leakage
        session.clear()
        
        # 2. CREATE NEW SESSION
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['role'] = role
        session.permanent = True
        
        # 3. SYNC PROFILE DATA FROM DB (name, avatar_url)
        try:
            from models import User
            conn = get_db()
            if conn:
                db_user = User(conn, user.id)
                profile_data = db_user.get_profile_data()
                if profile_data:
                    session['user_name'] = profile_data.get('name')
                    session['avatar_url'] = profile_data.get('avatar_url')
                    print(f"DEBUG: Login Sync - Name: {session.get('user_name')}, Avatar: {session.get('avatar_url')}")
        except Exception as db_e:
            print(f"DEBUG: Login Sync Error: {db_e}")
        
        return jsonify({
            "message": "Login successful!",
            "session": {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": role,
                    "name": session.get('user_name'),
                    "avatar_url": session.get('avatar_url')
                }
            }
        })

    except AuthApiError as e:
        return jsonify({"error": "Invalid email or password."}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = get_db()
    
    stats = {'accuracy': 0, 'quizzes_taken': 0, 'streak': 0, 'strongest': [], 'weakest': []}
    charts = {} # NEW: Hold the generated graphs
    
    if conn:
        try:
            from analytics_engine import AnalyticsEngine
            engine = AnalyticsEngine(user_id, conn)
            
            overall = engine.get_overall_stats()
            topic_stats = engine.process_topic_performance()
            
            stats['accuracy'] = overall.get('accuracy', 0)
            stats['quizzes_taken'] = overall.get('total_quizzes', 0)
            stats['streak'] = overall.get('streak', 0) 
            
            sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1]['avg_score'], reverse=True) if isinstance(topic_stats, dict) else topic_stats
            
            # Helper to extract data depending on structure
            def get_data(data):
                if isinstance(data, list):
                    return data
                # If dict (from old implementation?), convert to list
                return [{'name': k, 'score': v['avg_score']} for k, v in data.items()]

            # Just use engine methods which are already standardized in previous steps or standard list
            strongest = engine.get_strongest_areas()
            weakest = engine.get_weakest_areas()
            
            stats['strongest'] = [{'name': t['topic'], 'score': t['accuracy']} for t in strongest]
            stats['weakest'] = [{'name': t['topic'], 'score': t['accuracy']} for t in weakest]
            
            # NEW: Generate visual charts for the PDF
            charts = engine.generate_charts()
            
        except Exception as e:
            print(f"Settings Analytics Error: {e}")

    return render_template('settings.html', 
                           stats=stats, 
                           charts=charts, # Pass to template
                           user_email=session.get('user_email', ''), 
                           user_name=session.get('user_name', 'Student'))

@app.route('/api/settings/update-email', methods=['POST'])
def update_email_api():
    if 'user_id' not in session or not supabase: return jsonify({"error": "Unauthorized"}), 401
    try:
        res = supabase.auth.update_user({"email": request.json.get('new_email')})
        return jsonify({"message": "Verification link sent to new email."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/settings/update-password', methods=['POST'])
def update_password_settings_api():
    if 'user_id' not in session or not supabase: return jsonify({"error": "Unauthorized"}), 401
    try:
        res = supabase.auth.update_user({"password": request.json.get('new_password')})
        return jsonify({"message": "Password updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/settings/delete-history', methods=['POST'])
def delete_history_api():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM attempts WHERE user_id = %s", (session['user_id'],))
            conn.commit()
            cur.close()
            return jsonify({"message": "All quiz history deleted successfully."})
        except Exception as e:
            return jsonify({"error": "Database error occurred."}), 500
    return jsonify({"error": "No database connection."}), 500

@app.route('/profile')
def profile():
    """Renders the user profile page."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/api/user/profile', methods=['GET', 'POST'])
def user_profile_api():
    """Handles fetching and updating user profile with file upload support."""
    from models import User

    # 1. Auth Check
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    conn = get_db()
    
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        user = User(conn, user_id)
        
        if request.method == 'GET':
            # Use the new explicit method
            profile_data = user.get_profile_data()
            if profile_data:
                return jsonify(profile_data)
            else:
                return jsonify({"error": "Profile not found"}), 404
            
        elif request.method == 'POST':
            print("------------------------------------------------")
            print(f"DEBUG: POST /api/user/profile hit by User {user_id}")
            print(f"DEBUG: Form Data: {request.form}")
            print(f"DEBUG: Files Data: {request.files}")

            avatar_url_path = None

            # File Upload Logic
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and file.filename != '':
                    # Validate allowed file extensions (basic check)
                    filename = secure_filename(file.filename)
                    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    
                    if ext in app.config['ALLOWED_EXTENSIONS']:
                        # Create unique filename: user_{id}_{timestamp}.{ext}
                        import time
                        unique_filename = f"user_{user_id}_{int(time.time())}.{ext}"
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                        
                        # Save file
                        file.save(file_path)
                        
                        # Store URL path in DB (relative to static)
                        avatar_url_path = f"/static/uploads/avatars/{unique_filename}"
                        
                        # Update Session immediately
                        session['avatar_url'] = avatar_url_path
                        session.modified = True
            
            # Construct the final data dict explicitly
            # Note: We use .get() to avoid KeyErrors, and handle empty strings if needed
            update_data = {
                "name": request.form.get('name'),
                "phone": request.form.get('phone'),
                "birthdate": request.form.get('birthdate'), 
                "bio": request.form.get('bio'),
                "avatar_url": avatar_url_path 
            }
            
            print(f"DEBUG: Sending to Model: {update_data}")

            # Update DB
            success = user.update_profile(update_data)
            
            # Update Session Name if changed
            if 'name' in update_data and update_data['name']:
                session['user_name'] = update_data['name']
                session.modified = True
            
            if success:
                return jsonify({
                    "message": "Profile updated successfully!", 
                    "avatar_url": update_data.get('avatar_url') or session.get('avatar_url')
                })
            else:
                return jsonify({"error": "Failed to update profile"}), 500

    except Exception as e:
        print(f"Profile API Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/resend-otp', methods=['POST'])
def resend_otp_api():
    """Resends the signup OTP."""
    if not supabase:
        return jsonify({"error": "Server misconfiguration"}), 500

    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Resend the signup confirmation email
        supabase.auth.resend({
            "type": "signup",
            "email": email
        })
        return jsonify({"message": "OTP resent successfully."})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/update-password')
def update_password_page():
    return render_template('update_password.html')

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password_api():
    """Sends a password reset email."""
    if not supabase:
        return jsonify({"error": "Server misconfiguration"}), 500

    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        if os.environ.get('URL'):
            redirect_url = f"{os.environ.get('URL')}/update-password"
        else:
            redirect_url = url_for('update_password_page', _external=True).replace("127.0.0.1", "localhost")
        
        print(f"DEBUG: Sending reset email to {email} with redirect to {redirect_url}")
        
        supabase.auth.reset_password_email(email, options={
            "redirect_to": redirect_url
        })

        return jsonify({"message": "Password reset email sent."})

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Forgot Password Error: {e}")
        print(f"DEBUG: Checking Redirect URL: {redirect_url}")


@app.route('/api/update-password', methods=['POST'])
def update_password_api():
    """Updates the user's password using the session tokens."""
    if not supabase:
        return jsonify({"error": "Server misconfiguration"}), 500

    data = request.json
    new_password = data.get('new_password')
    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')

    if not new_password or not access_token:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # 1. Set the session using the tokens from the URL hash
        supabase.auth.set_session(access_token, refresh_token)
        
        # 2. Update the user attributes (password)
        res = supabase.auth.update_user({
            "password": new_password
        })
        
        return jsonify({"message": "Password updated successfully!"})

    except Exception as e:
        print(f"Update Password Error: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/api/chat', methods=['POST'])
def ai_chat_api():
    if not GEMINI_API_KEY:
        return jsonify({"error": "AI is currently unavailable (API key missing)."}), 503
        
    data = request.json
    action = data.get('action') 
    history = data.get('history', [])
    
    try:
        # TRIM HISTORY: Keep only the last 4 messages to prevent Token Limits!
        recent_history = history[-4:] if len(history) > 4 else history
        
        formatted_history = []
        for msg in recent_history:
            role = "model" if msg['sender'] == 'ai' else "user"
            formatted_history.append({"role": role, "parts": [msg['text']]})
            
        chat = model.start_chat(history=formatted_history)
        
        if action == 'explain':
            q_text = data.get('question')
            selected = data.get('selected')
            correct = data.get('correct')
            
            system_instruction = "You are PrepWise AI, a friendly and encouraging expert tutor. Explain concepts clearly and concisely. "
            internal_prompt = f"{system_instruction}\nI just answered a question incorrectly.\nQuestion: '{q_text}'\nI chose: '{selected}'\nThe correct answer is: '{correct}'\nCan you explain exactly why my choice was wrong and why the correct answer is right? Keep it brief and encouraging."
            
            response = chat.send_message(internal_prompt)
            return jsonify({"reply": response.text, "internal_prompt": internal_prompt})
            
        elif action == 'chat':
            message = data.get('message')
            if not message:
                return jsonify({"error": "Message is required"}), 400
                
            response = chat.send_message(message)
            return jsonify({"reply": response.text})
            
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API Error: {error_msg}")
        
        # CATCH THE 429 ERROR GRACEFULLY
        if "429" in error_msg or "Quota" in error_msg or "exhausted" in error_msg.lower():
            return jsonify({"error": "Whoa there! The AI speed limit was hit. Please wait a minute and try again."}), 429
            
        return jsonify({"error": "Sorry, I'm having trouble connecting to my brain right now."}), 500

if __name__ == '__main__':
    app.run(debug=True)