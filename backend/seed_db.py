import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

def seed_database():
    try:
        print("🌱 Seeding Database...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # 1. Subjects
        subjects = ["Computers", "Mathematics", "Physics", "Chemistry"]
        for sub in subjects:
            cur.execute("INSERT INTO subjects (subject_name) VALUES (%s) ON CONFLICT (subject_name) DO NOTHING;", (sub,))
        print("   ✅ Subjects seeded.")

        # 2. Topics (Map Subject Name -> List of Topics)
        topics_map = {
            "Computers": ["Data Structures", "Algorithms", "Operating Systems", "Networking", "Database Management", "Web Development", "Artificial Intelligence", "Cyber Security"],
            "Mathematics": ["Algebra", "Calculus", "Geometry", "Statistics"],
            "Physics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Optics"],
            "Chemistry": ["Organic", "Inorganic", "Physical", "Biochemistry"]
        }

        for sub_name, topics in topics_map.items():
            # Get subject_id
            cur.execute("SELECT subject_id FROM subjects WHERE subject_name = %s;", (sub_name,))
            res = cur.fetchone()
            if res:
                sub_id = res[0]
                for topic in topics:
                    cur.execute("INSERT INTO topics (topic_name, subject_id) VALUES (%s, %s) ON CONFLICT (topic_name, subject_id) DO NOTHING;", (topic, sub_id))
        
        print("   ✅ Topics seeded.")

        # 3. Comprehensive Sample Questions
        # 3. Comprehensive Sample Questions
        questions_data = [
            # --- COMPUTERS ---
            # Data Structures
            ("Computers", "Data Structures", "Easy", "What is the time complexity of accessing an array element?", "O(1)", "O(n)", "O(log n)", "O(n^2)", "A", "Accessing an array element by index is a direct operation, hence O(1)."),
            ("Computers", "Data Structures", "Medium", "Which data structure follows LIFO?", "Queue", "Stack", "Tree", "Graph", "B", "Stack follows Last-In-First-Out (LIFO)."),
            ("Computers", "Data Structures", "Hard", "What is the worst case search time in a BST?", "O(1)", "O(log n)", "O(n)", "O(n log n)", "C", "In a skewed tree (like a linked list), the height is n, so search is O(n)."),
            ("Computers", "Data Structures", "Easy", "Which data structure is used for recursion?", "Queue", "Stack", "List", "Array", "B", "The system uses a Call Stack to track recursion."),
            ("Computers", "Data Structures", "Medium", "What is the time complexity of inserting into a hash table (average)?", "O(1)", "O(n)", "O(log n)", "O(n^2)", "A", "Hash tables have O(1) average time complexity for insertions."),
            ("Computers", "Data Structures", "Hard", "Which traversal of BFS uses?", "Stack", "Queue", "Priority Queue", "None", "B", "BFS uses a Queue to explore level by level."),

            # Algorithms
            ("Computers", "Algorithms", "Easy", "Which algorithm is used for sorting?", "Bubble Sort", "Binary Search", "DFS", "BFS", "A", "Bubble Sort is a sorting algorithm."),
            ("Computers", "Algorithms", "Medium", "What is the time complexity of Merge Sort?", "O(n)", "O(n^2)", "O(n log n)", "O(log n)", "C", "Merge Sort is consistently O(n log n)."),
            ("Computers", "Algorithms", "Hard", "Dijkstra's algorithm is used for?", "Sorting", "Shortest Path", "MST", "Searching", "B", "Dijkstra finds the shortest path in a graph."),
            ("Computers", "Algorithms", "Easy", "Binary Search works on?", "Sorted Array", "Unsorted Array", "Linked List", "Tree", "A", "Binary Search requires the array to be sorted."),
            ("Computers", "Algorithms", "Medium", "Quick Sort best case complexity?", "O(n log n)", "O(n^2)", "O(n)", "O(log n)", "A", "Best case for Quick Sort is O(n log n)."),
            ("Computers", "Algorithms", "Hard", "Which is a dynamic programming problem?", "Knapsack", "Binary Search", "Merge Sort", "DFS", "A", "The Knapsack problem is a classic DP problem."),

            # Operating Systems
            ("Computers", "Operating Systems", "Easy", "What is the core of the OS called?", "Shell", "Kernel", "CPU", "Memory", "B", "The Kernel is the core component of the OS."),
            ("Computers", "Operating Systems", "Medium", "Which valid state is a process in?", "Running", "Eating", "Sleeping", "Walking", "A", "Processes can be in Running, Ready, or Blocked states."),
            ("Computers", "Operating Systems", "Easy", "Which is not an OS?", "Windows", "Linux", "Oracle", "MacOS", "C", "Oracle is a database company/product, not an OS."),
            ("Computers", "Operating Systems", "Medium", "What is paging?", "Memory Management", "Disk Management", "CPU Scheduling", "Network", "A", "Paging is a memory management scheme."),
            ("Computers", "Operating Systems", "Hard", "What is a deadlock?", "Process waiting indefinitely", "Process terminating", "CPU failure", "Memory leak", "A", "Deadlock occurs when processes wait indefinitely for resources."),

            # Networking
            ("Computers", "Networking", "Easy", "What does HTTP stand for?", "HyperText Transfer Protocol", "High Transfer Text Protocol", "None", "Hyper Transfer", "A", "HTTP stands for HyperText Transfer Protocol."),
            ("Computers", "Networking", "Medium", "Which layer is IP in?", "Network", "Application", "Physical", "Data Link", "A", "IP (Internet Protocol) is in the Network Layer."),
            ("Computers", "Networking", "Easy", "Port 80 is used for?", "HTTP", "FTP", "SSH", "DNS", "A", "Port 80 is the default port for HTTP."),
            ("Computers", "Networking", "Medium", "What is a MAC address?", "Hardware Address", "IP Address", "Port Number", "Socket", "A", "MAC Address is the physical hardware address."),

            # Database Management
            ("Computers", "Database Management", "Easy", "What does SQL stand for?", "Structured Query Language", "Strong Question Language", "Structured Question List", "None", "A", "SQL stands for Structured Query Language."),
            ("Computers", "Database Management", "Medium", "Which is a NoSQL database?", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "C", "MongoDB is a document-oriented NoSQL database."),
            ("Computers", "Database Management", "Hard", "ACID properties stand for?", "Atomicity, Consistency, Isolation, Durability", "Atomicity, Clarity, Isolation, Durability", "None", "All", "A", "ACID ensures reliable database transactions."),
            ("Computers", "Database Management", "Easy", "Primary Key must be?", "Unique", "Null", "Duplicate", "Float", "A", "A Primary Key must be unique and not null."),

            # Web Development
            ("Computers", "Web Development", "Easy", "HTML stands for?", "Hyper Text Markup Language", "Hyperlinks and Text Markup Language", "Home Tool Markup Language", "None", "A", "HTML is Hyper Text Markup Language."),
            ("Computers", "Web Development", "Medium", "Which tag is used for largest heading?", "<h6>", "<h1>", "<head>", "<heading>", "B", "<h1> defines the most important heading."),
            ("Computers", "Web Development", "Easy", "CSS stands for?", "Cascading Style Sheets", "Creative Style System", "Computer Style Sheets", "None", "A", "CSS stands for Cascading Style Sheets."),
            ("Computers", "Web Development", "Hard", "Which is a JS framework?", "Django", "Flask", "React", "Laravel", "C", "React is a JavaScript library/framework for UI."),

            # Artificial Intelligence
            ("Computers", "Artificial Intelligence", "Easy", "Who is the father of AI?", "Alan Turing", "John McCarthy", "Elon Musk", "Bill Gates", "B", "John McCarthy coined the term Artificial Intelligence."),
            ("Computers", "Artificial Intelligence", "Medium", "Which is a type of Machine Learning?", "Supervised", "HTML", "SQL", "Networking", "A", "Supervised Learning is a main type of ML."),
            ("Computers", "Artificial Intelligence", "Hard", "What is a Neural Network modeled after?", "Human Brain", "Computer Chip", "Internet", "Tree", "A", "Neural Networks are inspired by biological neural networks."),
            ("Computers", "Artificial Intelligence", "Easy", "AI stands for?", "Artificial Intelligence", "Auto Interface", "Automated Intelligence", "None", "A", "AI stands for Artificial Intelligence."),

            # Cyber Security
            ("Computers", "Cyber Security", "Easy", "What is Phishing?", "Fraudulent email", "Fishing sport", "Code optimization", "None", "A", "Phishing involves sending fraudulent emails to steal info."),
            ("Computers", "Cyber Security", "Medium", "What does SSL stand for?", "Secure Sockets Layer", "System Sockets Layer", "Super Secure Layer", "None", "A", "SSL stands for Secure Sockets Layer."),
            ("Computers", "Cyber Security", "Hard", "Which is a strong password?", "123456", "password", "MyP@ssw0rd!", "admin", "C", "Strong passwords mix cases, numbers, and symbols."),
            ("Computers", "Cyber Security", "Easy", "Malware is?", "Bad software", "Good software", "Hardware", "None", "A", "Malware (Malicious Software) is designed to cause harm."),

            # --- MATHEMATICS ---
            # Algebra
            ("Mathematics", "Algebra", "Easy", "Solve for x: 2x + 4 = 10", "2", "3", "4", "5", "B", "2x = 6, so x = 3."),
            ("Mathematics", "Algebra", "Medium", "What is the slope of y = 3x + 2?", "2", "3", "x", "3x", "B", "In y=mx+b, m is the slope, which is 3."),
            ("Mathematics", "Algebra", "Easy", "Factor x^2 - 9", "(x-3)(x+3)", "(x-3)(x-3)", "(x+3)(x+3)", "None", "A", "Difference of squares: a^2-b^2 = (a-b)(a+b)."),
            ("Mathematics", "Algebra", "Medium", "Solve x^2 = 16", "4", "-4", "+/- 4", "16", "C", "Square root of 16 is both +4 and -4."),
            ("Mathematics", "Algebra", "Hard", "Log base 2 of 8 is?", "2", "3", "4", "8", "B", "2^3 = 8, so log2(8) = 3."),

            # Calculus
            ("Mathematics", "Calculus", "Hard", "Derivative of sin(x)?", "cos(x)", "-cos(x)", "tan(x)", "sec(x)", "A", "The derivative of sin(x) is cos(x)."),
            ("Mathematics", "Calculus", "Easy", "Derivative of x^2?", "x", "2x", "x^2", "2", "B", "Using power rule: 2 * x^(2-1) = 2x."),
            ("Mathematics", "Calculus", "Medium", "Integral of 2x?", "x^2", "2x^2", "x", "2", "A", "The integral of 2x is x^2 + C."),
            ("Mathematics", "Calculus", "Hard", "Derivative of ln(x)?", "1/x", "e^x", "x", "ln(x)", "A", "The derivative of ln(x) is 1/x."),

            # Geometry
            ("Mathematics", "Geometry", "Easy", "Sum of angles in a triangle?", "180", "360", "90", "270", "A", "The sum of interior angles of a triangle is 180 degrees."),
            ("Mathematics", "Geometry", "Medium", "Area of circle radius r?", "pi*r^2", "2*pi*r", "pi*d", "r^2", "A", "Area = pi * r^2."),
            ("Mathematics", "Geometry", "Easy", "Perimeter of square side a?", "4a", "a^2", "2a", "a", "A", "Perimeter = 4 * side."),
            ("Mathematics", "Geometry", "Medium", "Volume of cube side a?", "a^3", "6a^2", "4a", "a^2", "A", "Volume = side^3."),

            # Statistics
            ("Mathematics", "Statistics", "Medium", "What is the median of [1, 3, 5, 7, 9]?", "3", "5", "7", "9", "B", "5 is the middle number."),
            ("Mathematics", "Statistics", "Easy", "Probability of heads?", "0.5", "1", "0", "0.25", "A", "A fair coin has a 50% chance of heads."),
            ("Mathematics", "Statistics", "Medium", "Mean of 2, 4, 6?", "2", "4", "6", "12", "B", "(2+4+6)/3 = 4."),
            ("Mathematics", "Statistics", "Hard", "Standard deviation measures?", "Spread", "Center", "Max", "Min", "A", "Standard deviation measures the spread of data."),

            # --- PHYSICS ---
            # Mechanics
            ("Physics", "Mechanics", "Easy", "Unit of Force?", "Newton", "Joule", "Watt", "Pascal", "A", "Newton is the SI unit of force."),
            ("Physics", "Mechanics", "Medium", "F = ?", "ma", "mv", "m/a", "mgh", "A", "Newton's Second Law: F = ma."),
            ("Physics", "Mechanics", "Easy", "Gravity on Earth?", "9.8", "10", "9.2", "8.9", "A", "Standard gravity is approx 9.8 m/s^2."),
            ("Physics", "Mechanics", "Hard", "Kinetic Energy formula?", "0.5mv^2", "mgh", "ma", "mv", "A", "KE = 1/2 * m * v^2."),

            # Thermodynamics
            ("Physics", "Thermodynamics", "Medium", "Water boils at?", "90C", "100C", "110C", "120C", "B", "Boiling point of water is 100°C at sea level."),
            ("Physics", "Thermodynamics", "Easy", "What measures temperature?", "Barometer", "Thermometer", "Speedometer", "None", "B", "A thermometer measures temperature."),
            ("Physics", "Thermodynamics", "Hard", "First law is about?", "Energy Conservation", "Entropy", "Heat Flow", "Gravity", "A", "First law states energy is conserved."),
            ("Physics", "Thermodynamics", "Medium", "Freezing point of water?", "0C", "32C", "-10C", "100C", "A", "Water freezes at 0°C."),

            # Electromagnetism
            ("Physics", "Electromagnetism", "Hard", "Who discovered induction?", "Tesla", "Edison", "Faraday", "Ampere", "C", "Faraday discovered electromagnetic induction."),
            ("Physics", "Electromagnetism", "Medium", "Unit of Current?", "Volt", "Ampere", "Ohm", "Watt", "B", "Ampere is the unit of electric current."),
            ("Physics", "Electromagnetism", "Easy", "Opposite poles...?", "Attract", "Repel", "Nothing", "Explode", "A", "Opposite magnetic poles attract."),
            ("Physics", "Electromagnetism", "Hard", "V = IR is whose law?", "Ohm", "Newton", "Faraday", "Tesla", "A", "Ohm's Law: V = IR."),

            # Optics
            ("Physics", "Optics", "Easy", "Speed of light is approx?", "3x10^8 m/s", "3x10^6 m/s", "300 m/s", "Sound speed", "A", "Light travels at approx 300,000 km/s."),
            ("Physics", "Optics", "Medium", "Bending of light is?", "Reflection", "Refraction", "Diffraction", "Interference", "B", "Refraction is the bending of light."),
            ("Physics", "Optics", "Easy", "Mirror reflects?", "Light", "Sound", "Heat", "All", "A", "Mirrors reflect light."),
            ("Physics", "Optics", "Hard", "Rainbow is caused by?", "Dispersion", "Reflection", "Refraction", "Diffraction", "A", "Dispersion splits light into colors."),

            # --- CHEMISTRY ---
            # Organic
            ("Chemistry", "Organic", "Easy", "Methane formula?", "CH4", "C2H6", "CO2", "H2O", "A", "Methane is CH4."),
            ("Chemistry", "Organic", "Medium", "Benzene ring has how many carbons?", "4", "5", "6", "8", "C", "Benzene (C6H6) has 6 carbons."),
            ("Chemistry", "Organic", "Easy", "Simplest Alcohol?", "Methanol", "Ethanol", "Propanol", "Butanol", "A", "Methanol is the simplest alcohol."),
            ("Chemistry", "Organic", "Hard", "Double bond ending?", "-ane", "-ene", "-yne", "-ol", "B", "-ene suffix indicates a double bond."),

            # Inorganic
            ("Chemistry", "Inorganic", "Medium", "Symbol for Gold?", "Ag", "Au", "Fe", "Pb", "B", "Au comes from Aurum (Gold)."),
            ("Chemistry", "Inorganic", "Easy", "Oxygen atomic number?", "6", "7", "8", "9", "C", "Oxygen is number 8."),
            ("Chemistry", "Inorganic", "Medium", "NaCl is?", "Salt", "Sugar", "Acid", "Base", "A", "NaCl is Sodium Chloride (Table Salt)."),
            ("Chemistry", "Inorganic", "Hard", "Noble gas?", "Helium", "Hydrogen", "Oxygen", "Nitrogen", "A", "Helium is a Noble Gas."),

            # Physical
            ("Chemistry", "Physical", "Hard", "pH of pure water?", "5", "6", "7", "8", "C", "Pure water has a neutral pH of 7."),
            ("Chemistry", "Physical", "Medium", "Acid turns litmus?", "Red", "Blue", "Green", "Yellow", "A", "Acids turn blue litmus paper red."),
            ("Chemistry", "Physical", "Easy", "H2O is?", "Water", "Acid", "Base", "Gas", "A", "H2O is Water."),
            ("Chemistry", "Physical", "Hard", "Avogadro's number", "6.022x10^23", "3.14", "9.8", "100", "A", "Avogadro's number is 6.022 x 10^23."),

            # Biochemistry
            ("Chemistry", "Biochemistry", "Medium", "Building block of protein?", "Sugar", "Fat", "Amino Acid", "DNA", "C", "Amino acids are the building blocks of proteins."),
            ("Chemistry", "Biochemistry", "Easy", "DNA shape?", "Line", "Double Helix", "Circle", "Square", "B", "DNA forms a Double Helix structure."),
            ("Chemistry", "Biochemistry", "Hard", "Energy currency of cell?", "ATP", "DNA", "RNA", "Glucose", "A", "ATP is the energy currency."),
            ("Chemistry", "Biochemistry", "Medium", "Enzymes are?", "Proteins", "Fats", "Carbs", "Minerals", "A", "Enzymes are biological catalysts, mostly proteins.")
        ]


        print("   ⏳ Inserting questions...")
        print("   ⏳ Inserting questions...")
        for subject, topic, difficulty, q_text, op_a, op_b, op_c, op_d, correct, explanation in questions_data:
            # Get topic_id
            cur.execute("""
                SELECT t.topic_id 
                FROM topics t 
                JOIN subjects s ON t.subject_id = s.subject_id 
                WHERE s.subject_name = %s AND t.topic_name = %s;
            """, (subject, topic))
            
            res = cur.fetchone()
            if res:
                topic_id = res[0]
                cur.execute("""
                     INSERT INTO questions (topic_id, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                     ON CONFLICT (topic_id, question_text) DO UPDATE 
                     SET explanation = EXCLUDED.explanation;
                 """, (topic_id, difficulty, q_text, op_a, op_b, op_c, op_d, correct, explanation))
        
        print(f"   ✅ {len(questions_data)} Questions processed.")

        conn.commit()
        cur.close()
        conn.close()
        print("\n✨ DATABASE SEEDED SUCCESSFULLY! ✨")

    except Exception as e:
        print("\n❌ Error Seeding Tables:")
        print(e)

if __name__ == "__main__":
    seed_database()
