import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, g, jsonify, request, url_for
from datetime import date
from dotenv import load_dotenv
import uuid

# 1. Load environment variables from .env
load_dotenv()

print("------------------------------------------------")
print("DEBUG: Checking .env file...")
db_url = os.environ.get("DATABASE_URL")

if db_url:
    print(f"DEBUG: Success! Found Database URL: {db_url[:15]}...")
else:
    print("DEBUG: ERROR! DATABASE_URL is EMPTY or None.")
    print("DEBUG: Make sure .env is in the same folder as app.py")
print("------------------------------------------------")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")
DB_URL = os.environ.get("DATABASE_URL")

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
    
    # In a real app, we'd get user_id from session. 
    # For this demo refactor, we try to find a valid user or use a placeholder/demo logic.
    # Check if a user param is passed, or try to find one from the DB for demonstration.
    user_id = request.args.get('user_id')
    
    conn = get_db()
    
    # DEMO LOGIC: If no user_id, pick the first one to show the dashboard working
    if not user_id and conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users LIMIT 1;")
            res = cur.fetchone()
            if res:
                user_id = res['user_id']
    
    history_list = []
    analytics_data = {}
    
    if user_id and conn:
        # OOP: Create User Object
        current_user = User(conn, user_id)
        
        # OOP: Fetch Data through methods
        raw_history = current_user.get_attempt_history()
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
             
        daily_goal = 5
        daily_percentage = int((daily_count / daily_goal) * 100)
        if daily_percentage > 100: daily_percentage = 100

    return render_template('student_dashboard.html', 
                         history=history_list, 
                         user_stats=analytics_data,
                         daily_count=daily_count,
                         daily_percentage=daily_percentage)

@app.route('/teacher-console')
def teacher_console():
    return render_template('teacher_console.html')

@app.route('/analytics')
def analytics():
    from analytics_engine import AnalyticsEngine
    
    conn = get_db()
    # Demo User fallback if no session (same as dashboard)
    # In a real app we'd use session['user_id']
    user_id = request.args.get('user_id')
    
    if not user_id and conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users LIMIT 1;")
            res = cur.fetchone()
            if res:
                user_id = res['user_id']
                
    if not user_id or not conn:
        return "Please log in or ensure database is connected", 401

    # OOP: Instantiate Engine
    engine = AnalyticsEngine(user_id, conn)
    
    # OOP: Fetch Data via Methods
    topic_stats = engine.process_topic_performance()
    weakest_topics = engine.get_weakest_areas()
    strongest_topics = engine.get_strongest_areas()
    overall_stats = engine.get_overall_stats()
    
    # Backend Rendering: Generate Matplotlib Charts
    charts = engine.generate_charts()
    
    return render_template('analytics.html', 
                         overall=overall_stats,
                         topic_stats=topic_stats,
                         weakest_topics=weakest_topics,
                         strongest_topics=strongest_topics,
                         charts=charts)

