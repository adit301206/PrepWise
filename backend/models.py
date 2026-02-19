
import pytz
from datetime import timezone

class HistoryStack:
    """
    DSA Implementation: Stack Data Structure for User History.
    Follows LIFO (Last-In, First-Out) principle so the most recent attempts are shown first.
    """
    def __init__(self):
        self.stack = []

    def push(self, item):
        """Push a test record onto the stack."""
        self.stack.append(item)

    def pop_all(self):
        """
        Pop all items from the stack in LIFO order.
        Returns a list where the last pushed item (most recent) is first.
        """
        result = []
        while self.stack:
            result.append(self.stack.pop())
        return result

    def load_history(self, history_data):
        """
        Loads a list of history records into the stack.
        Assumes input data is sorted chronologically (oldest -> newest).
        """
        for record in history_data:
            self.push(record)

class User:
    """
    OOP Implementation: User Class.
    Encapsulates user-related database logic.
    """
    def __init__(self, db_conn, user_id):
        self.conn = db_conn
        self.user_id = user_id
        self.name = None
        self.email = None
        self._load_profile()

    def get_profile_data(self):
        """Explicitly fetches profile data for the API using user_id."""
        if not self.conn: return None
        cur = self.conn.cursor()
        try:
            # STRICTLY use user_id
            cur.execute("SELECT name, email, bio, phone, birthdate, avatar_url FROM users WHERE user_id = %s", (self.user_id,))
            res = cur.fetchone()
            if res:
                return {
                    "name": res['name'],
                    "email": res['email'],
                    "bio": res['bio'],
                    "phone": res['phone'],
                    "birthdate": res['birthdate'], 
                    "avatar_url": res['avatar_url']
                }
            return None
        except Exception as e:
            print(f"Error fetching profile data: {e}")
            return None
        finally:
            cur.close()

    def _load_profile(self):
        """Internal method to load basic info into the object."""
        data = self.get_profile_data()
        if data:
            self.name = data['name']
            self.email = data['email']
            self.bio = data['bio']
            self.phone = data['phone']
            self.birthdate = data['birthdate']
            self.avatar_url = data['avatar_url']

    def update_profile(self, data):
        print(f"DEBUG: update_profile called with: {data}")
        if not self.conn: return False
        
        try:
            cur = self.conn.cursor()
            
            # 1. Check if user exists first
            cur.execute("SELECT user_id FROM users WHERE user_id = %s", (self.user_id,))
            if not cur.fetchone():
                print(f"DEBUG: User {self.user_id} NOT FOUND in DB!")
                return False

            # 2. Prepare SQL
            # Using COALESCE to keep existing values if new ones are None. 
            # Note: We use %s placeholder syntax for psycopg2.
            sql = """
                UPDATE users 
                SET name = COALESCE(%s, name),
                    phone = COALESCE(%s, phone),
                    birthdate = COALESCE(%s, birthdate),
                    bio = COALESCE(%s, bio),
                    avatar_url = COALESCE(%s, avatar_url)
                WHERE user_id = %s
            """
            
            # Helper: Extract values or None. 
            # If a field is NOT in data, we pass None so COALESCE uses DB value.
            # If a field IS in data but empty string, we might want to allow clearing it? 
            # The user requested COALESCE logic which implies "if None, keep old".
            # But earlier we handled empty strings as None.
            # Let's stick to the user's specific request: "Use COALESCE... to only update fields that are present"
            
            name_val = data.get('name')
            phone_val = data.get('phone')
            birthdate_val = data.get('birthdate')
            bio_val = data.get('bio')
            avatar_val = data.get('avatar_url')
            
            # Handle empty strings for Date/optional fields if they come from form as ''
            if birthdate_val == '': birthdate_val = None
            if phone_val == '': phone_val = None
            if bio_val == '': bio_val = None
            if avatar_val == '': avatar_val = None

            params = (name_val, phone_val, birthdate_val, bio_val, avatar_val, self.user_id)
            
            # 3. Execute & Commit
            cur.execute(sql, params)
            self.conn.commit()
            print("DEBUG: SQL Executed and COMMITTED successfully.")
            
            # 4. Verify Update
            if cur.rowcount == 0:
                print("DEBUG: WARNING - 0 rows updated! Check user_id.")
                
            cur.close()
            # self._load_profile() # Reload to keep object in sync - Optional but good practice
            return True
        except Exception as e:
            print(f"DEBUG: Model Error: {e}")
            if self.conn: self.conn.rollback()
            return False

    def get_attempt_history(self):
        query = """
            SELECT a.attempt_id, a.score, a.total_questions, a.percentage, a.attempted_at, t.topic_name
            FROM attempts a
            JOIN topics t ON a.topic_id = t.topic_id
            WHERE a.user_id = %s
            ORDER BY a.attempted_at ASC;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (self.user_id,))
            raw_records = cur.fetchall()

        formatted_history = []
        # Define the timezone
        ist_tz = pytz.timezone('Asia/Kolkata')
        
        for row in raw_records:
            db_time = row['attempted_at']
            
            # 1. Ensure the DB time is treated as UTC
            if db_time.tzinfo is None:
                db_time = db_time.replace(tzinfo=timezone.utc)
                
            # 2. Convert to Indian Standard Time (IST) using pytz
            local_time = db_time.astimezone(ist_tz)
            
            # 3. Format strictly as "13 Feb 2026, 09:26 PM"
            display_date = local_time.strftime("%d %b %Y, %I:%M %p")
            
            formatted_history.append({
                "attempt_id": row['attempt_id'],
                "topic_name": row['topic_name'],
                "score": row['score'],
                "total_questions": row['total_questions'],
                "percentage": row['percentage'],
                "date": display_date  # Passed to the Jinja2 template
            })
            
        return formatted_history

    def get_analytics(self):
        """Returns analytics like average score and accuracy."""
        if not self.conn: return {}
        cur = self.conn.cursor()
        try:
            # Calculate Total Quizzes, Avg Score, and Accuracy
            # Accuracy = (Sum of user's scores / Sum of total possible scores) * 100
            query = """
                SELECT 
                    COUNT(*) as total_quizzes,
                    AVG(percentage) as avg_score,
                    SUM(score) as total_score,
                    SUM(total_questions) as total_possible
                FROM attempts 
                WHERE user_id = %s
            """
            cur.execute(query, (self.user_id,))
            res = cur.fetchone()
            
            if res and res['total_quizzes'] and res['total_quizzes'] > 0:
                total_possible = res['total_possible'] or 0
                total_score = res['total_score'] or 0
                accuracy = (total_score / total_possible * 100) if total_possible > 0 else 0
                return {
                    "total_quizzes": res['total_quizzes'],
                    "avg_score": round(res['avg_score'], 1),
                    "accuracy": round(accuracy, 1)
                }
            else:
                return {
                    "total_quizzes": 0,
                    "avg_score": 0,
                    "accuracy": 0
                }
        except Exception as e:
            print(f"Error analytics: {e}")
            return {"total_quizzes": 0, "avg_score": 0, "accuracy": 0}
        finally:
            cur.close()

    def save_attempt(self, topic_id, score, total_questions):
        """Saves a new test attempt to the database."""
        if not self.conn: return False
        cur = self.conn.cursor()
        try:
            # simple percentage calc
            percentage = (score / total_questions) * 100 if total_questions > 0 else 0
            
            # Insert into attempts
            query = """
                INSERT INTO attempts (user_id, topic_id, score, total_questions, percentage)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING attempt_id;
            """
            cur.execute(query, (self.user_id, topic_id, score, total_questions, percentage))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving result: {e}")
            self.conn.rollback()
            return False
        finally:
            cur.close()

class LeaderboardDSA:
    def __init__(self, db_connection):
        self.conn = db_connection

    def get_top_students(self, limit=5):
        """
        Uses a Min-Heap to efficiently find the top N students by total score.
        Updated to safely handle legacy data.
        """
        import heapq
        
        query = """
            SELECT u.name, u.avatar_url, SUM(COALESCE(a.score, 0)) as total_score, COUNT(a.attempt_id) as quizzes_taken
            FROM users u
            JOIN attempts a ON u.user_id = a.user_id
            WHERE LOWER(u.role) = 'student' OR u.role IS NULL
            GROUP BY u.user_id, u.name, u.avatar_url
            HAVING SUM(COALESCE(a.score, 0)) > 0;
        """
        
        with self.conn.cursor() as cur:
            cur.execute(query)
            students = cur.fetchall()
            
        print(f"DEBUG: Leaderboard fetched {len(students)} raw records from DB.") # Debugging line

        # Min-Heap Implementation
        top_k_heap = []
        
        for student in students:
            score = student['total_score'] or 0
            name = student['name'] or 'Anonymous'
            quizzes = student['quizzes_taken'] or 0
            avatar_url = student['avatar_url']
            
            # Push tuple into heap: (score, name, quizzes, avatar_url)
            heapq.heappush(top_k_heap, (score, name, quizzes, avatar_url))
            
            # If heap grows larger than limit, pop the smallest score
            if len(top_k_heap) > limit:
                heapq.heappop(top_k_heap)
                
        # Sort the top K students descending for the UI
        top_students = sorted(top_k_heap, key=lambda x: x[0], reverse=True)
        
        leaderboard = []
        for rank, (score, name, quizzes, avatar_url) in enumerate(top_students, start=1):
            leaderboard.append({
                "rank": rank,
                "name": name,
                "score": score,
                "quizzes": quizzes,
                "avatar_url": avatar_url,
                "initial": name[0].upper() if name else "U"
            })
            
        return leaderboard
