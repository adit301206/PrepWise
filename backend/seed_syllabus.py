
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

SYLLABUS = {
    "subject": "Python Programming",
    "units": [
        {
            "name": "Unit 1: Python Basics",
            "questions": [
                {
                    "text": "What is the correct extension for a Python file?",
                    "a": ".python", "b": ".pl", "c": ".py", "d": ".p",
                    "correct": "c", "difficulty": "Easy",
                    "explanation": "Python files always use the .py extension."
                },
                {
                    "text": "Which method is used to remove whitespace from the beginning and end of a string?",
                    "a": "trim()", "b": "strip()", "c": "len()", "d": "ptrim()",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "The strip() method removes leading and trailing whitespaces."
                },
                {
                    "text": "Which operator is used for exponentiation in Python?",
                    "a": "^", "b": "**", "c": "exp()", "d": "//",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "** is the exponentiation operator (e.g., 2**3 = 8)."
                },
                {
                    "text": "What is the output of print(10 // 3)?",
                    "a": "3.33", "b": "3", "c": "3.0", "d": "1",
                    "correct": "b", "difficulty": "Medium",
                    "explanation": "The // operator performs floor division, returning the integer part."
                },
                {
                    "text": "Which of these is NOT a valid variable name?",
                    "a": "my_var", "b": "_myvar", "c": "2myvar", "d": "myVar2",
                    "correct": "c", "difficulty": "Easy",
                    "explanation": "Variable names cannot start with a number."
                }
            ]
        },
        {
            "name": "Unit 2: Control Flow",
            "questions": [
                {
                    "text": "Which keyword is used to stop a loop immediately?",
                    "a": "stop", "b": "break", "c": "exit", "d": "continue",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "The 'break' keyword halts loop execution immediately."
                },
                {
                    "text": "What does the 'continue' keyword do?",
                    "a": "Stops the loop", "b": "Restarts the loop", "c": "Skips the current iteration", "d": "Exits the program",
                    "correct": "c", "difficulty": "Medium",
                    "explanation": "Continue skips the code remaining in the current iteration and jumps to the next one."
                },
                {
                    "text": "How do you write an inline if-statement (Ternary Operator)?",
                    "a": "if x > 5 then y", "b": "x > 5 ? y : z", "c": "y iff x > 5", "d": "y if x > 5 else z",
                    "correct": "d", "difficulty": "Medium",
                    "explanation": "Python uses 'value_if_true if condition else value_if_false'."
                },
                {
                    "text": "What is the output of range(3)?",
                    "a": "[1, 2, 3]", "b": "[0, 1, 2]", "c": "[0, 1, 2, 3]", "d": "(0, 1, 2)",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "range(n) starts at 0 and goes up to n-1."
                },
                {
                    "text": "Which loop is best when we know the number of iterations?",
                    "a": "while", "b": "for", "c": "do-while", "d": "until",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "For loops are optimized for iterating over sequences of known length."
                }
            ]
        },
        {
            "name": "Unit 3: Functions",
            "questions": [
                {
                    "text": "Which keyword creates a function?",
                    "a": "func", "b": "def", "c": "function", "d": "create",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "Functions are defined using the 'def' keyword."
                },
                {
                    "text": "What is a recursive function?",
                    "a": "A function that calls itself", "b": "A function inside a class", "c": "A function that returns nothing", "d": "A lambda function",
                    "correct": "a", "difficulty": "Medium",
                    "explanation": "Recursion occurs when a function calls itself to solve a smaller instance of the problem."
                },
                {
                    "text": "What does *args allow in a function definition?",
                    "a": "Keyword arguments", "b": "Variable number of positional arguments", "c": "Default arguments", "d": "Type hinting",
                    "correct": "b", "difficulty": "Hard",
                    "explanation": "*args collects extra positional arguments into a tuple."
                },
                {
                    "text": "What is a lambda function?",
                    "a": "A named function", "b": "An anonymous single-line function", "c": "A loop function", "d": "A module",
                    "correct": "b", "difficulty": "Medium",
                    "explanation": "Lambda creates small, anonymous functions using the syntax 'lambda args: expression'."
                },
                {
                    "text": "What is the default return value of a function that returns nothing?",
                    "a": "0", "b": "False", "c": "None", "d": "Null",
                    "correct": "c", "difficulty": "Easy",
                    "explanation": "If no return statement is executed, Python returns None."
                }
            ]
        },
        {
            "name": "Unit 4: Data Structures",
            "questions": [
                {
                    "text": "Which collection is ordered, changeable, and allows duplicates?",
                    "a": "Tuple", "b": "Set", "c": "Dictionary", "d": "List",
                    "correct": "d", "difficulty": "Easy",
                    "explanation": "Lists are mutable sequences that maintain order and allow duplicates."
                },
                {
                    "text": "Which collection is unordered and has no duplicate members?",
                    "a": "List", "b": "Tuple", "c": "Set", "d": "Dictionary",
                    "correct": "c", "difficulty": "Medium",
                    "explanation": "Sets are unordered collections of unique elements."
                },
                {
                    "text": "How do you access the value of key 'k' in dictionary 'd'?",
                    "a": "d.get('k')", "b": "d['k']", "c": "Both A and B", "d": "d('k')",
                    "correct": "c", "difficulty": "Easy",
                    "explanation": "Both d['k'] and d.get('k') retrieve values, though get() is safer if the key is missing."
                },
                {
                    "text": "Are tuples mutable?",
                    "a": "Yes", "b": "No", "c": "Only if they contain lists", "d": "Sometimes",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "Tuples are immutable; once created, they cannot be changed."
                },
                {
                    "text": "What is the time complexity to lookup an item in a Dictionary?",
                    "a": "O(n)", "b": "O(log n)", "c": "O(1)", "d": "O(n^2)",
                    "correct": "c", "difficulty": "Hard",
                    "explanation": "Dictionaries use hash tables, providing O(1) average time complexity for lookups."
                }
            ]
        },
        {
            "name": "Unit 5: File Handling",
            "questions": [
                {
                    "text": "Which mode opens a file for writing, creating it if it doesn't exist?",
                    "a": "'r'", "b": "'w'", "c": "'a'", "d": "'x'",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "'w' opens for writing. 'a' appends. 'x' creates but fails if exists."
                },
                {
                    "text": "Ideally, how should we open files to ensure they close automatically?",
                    "a": "open()", "b": "try-finally", "c": "with open() as f:", "d": "file.open()",
                    "correct": "c", "difficulty": "Medium",
                    "explanation": "The 'with' statement creates a context manager that automatically closes the file."
                },
                {
                    "text": "What does readlines() return?",
                    "a": "A string", "b": "A list of strings", "c": "A dictionary", "d": "None",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "readlines() returns a list where each element is a line from the file."
                },
                {
                    "text": "Which method is used to write a string to a file?",
                    "a": "print()", "b": "write()", "c": "insert()", "d": "add()",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "file.write(str) writes the string to the file."
                },
                {
                    "text": "What happens if you open a non-existent file in 'r' mode?",
                    "a": "Creates new file", "b": "Returns None", "c": "FileNotFoundError", "d": "Opens empty buffer",
                    "correct": "c", "difficulty": "Medium",
                    "explanation": "Read mode expects the file to exist; otherwise, it raises an error."
                }
            ]
        },
        {
            "name": "Unit 8-9: OOP & Inheritance",
            "questions": [
                {
                    "text": "Which keyword is used to create a class?",
                    "a": "object", "b": "class", "c": "struct", "d": "def",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "The 'class' keyword defines a new class."
                },
                {
                    "text": "What is '__init__'?",
                    "a": "A constructor method", "b": "A destructor", "c": "A static method", "d": "A module",
                    "correct": "a", "difficulty": "Medium",
                    "explanation": "__init__ is the initializer method (constructor) called when creating an object."
                },
                {
                    "text": "What represents the instance of the class?",
                    "a": "this", "b": "self", "c": "init", "d": "me",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "In Python, 'self' refers to the current instance of the class."
                },
                {
                    "text": "What is Inheritance?",
                    "a": "Classes having same methods", "b": "Class deriving properties from another class", "c": "Hiding data", "d": "Overloading operators",
                    "correct": "b", "difficulty": "Medium",
                    "explanation": "Inheritance allows a child class to acquire properties and methods from a parent class."
                },
                {
                    "text": "Which function checks if an object is an instance of a class?",
                    "a": "check()", "b": "isinstance()", "c": "type()", "d": "typeof()",
                    "correct": "b", "difficulty": "Medium",
                    "explanation": "isinstance(obj, Class) returns True if obj is an instance of Class."
                }
            ]
        },
        {
            "name": "DSA Basics",
            "questions": [
                {
                    "text": "A Stack follows which principle?",
                    "a": "FIFO", "b": "LIFO", "c": "FILO", "d": "LILO",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "Stack is Last-In, First-Out (LIFO)."
                },
                {
                    "text": "A Queue follows which principle?",
                    "a": "FIFO", "b": "LIFO", "c": "FILO", "d": "Random",
                    "correct": "a", "difficulty": "Easy",
                    "explanation": "Queue is First-In, First-Out (FIFO)."
                },
                {
                    "text": "What is the worst-case complexity of Bubble Sort?",
                    "a": "O(n)", "b": "O(n log n)", "c": "O(n^2)", "d": "O(1)",
                    "correct": "c", "difficulty": "Medium",
                    "explanation": "Bubble sort has nested loops, leading to quadratic time complexity O(n^2)."
                },
                {
                    "text": "Which data structure uses keys and values?",
                    "a": "Array", "b": "Hash Table / Dictionary", "c": "Linked List", "d": "Stack",
                    "correct": "b", "difficulty": "Easy",
                    "explanation": "Hash Tables (Dictionaries in Python) map keys to values."
                },
                {
                    "text": "In a Linked List, what does each node contain?",
                    "a": "Only Data", "b": "Data and a Reference (Link) to next node", "c": "Index and Value", "d": "None",
                    "correct": "b", "difficulty": "Medium",
                    "explanation": "A Node contains the data payload and a pointer/reference to the next node."
                }
            ]
        }
    ]
}