@app.route('/start-quiz', methods=['GET', 'POST'])
def start_quiz():
    """
    Adaptive Quiz Algorithm (SSR)
    1. Receives selected topic IDs.
    2. Calculates difficulty mix based on user history.
    3. Fetches randomized questions.
    4. Renders quiz.html directly.
    """
    try:
        # 1. Get Data from Form
        # topic_ids comes as "1,2,3" string or list depending on implementation
        # Here we expect a simple comma separated string in query param or form for GET/POST consistency handling
        # But per requirements, it's a form POST.
        
        # Handle cases where it might come from URL (GET) for testing transparency if needed, 
        # but strictly following POST requirement:
        topic_ids_str = request.args.get('topic_ids') # Fallback for GET link
        if request.method == 'POST':
             # It might be in form as 'topics' or we might pass it differently. 
             # The dashboard JS does a window.location = ... which is a GET.
             # USER REQUESTED: <form action="/start-quiz" method="POST">
             # BUT dashboard JS currently uses GET redirection. 
             # I will parse from args if GET, or form if POST to be robust.
             pass 
        
        # Supporting both for now but focusing on the requested logic
        if not topic_ids_str:
            topic_ids_str = request.form.get('topic_ids_hidden') # If we use a hidden input

        if not topic_ids_str:
             return "No topics selected", 400
             
        topic_ids = [int(tid) for tid in topic_ids_str.split(',') if tid.isdigit()]
        
        conn = get_db()
        cur = conn.cursor()

        # 2. Adaptive Logic (Strict Distribution)
        # Get total questions requested by user (Default to 10)
        try:
             total_questions = int(request.form.get('num_questions', 10))
        except ValueError:
             total_questions = 10

        print(f"DEBUG: User requested {total_questions} questions")

        # Calculate Ratios (The Remainder Method)
        # 1. Calculate the first two
        n_easy = int(total_questions * 0.5)   # 50%
        n_med = int(total_questions * 0.3)    # 30%
      
        # 2. Force the last one to be the remainder (Ensures Sum == Total)
        n_hard = total_questions - (n_easy + n_med)

        # Safety check for very small numbers
        if n_hard < 0: n_hard = 0

        
        # 3. Fetch Questions Randomly
        # We need to distribute these counts across the selected topics.
        # Strategy: Pool all questions from selected topics, then pick per difficulty.
        
        topic_placeholders = ','.join(['%s'] * len(topic_ids))
        
        quiz_questions = []
        
        # Fetch Easy
        cur.execute(f"""
            SELECT question_id, topic_id, question_text, option_a, option_b, option_c, option_d, correct_option, difficulty, explanation 
            FROM questions 
            WHERE topic_id IN ({topic_placeholders}) AND difficulty = 'Easy'
            ORDER BY RANDOM() LIMIT %s;
        """, (*topic_ids, n_easy))
        quiz_questions.extend(cur.fetchall())
        
        # Fetch Medium
        cur.execute(f"""
            SELECT question_id, topic_id, question_text, option_a, option_b, option_c, option_d, correct_option, difficulty, explanation 
            FROM questions 
            WHERE topic_id IN ({topic_placeholders}) AND difficulty = 'Medium'
            ORDER BY RANDOM() LIMIT %s;
        """, (*topic_ids, n_med))
        quiz_questions.extend(cur.fetchall())

        # Fetch Hard
        cur.execute(f"""
            SELECT question_id, topic_id, question_text, option_a, option_b, option_c, option_d, correct_option, difficulty, explanation 
            FROM questions 
            WHERE topic_id IN ({topic_placeholders}) AND difficulty = 'Hard'
            ORDER BY RANDOM() LIMIT %s;
        """, (*topic_ids, n_hard))
        quiz_questions.extend(cur.fetchall())
        
        cur.close()
        
        # random.shuffle(quiz_questions) # Shuffle the final mix so difficulties aren't clumped
        import random
        random.shuffle(quiz_questions)

        # 4. Render Template
        return render_template('quiz.html', questions=quiz_questions)

    except Exception as e:
        return f"Error generating quiz: {str(e)}", 500

@app.route('/quiz')
def quiz():
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
                             score_percent=int(percentage), 
                             percentage=f"{degree:.1f}", # Passing degrees for CSS
                             feedback_message=msg)
    except Exception as e:
        return f"Error loading result: {str(e)}", 500

@app.route('/api/save-quiz-result', methods=['POST'])
def save_quiz_result():
    from models import User
    
    data = request.json
    user_id = data.get('user_id')
    score = data.get('score')
    total = data.get('total')
    topic_id = data.get('topic_id') # We should pass this from frontend
    
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
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Database insert failed"}), 500
            
    return jsonify({"error": "DB Connection failed"}), 500

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
    if not conn: return jsonify({"error": "DB Connection failed"}), 500
    
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
        
        return jsonify({
            "message": "Login successful!",
            "session": {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": role
                }
            }
        })

    except AuthApiError as e:
        return jsonify({"error": "Invalid email or password."}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Fetches user profile (name, email) from database using Auth token."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 401

    token = auth_header.split(" ")[1] # Bearer <token>

    try:
        # 1. Verify Session with Supabase Auth
        user_response = supabase.auth.get_user(token)
        user_id = user_response.user.id

        # 2. Query 'users' table for profile data
        # Using Supabase client to query the table directly
        data_response = supabase.table('users').select('name, email').eq('user_id', user_id).execute()
        
        if data_response.data and len(data_response.data) > 0:
            user_data = data_response.data[0]
            return jsonify({
                "name": user_data.get('name'),
                "email": user_data.get('email')
            })
        else:
            # Fallback if user record missing in table (shouldn't happen if sync works)
            return jsonify({"error": "User profile not found"}), 404

    except AuthApiError:
         return jsonify({"error": "Invalid or expired token"}), 401
    except Exception as e:
        print(f"Profile Fetch Error: {e}")
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
        # Redirect URL should point to our update-password page
        # Note: In local dev, ensure Supabase allows localhost:5000/update-password
        # Force localhost depending on environment to match common whitelist
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
        return jsonify({"error": str(e) + " (Check server logs for details. Hint: Is the Redirect URL whitelisted in Supabase?)"}), 400

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

if __name__ == '__main__':
    app.run(debug=True)