
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
        """Fetches all past test attempts for this user."""
        if not self.conn: return []
        cur = self.conn.cursor()
        try:
            # Fetch ordered by creation time (Oldest -> Newest) so Stack can reverse it properly
            # We JOIN topics to get topic_name. 
            # Note: attempts now has topic_id directly.
            query = """
                SELECT 
                    a.attempt_id,
                    t.topic_name,
                    a.score,
                    a.total_questions,
                    a.percentage,
                    to_char(a.attempted_at, 'YYYY-MM-DD HH24:MI') as date
                FROM attempts a
                LEFT JOIN topics t ON a.topic_id = t.topic_id
                WHERE a.user_id = %s
                ORDER BY a.attempted_at ASC
            """
            cur.execute(query, (self.user_id,))
            return cur.fetchall()
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
        finally:
            cur.close()

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