def seed():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print("\n🌱 SYLLABUS SEEDING STARTED...")
    
    try:
        # 1. Ensure Subject exists
        cur.execute("INSERT INTO subjects (subject_name) VALUES (%s) ON CONFLICT (subject_name) DO NOTHING RETURNING subject_id;", (SYLLABUS['subject'],))
        res = cur.fetchone()
        
        if res:
            subject_id = res[0]
        else:
            cur.execute("SELECT subject_id FROM subjects WHERE subject_name = %s;", (SYLLABUS['subject'],))
            subject_id = cur.fetchone()[0]
            
        print(f"📘 Subject: {SYLLABUS['subject']} (ID: {subject_id})")

        total_q = 0
        
        # 2. Loop Units
        for unit in SYLLABUS['units']:
            # Create Topic
            cur.execute("""
                INSERT INTO topics (topic_name, subject_id) 
                VALUES (%s, %s) 
                ON CONFLICT (topic_name, subject_id) DO NOTHING 
                RETURNING topic_id;
            """, (unit['name'], subject_id))
            
            res_topic = cur.fetchone()
            if res_topic:
                topic_id = res_topic[0]
            else:
                cur.execute("SELECT topic_id FROM topics WHERE topic_name = %s AND subject_id = %s;", (unit['name'], subject_id))
                topic_id = cur.fetchone()[0]

            print(f"   📂 Topic: {unit['name']}")

            # 3. Create Questions
            for q in unit['questions']:
                cur.execute("""
                    INSERT INTO questions (topic_id, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (topic_id, question_text) DO NOTHING;
                """, (topic_id, q['difficulty'], q['text'], q['a'], q['b'], q['c'], q['d'], q['correct'], q['explanation']))
                total_q += 1

        conn.commit()
        print(f"\n✅ SUCCESSFULLY SEEDED ~{total_q} questions across {len(SYLLABUS['units'])} units.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed()
