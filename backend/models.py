
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

    def _load_profile(self):
        """Private method to load basic user info."""
        if not self.conn: return
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT name, email FROM users WHERE user_id = %s", (self.user_id,))
            res = cur.fetchone()
            if res:
                self.name = res['name']
                self.email = res['email']
        except Exception as e:
            print(f"Error loading profile: {e}")
        finally:
            cur.close()

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
                accuracy = (res['total_score'] / res['total_possible'] * 100) if res['total_possible'] > 0 else 0
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
