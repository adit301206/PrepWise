import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

def seed_extra_questions():
    try:
        print("🌱 Seeding Extra Questions...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Format: (Subject, Topic, Difficulty, Question, A, B, C, D, Correct, Explanation)
        extra_questions = [
            # --- COMPUTERS ---
            # Data Structures (10 questions)
            ("Computers", "Data Structures", "Easy", "Arrays are stored in?", "Contiguous memory", "Non-contiguous memory", "Random memory", "None", "A", "Arrays require contiguous memory allocation."),
            ("Computers", "Data Structures", "Medium", "Which data structure is best for a priority queue?", "Stack", "Linked List", "Heap", "Array", "C", "A Heap is the standard implementation for priority queues."),
            ("Computers", "Data Structures", "Hard", "Time complexity of searching in a Hash Map (Worst Case)?", "O(1)", "O(n)", "O(log n)", "O(n^2)", "B", "Worst case is O(n) when hash collisions occur."),
            ("Computers", "Data Structures", "Easy", "What is a node with no children called?", "Parent", "Root", "Leaf", "Sibling", "C", "A leaf node has no children."),
            ("Computers", "Data Structures", "Medium", "Circular queue avoids?", "Underflow", "Overflow", "Memory wastage", "None", "C", "Circular queues utilize the empty space at the beginning."),
            ("Computers", "Data Structures", "Hard", "AVL trees are?", "Self-balancing", "Unbalanced", "Heaps", "Graphs", "A", "AVL trees are self-balancing Binary Search Trees."),
            ("Computers", "Data Structures", "Easy", "Which DS uses pointers?", "Array", "Linked List", "Stack (Arr)", "Queue (Arr)", "B", "Linked Lists use pointers to connect nodes."),
            ("Computers", "Data Structures", "Medium", "Stack overflow occurs when?", "Stack is empty", "Stack is full", "Heap is full", "None", "B", "Pushing to a full stack causes overflow."),
            ("Computers", "Data Structures", "Hard", "Minimum edges in a connected graph with n nodes?", "n", "n-1", "n+1", "n/2", "B", "A tree (minimally connected graph) has n-1 edges."),
            ("Computers", "Data Structures", "Easy", "Queue follows?", "LIFO", "FIFO", "LILO", "None", "B", "Queue is First-In-First-Out."),
            ("Computers", "Data Structures", "Medium", "Inorder traversal of BST gives?", "Sorted sequence", "Reverse sorted", "Random", "Level order", "A", "Inorder traversal of a BST yields sorted values."),

            # Algorithms (10 questions)
            ("Computers", "Algorithms", "Easy", "Worst case complexity of Bubble Sort?", "O(n)", "O(n log n)", "O(n^2)", "O(log n)", "C", "Bubble sort is O(n^2) in the worst case."),
            ("Computers", "Algorithms", "Medium", "DFS uses which data structure?", "Queue", "Stack", "Heap", "Tree", "B", "DFS uses a Stack (recursion or explicit)."),
            ("Computers", "Algorithms", "Hard", "Floyd-Warshall algorithm computes?", "MST", "All-pairs shortest path", "Single-source shortest path", "Sorting", "B", "Floyd-Warshall finds shortest paths between all pairs."),
            ("Computers", "Algorithms", "Easy", "Big O notation describes?", "Best case", "Average case", "Upper bound", "Lower bound", "C", "Big O represents the upper bound of complexity."),
            ("Computers", "Algorithms", "Medium", "Binary search requires?", "Linear access", "Random access", "Hashing", "Pointers", "B", "Binary search needs random access (like arrays)."),
            ("Computers", "Algorithms", "Hard", "Kruskal's algorithm finds?", "Shortest Path", "MST", "Longest Path", "Flow", "B", "Kruskal's is for Minimum Spanning Tree."),
            ("Computers", "Algorithms", "Easy", "Linear Search complexity?", "O(1)", "O(n)", "O(log n)", "O(n^2)", "B", "Linear search checks each element once: O(n)."),
            ("Computers", "Algorithms", "Medium", "Selection Sort stability?", "Stable", "Unstable", "Both", "None", "B", "Selection sort is generally unstable."),
            ("Computers", "Algorithms", "Hard", "Strassen’s algorithm is for?", "Sorting", "Matrix Multiplication", "Searching", "Graph", "B", "Strassen's algorithm multiplies matrices faster."),
            ("Computers", "Algorithms", "Easy", "Greedy algorithms make?", "Global optimal choice", "Local optimal choice", "Random choice", "None", "B", "Greedy algorithms choose the local optimum at each step."),

            # Operating Systems (10 questions)
            ("Computers", "Operating Systems", "Easy", "Linux is?", "Open source", "Proprietary", "Paid", "None", "A", "Linux is open-source software."),
            ("Computers", "Operating Systems", "Medium", "Context switching happens in?", "User mode", "Kernel mode", "Disk", "Monitor", "B", "Context switching is a kernel operation."),
            ("Computers", "Operating Systems", "Hard", "Banker's algorithm avoids?", "Deadlock", "Starvation", "Crash", "Fragmentation", "A", "Banker's algorithm is for deadlock avoidance."),
            ("Computers", "Operating Systems", "Easy", "GUI stands for?", "Graphical User Interface", "Global User Interface", "General User Interface", "None", "A", "Graphical User Interface."),
            ("Computers", "Operating Systems", "Medium", "Virtual memory uses?", "SRAM", "DRAM", "Disk space", "ROM", "C", "Virtual memory extends RAM using disk space."),
            ("Computers", "Operating Systems", "Hard", "Thrashing occurs when?", "CPU is idle", "Page fault rate is high", "Disk is full", "RAM is full", "B", "Thrashing is excessive paging."),
            ("Computers", "Operating Systems", "Easy", "Which is a valid file extension?", ".exe", ".os", ".cpu", ".ram", "A", ".exe is an executable file."),
            ("Computers", "Operating Systems", "Medium", "Semaphore is a?", "Variable", "Hardware", "Function", "Thread", "A", "A semaphore is an integer variable for sync."),
            ("Computers", "Operating Systems", "Hard", "Round Robin is?", "Preemptive", "Non-preemptive", "Random", "None", "A", "Round Robin is a preemptive scheduling algorithm."),
            ("Computers", "Operating Systems", "Medium", "Bootstrap program is stored in?", "RAM", "ROM", "Disk", "Cache", "B", "BIOS/Bootstrap is stored in ROM."),

            # Networking (10 questions)
            ("Computers", "Networking", "Easy", "IPv4 address length?", "32 bit", "64 bit", "128 bit", "16 bit", "A", "IPv4 addresses are 32 bits long."),
            ("Computers", "Networking", "Medium", "DNS translates?", "IP to MAC", "URL to IP", "MAC to IP", "None", "B", "DNS translates domain names (URL) to IP addresses."),
            ("Computers", "Networking", "Hard", "OSI model has how many layers?", "5", "6", "7", "4", "C", "The OSI model has 7 layers."),
            ("Computers", "Networking", "Easy", "WWW stands for?", "World Wide Web", "World Web Wide", "Web World Wide", "None", "A", "World Wide Web."),
            ("Computers", "Networking", "Medium", "TCP is?", "Connectionless", "Connection-oriented", "Unreliable", "None", "B", "TCP establishes a connection before sending data."),
            ("Computers", "Networking", "Hard", "Which protocol sends email?", "FTP", "MTP", "SMTP", "HTTP", "C", "SMTP (Simple Mail Transfer Protocol)."),
            ("Computers", "Networking", "Easy", "Which device connects networks?", "Hub", "Switch", "Router", "Cable", "C", "Routers connect different networks."),
            ("Computers", "Networking", "Medium", "UDP is preferred for?", "File transfer", "Streaming", "Email", "Banking", "B", "UDP is faster and used for streaming."),
            ("Computers", "Networking", "Hard", "Ping uses which protocol?", "TCP", "UDP", "ICMP", "ARP", "C", "Ping uses ICMP (Internet Control Message Protocol)."),
            ("Computers", "Networking", "Easy", "LAN stands for?", "Local Area Network", "Long Area Network", "Live Area Network", "None", "A", "Local Area Network."),

            # Database Management (10 questions)
            ("Computers", "Database Management", "Easy", "Rows in a table are called?", "Attributes", "Tuples", "Fields", "Columns", "B", "Rows are referred to as tuples or records."),
            ("Computers", "Database Management", "Medium", "Normalization reduces?", "Security", "Redundancy", "Performance", "Tables", "B", "Normalization organizes data to reduce redundancy."),
            ("Computers", "Database Management", "Hard", "Which form eliminates multivalued dependencies?", "1NF", "2NF", "3NF", "4NF", "D", "4NF handles multivalued dependencies."),
            ("Computers", "Database Management", "Easy", "A column is a?", "Tuple", "Attribute", "Record", "File", "B", "Columns are attributes of the data."),
            ("Computers", "Database Management", "Medium", "Foreign Key links to?", "Primary Key", "Unique Key", "Check", "Null", "A", "Foreign keys reference Primary keys in another table."),
            ("Computers", "Database Management", "Hard", "Which is a DDL command?", "SELECT", "INSERT", "CREATE", "UPDATE", "C", "CREATE is a Data Definition Language command."),
            ("Computers", "Database Management", "Easy", "DBA stands for?", "Data Base Access", "Data Base Administrator", "Data Bus Allocator", "None", "B", "Data Base Administrator."),
            ("Computers", "Database Management", "Medium", "View is a?", "Virtual Table", "Physical Table", "Index", "Key", "A", "A view is a virtual table based on a query."),
            ("Computers", "Database Management", "Hard", "B-Trees are used for?", "Sorting", "Indexing", "Hashing", "Encryption", "B", "B-Trees are widely used for database indexing."),
            ("Computers", "Database Management", "Easy", "Unique Key allows nulls?", "Yes (one)", "No", "Yes (many)", "None", "A", "Standard SQL allows one NULL in a Unique column."),

            # Web Development (10 questions)
            ("Computers", "Web Development", "Easy", "Correct HTML tag for newline?", "<br>", "<lb>", "<break>", "<n>", "A", "<br> introduces a line break."),
            ("Computers", "Web Development", "Medium", "Which is not a semantic tag?", "<div>", "<article>", "<section>", "<footer>", "A", "<div> has no semantic meaning."),
            ("Computers", "Web Development", "Hard", "GET vs POST: Which is safer?", "GET", "POST", "Both", "Neither", "B", "POST sends data in the body, not URL, so it's safer."),
            ("Computers", "Web Development", "Easy", "CSS id selector uses?", ".", "#", "@", "*", "B", "IDs are selected with #."),
            ("Computers", "Web Development", "Medium", "DOM stands for?", "Document Object Model", "Data Object Model", "Disk Object Model", "None", "A", "Document Object Model."),
            ("Computers", "Web Development", "Hard", "React uses which DOM?", "Real DOM", "Virtual DOM", "Shadow DOM", "Phantom DOM", "B", "React uses a Virtual DOM for performance."),
            ("Computers", "Web Development", "Easy", "Which runs in browser?", "Python", "PHP", "JavaScript", "Java", "C", "JavaScript runs natively in browsers."),
            ("Computers", "Web Development", "Medium", "Bootstrap is a?", "CSS Framework", "JS Library", "Database", "OS", "A", "Bootstrap is a front-end CSS framework."),
            ("Computers", "Web Development", "Hard", "Explain 'hoisting' in JS?", "Looping", "Moving declarations up", "Linking", "Parsing", "B", "Declarations are moved to the top of scope."),
            ("Computers", "Web Development", "Medium", "AJAX stands for?", "Asynchronous JS and XML", "All JS and XML", "Advanced JS and XML", "None", "A", "Asynchronous JavaScript and XML."),

            # Artificial Intelligence (10 questions)
            ("Computers", "Artificial Intelligence", "Easy", "Robot brain is?", "Sensor", "Actuator", "Controller", "Wire", "C", "The controller acts as the brain."),
            ("Computers", "Artificial Intelligence", "Medium", "Turing Test checks?", "Intelligence", "Speed", "Memory", "Power", "A", "Turing Test evaluates machine intelligence."),
            ("Computers", "Artificial Intelligence", "Hard", "Which search is uninformed?", "A*", "Best-First", "BFS", "Heuristic", "C", "BFS is an uninformed (blind) search."),
            ("Computers", "Artificial Intelligence", "Easy", "NLP stands for?", "Natural Language Processing", "Next Level Programming", "New Language Process", "None", "A", "Natural Language Processing."),
            ("Computers", "Artificial Intelligence", "Medium", "Genetic Algorithms are inspired by?", "Physics", "Evolution", "Chemistry", "Math", "B", "Inspired by biological evolution."),
            ("Computers", "Artificial Intelligence", "Hard", "Deep Learning uses?", "Single layer", "Multi-layer neural nets", "Trees", "Graphs", "B", "Deep learning uses multi-layered (deep) neural networks."),
            ("Computers", "Artificial Intelligence", "Easy", "A chatbot is an?", "AI Agent", "Virus", "Hardware", "OS", "A", "Chatbots are AI agents."),
            ("Computers", "Artificial Intelligence", "Medium", "Which logic uses 0 and 1?", "Fuzzy", "Boolean", "Crisp", "Probabilistic", "B", "Boolean logic uses True(1) and False(0)."),
            ("Computers", "Artificial Intelligence", "Hard", "AlphaGo plays?", "Chess", "Go", "Poker", "Dota", "B", "AlphaGo is famous for playing the game Go."),
            ("Computers", "Artificial Intelligence", "Medium", "A heuristic is a?", "Rule of thumb", "Guaranteed solution", "Algorithm", "Loop", "A", "Heuristics are mental shortcuts or rules of thumb."),

            # Cyber Security (10 questions)
            ("Computers", "Cyber Security", "Easy", "Antivirus detects?", "Hardware", "Malware", "User", "Network", "B", "Antivirus software detects malware."),
            ("Computers", "Cyber Security", "Medium", "DDoS stands for?", "Distributed Denial of Service", "Direct Denial of Service", "Data Denial of Service", "None", "A", "Distributed Denial of Service."),
            ("Computers", "Cyber Security", "Hard", "Which is an encryption algorithm?", "AES", "HTTP", "FTP", "SQL", "A", "AES (Advanced Encryption Standard)."),
            ("Computers", "Cyber Security", "Easy", "Firewall protects?", "Network", "Monitor", "Keyboard", "Mouse", "A", "Firewalls filter network traffic."),
            ("Computers", "Cyber Security", "Medium", "Spyware steals?", "Hardware", "Data", "Electricity", "WiFi", "B", "Spyware is designed to steal user data."),
            ("Computers", "Cyber Security", "Hard", "Man-in-the-Middle is a?", "Attack", "Software", "Hardware", "Protocol", "A", "MitM is an active eavesdropping attack."),
            ("Computers", "Cyber Security", "Easy", "Spam is?", "Junk email", "Virus", "Hacker", "Code", "A", "Unsolicited junk email."),
            ("Computers", "Cyber Security", "Medium", "VPN hides?", "IP Address", "MAC Address", "Screen", "Keyboard", "A", "VPNs mask your IP address."),
            ("Computers", "Cyber Security", "Hard", "Ransomware demands?", "Payment", "Password", "Email", "Update", "A", "Ransomware encrypts data and demands payment."),
            ("Computers", "Cyber Security", "Medium", "2FA stands for?", "2 Factor Authentication", "2 Fast Auth", "2 Form Access", "None", "A", "Two-Factor Authentication."),

            # --- MATHEMATICS ---
            # Algebra (10 questions)
            ("Mathematics", "Algebra", "Easy", "Simplify 2(x+3)", "2x+3", "2x+6", "x+6", "2x+5", "B", "Distribute the 2: 2*x + 2*3 = 2x+6."),
            ("Mathematics", "Algebra", "Medium", "Roots of x^2 - 5x + 6 = 0?", "2, 3", "1, 6", "-2, -3", "2, -3", "A", "(x-2)(x-3)=0."),
            ("Mathematics", "Algebra", "Hard", "Discriminant of ax^2+bx+c?", "b^2-4ac", "b^2+4ac", "4ac-b^2", "a^2-4bc", "A", "Discriminant is b^2 - 4ac."),
            ("Mathematics", "Algebra", "Easy", "If x=5, x^2?", "10", "25", "5", "2.5", "B", "5 squared is 25."),
            ("Mathematics", "Algebra", "Medium", "Equation of line with slope 2 thru (0,0)?", "y=2x", "y=x+2", "y=x/2", "y=2", "A", "y = mx + b -> y = 2x + 0."),
            ("Mathematics", "Algebra", "Hard", "Inverse of f(x)=x+1?", "x-1", "x+1", "1-x", "1/x", "A", "y=x+1 -> x=y-1 -> f-1(x)=x-1."),
            ("Mathematics", "Algebra", "Easy", "3x = 12, x=?", "3", "4", "36", "9", "B", "x = 12/3 = 4."),
            ("Mathematics", "Algebra", "Medium", "Expand (a+b)^2", "a^2+b^2", "a^2+2ab+b^2", "a^2+ab+b^2", "2a+2b", "B", "Standard expansion."),
            ("Mathematics", "Algebra", "Hard", "Sum of roots of 2x^2 - 8x + 1 = 0", "4", "-4", "2", "8", "A", "Sum is -b/a = -(-8)/2 = 4."),
            ("Mathematics", "Algebra", "Medium", "Value of i^2?", "1", "-1", "0", "i", "B", "i is sqrt(-1), so i^2 is -1."),

            # Calculus (10 questions)
            ("Mathematics", "Calculus", "Easy", "Derivative of constant?", "0", "1", "x", "Undefined", "A", "Rate of change of a constant is 0."),
            ("Mathematics", "Calculus", "Medium", "Integral of 1/x?", "ln(x)", "x", "e^x", "-1/x^2", "A", "Integral of 1/x is ln|x|."),
            ("Mathematics", "Calculus", "Hard", "Chain rule applies to?", "Composite functions", "Product", "Sum", "Quotient", "A", "Chain rule is for f(g(x))."),
            ("Mathematics", "Calculus", "Easy", "Limit x->0 of 1/x?", "Infinity", "0", "1", "Undefined", "D", "Undefined (approaches +/- int)."),
            ("Mathematics", "Calculus", "Medium", "Derivative of e^x?", "e^x", "xe^x", "1", "0", "A", "Derivative of e^x is itself."),
            ("Mathematics", "Calculus", "Hard", "Integration by parts formula?", "uv-int(vdu)", "uv+int(vdu)", "u+v", "udv", "A", "Integral udv = uv - Integral vdu."),
            ("Mathematics", "Calculus", "Easy", "Slope of tangent is?", "Derivative", "Integral", "Limit", "Area", "A", "Derivative represents the slope."),
            ("Mathematics", "Calculus", "Medium", "Second derivative test finds?", "Concavity", "Root", "Limit", "Slope", "A", "Used for max/min and concavity."),
            ("Mathematics", "Calculus", "Hard", "Taylor series of e^x at 0?", "1+x+x^2/2!...", "1-x+x^2...", "x-x^3/3!...", "None", "A", "Sum x^n/n!."),
            ("Mathematics", "Calculus", "Medium", "Area under curve is?", "Integral", "Derivative", "Slope", "Limit", "A", "Definite integral calculates area."),

            # Geometry (10 questions)
            ("Mathematics", "Geometry", "Easy", "Angles in right triangle?", "90, 45, 45 (iso)", "90, 60, 60", "90, 90, 0", "None", "A", "One angle is always 90."),
            ("Mathematics", "Geometry", "Medium", "Volume of sphere?", "4/3 pi r^3", "pi r^2", "2 pi r", "4 pi r^2", "A", "4/3 pi r^3."),
            ("Mathematics", "Geometry", "Hard", "Euler's formula for polyhedra?", "V-E+F=2", "V+E-F=2", "V-E-F=2", "V+E+F=2", "A", "Vertices - Edges + Faces = 2."),
            ("Mathematics", "Geometry", "Easy", "Sides in a pentagon?", "5", "6", "4", "8", "A", "Penta means 5."),
            ("Mathematics", "Geometry", "Medium", "Pythagoras theorem?", "a^2+b^2=c^2", "a+b=c", "a^2-b^2=c^2", "None", "A", "For right triangles."),
            ("Mathematics", "Geometry", "Hard", "Distance between (x1,y1) & (x2,y2)?", "sqrt((x2-x1)^2+(y2-y1)^2)", "x1+x2", "y1+y2", "None", "A", "Distance formula."),
            ("Mathematics", "Geometry", "Easy", "Complementary angles sum to?", "90", "180", "360", "45", "A", "Complementary sum to 90."),
            ("Mathematics", "Geometry", "Medium", "Area of triangle?", "0.5*b*h", "b*h", "l*w", "s^2", "A", "1/2 base * height."),
            ("Mathematics", "Geometry", "Hard", "Equation of circle radius r?", "x^2+y^2=r^2", "x+y=r", "y=x^2", "x^2-y^2=r", "A", "Centered at origin."),
            ("Mathematics", "Geometry", "Medium", "Sum of exterior angles?", "360", "180", "720", "90", "A", "Always 360 for convex polygons."),

            # Statistics (10 questions)
            ("Mathematics", "Statistics", "Easy", "Mode is?", "Most frequent", "Average", "Middle", "Largest", "A", "Mode is the most frequent value."),
            ("Mathematics", "Statistics", "Medium", "Range is?", "Max - Min", "Max + Min", "Mean", "Median", "A", "Difference between highest and lowest."),
            ("Mathematics", "Statistics", "Hard", "Variance is?", "Std Dev squared", "Mean squared", "Root of Mean", "None", "A", "Variance is the square of standard deviation."),
            ("Mathematics", "Statistics", "Easy", "Total probability sums to?", "1", "100", "0", "0.5", "A", "Probabilities sum to 1."),
            ("Mathematics", "Statistics", "Medium", "Event A and B independent if?", "P(AB)=P(A)P(B)", "P(A)=P(B)", "P(A+B)=1", "None", "A", "Joint probability is product of individual ones."),
            ("Mathematics", "Statistics", "Hard", "Normal distribution shape?", "Bell curve", "Linear", "Exponential", "Flat", "A", "Symmetric bell-shaped curve."),
            ("Mathematics", "Statistics", "Easy", "Data type of 'Red, Blue'?", "Categorical", "Numerical", "Ordinal", "Binary", "A", "Qualitative data."),
            ("Mathematics", "Statistics", "Medium", "Z-score measures?", "Std deviations from mean", "Error", "Variance", "Probability", "A", "Standardized score."),
            ("Mathematics", "Statistics", "Hard", "Correlation of 1 means?", "Perfect positive", "No correlation", "Negative", "Random", "A", "Perfect positive linear relationship."),
            ("Mathematics", "Statistics", "Medium", "Outlier is?", "Extreme value", "Average", "Error", "Missing", "A", "Value significantly different from others."),

            # --- PHYSICS ---
            # Mechanics (10 questions)
            ("Physics", "Mechanics", "Easy", "SI unit of mass?", "Kilogram", "Gram", "Pound", "Ton", "A", "kg is the SI unit."),
            ("Physics", "Mechanics", "Medium", "Momentum formula?", "p=mv", "p=ma", "p=m/v", "p=vt", "A", "Momentum = mass * velocity."),
            ("Physics", "Mechanics", "Hard", "Escape velocity of Earth?", "11.2 km/s", "5 km/s", "20 km/s", "9.8 km/s", "A", "Minimum speed to escape gravity."),
            ("Physics", "Mechanics", "Easy", "Friction opposes?", "Motion", "Gravity", "Heat", "Light", "A", "Friction acts against direction of motion."),
            ("Physics", "Mechanics", "Medium", "Work done is?", "Force * Distance", "Force / Time", "Mass * Gravity", "None", "A", "W = Fd cos(theta)."),
            ("Physics", "Mechanics", "Hard", "Kepler's laws describe?", "Planetary motion", "Gravity", "Electricity", "Light", "A", "Orbits of planets."),
            ("Physics", "Mechanics", "Easy", "Weight depends on?", "Gravity", "Speed", "Color", "Time", "A", "Weight = mass * gravity."),
            ("Physics", "Mechanics", "Medium", "Power is?", "Work/Time", "Work*Time", "Force*Time", "Energy", "A", "Rate of doing work."),
            ("Physics", "Mechanics", "Hard", "Hooke's Law?", "F = -kx", "F = ma", "E = mc^2", "V = IR", "A", "For springs."),
            ("Physics", "Mechanics", "Medium", "Inertia depends on?", "Mass", "Velocity", "Shape", "Size", "A", "More mass = more inertia."),

            # Thermodynamics (10 questions)
            ("Physics", "Thermodynamics", "Easy", "Heat flows from?", "Hot to Cold", "Cold to Hot", "Low to High", "None", "A", "Nature seeks equilibrium."),
            ("Physics", "Thermodynamics", "Medium", "Adiabatic process means?", "No heat exchange", "Constant Temp", "Constant Pressure", "Constant Volume", "A", "Q = 0."),
            ("Physics", "Thermodynamics", "Hard", "Entropy of universe helps?", "Increase", "Decrease", "Stay same", "Fluctuate", "A", "Second law: Entropy increases."),
            ("Physics", "Thermodynamics", "Easy", "Absolute Zero in Kelvin?", "0 K", "273 K", "-273 K", "100 K", "A", "0 K is absolute zero."),
            ("Physics", "Thermodynamics", "Medium", "Specific heat capacity?", "Heat to raise 1kg by 1K", "Total heat", "Latent heat", "None", "A", "Definition of specific heat."),
            ("Physics", "Thermodynamics", "Hard", "Carnot engine efficiency?", "1 - Tc/Th", "Tc/Th", "1 + Tc/Th", "Th - Tc", "A", "Ideal efficiency."),
            ("Physics", "Thermodynamics", "Easy", "Conduction needs?", "Medium", "Vacuum", "Light", "Waves", "A", "Direct contact needed."),
            ("Physics", "Thermodynamics", "Medium", "Radiation needs?", "No medium", "Air", "Water", "Solids", "A", "Can travel through vacuum."),
            ("Physics", "Thermodynamics", "Hard", "Isobaric process?", "Constant Pressure", "Constant Temp", "Constant Volume", "No Heat", "A", "Baric refers to pressure."),
            ("Physics", "Thermodynamics", "Medium", "Latent heat is for?", "Phase change", "Temp change", "Pressure change", "None", "A", "Heat absorbed/released during phase change."),

            # Electromagnetism (10 questions)
            ("Physics", "Electromagnetism", "Easy", "Charge of electron?", "Negative", "Positive", "Neutral", "None", "A", "Electrons are negative."),
            ("Physics", "Electromagnetism", "Medium", "Capacitor stores?", "Charge", "Current", "Heat", "Magnetic field", "A", "Stores energy in electric field."),
            ("Physics", "Electromagnetism", "Hard", "Maxwell's equations count?", "4", "3", "2", "5", "A", "There are 4 fundamental equations."),
            ("Physics", "Electromagnetism", "Easy", "Good conductor?", "Copper", "Rubber", "Glass", "Wood", "A", "Copper involves free electrons."),
            ("Physics", "Electromagnetism", "Medium", "Tesla is unit of?", "Magnetic Field", "Current", "Flux", "Inductance", "A", "Unit of B-field."),
            ("Physics", "Electromagnetism", "Hard", "Lenz's Law is about?", "Induced Current direction", "Force", "Charge", "Voltage", "A", "Conservation of energy in induction."),
            ("Physics", "Electromagnetism", "Easy", "Like charges?", "Repel", "Attract", "Mix", "None", "A", "Repulsion."),
            ("Physics", "Electromagnetism", "Medium", "Transformer works on?", "AC", "DC", "Both", "None", "A", "Requires changing magnetic field."),
            ("Physics", "Electromagnetism", "Hard", "Lorentz Force?", "F = q(E + v x B)", "F = ma", "F = qE", "F = ILB", "A", "Force on charge in E and B fields."),
            ("Physics", "Electromagnetism", "Medium", "Resistance depends on?", "Length & Area", "Color", "Time", "Voltage", "A", "R = rho * L / A."),

            # Optics (10 questions)
            ("Physics", "Optics", "Easy", "Light is a?", "Wave & Particle", "Gas", "Liquid", "Solid", "A", "Wave-particle duality."),
            ("Physics", "Optics", "Medium", "Concave lens is?", "Diverging", "Converging", "Flat", "None", "A", "Spreads light out."),
            ("Physics", "Optics", "Hard", "Total Internal Reflection needs?", "Dense to Rare medium", "Rare to Dense", "Same medium", "Vacuum", "A", "Angle > Critical angle."),
            ("Physics", "Optics", "Easy", "Sky is blue due to?", "Scattering", "Reflection", "Refraction", "Diffraction", "A", "Rayleigh scattering."),
            ("Physics", "Optics", "Medium", "Power of lens unit?", "Diopter", "Meter", "Watt", "Second", "A", "P = 1/f."),
            ("Physics", "Optics", "Hard", "Young's Double Slit showed?", "Interference", "Particle nature", "Reflection", "Gravity", "A", "Prove wave nature."),
            ("Physics", "Optics", "Easy", "Convex mirror image?", "Virtual & Diminished", "Real", "Inverted", "Large", "A", "Side mirrors are convex."),
            ("Physics", "Optics", "Medium", "Snell's law?", "n1 sin1 = n2 sin2", "V=IR", "F=ma", "E=mc2", "A", "Law of refraction."),
            ("Physics", "Optics", "Hard", "Polarization proves?", "Transverse nature", "Longitudinal", "Particle", "Speed", "A", "Only transverse waves polarize."),
            ("Physics", "Optics", "Medium", "Myopia is?", "Nearsightedness", "Farsightedness", "Blindness", "None", "A", "Can see near, not far."),

            # --- CHEMISTRY ---
            # Organic (10 questions)
            ("Chemistry", "Organic", "Easy", "Carbon valency?", "4", "2", "6", "8", "A", "Carbon forms 4 bonds."),
            ("Chemistry", "Organic", "Medium", "Isomers have same?", "Formula", "Structure", "Shape", "Name", "A", "Same molecular formula, different structure."),
            ("Chemistry", "Organic", "Hard", "Main component of Natural Gas?", "Methane", "Ethane", "Propane", "Butane", "A", "Mostly CH4."),
            ("Chemistry", "Organic", "Easy", "Saturated hydrocarbon?", "Alkane", "Alkene", "Alkyne", "Benzene", "A", "Single bonds only."),
            ("Chemistry", "Organic", "Medium", "Functional group -OH?", "Alcohol", "Acid", "Ketone", "Amine", "A", "Hydroxyl group."),
            ("Chemistry", "Organic", "Hard", "Ester smells like?", "Fruity", "Rotten", "Fishy", "Sharp", "A", "Esters are sweet/fruity."),
            ("Chemistry", "Organic", "Easy", "Polymer of ethene?", "Polythene", "PVC", "Nylon", "Rubber", "A", "Polyethylene."),
            ("Chemistry", "Organic", "Medium", "Vinegar contains?", "Acetic Acid", "Citric Acid", "Sulfuric", "Nitric", "A", "Dilute acetic acid."),
            ("Chemistry", "Organic", "Hard", "Benzene hybridization?", "sp2", "sp3", "sp", "sp3d", "A", "Planar ring structure."),
            ("Chemistry", "Organic", "Medium", "Acetone is a?", "Ketone", "Alcohol", "Aldehyde", "Ester", "A", "Simplest ketone."),

            # Inorganic (10 questions)
            ("Chemistry", "Inorganic", "Easy", "Symbol for Iron?", "Fe", "Ir", "In", "F", "A", "Ferrum."),
            ("Chemistry", "Inorganic", "Medium", "Brass is alloy of?", "Cu + Zn", "Cu + Sn", "Fe + C", "Au + Ag", "A", "Copper and Zinc."),
            ("Chemistry", "Inorganic", "Hard", "Most electronegative element?", "Fluorine", "Oxygen", "Chlorine", "Neon", "A", "Top right of periodic table."),
            ("Chemistry", "Inorganic", "Easy", "Periodic table arranged by?", "Atomic Number", "Mass", "Date", "Size", "A", "Moseley's law."),
            ("Chemistry", "Inorganic", "Medium", "Ammonia formula?", "NH3", "NH4", "NO2", "N2", "A", "NH3."),
            ("Chemistry", "Inorganic", "Hard", "Coordination number of NaCl?", "6:6", "4:4", "8:8", "1:1", "A", "Face centered cubic."),
            ("Chemistry", "Inorganic", "Easy", "Diamond is made of?", "Carbon", "Glass", "Gold", "Silica", "A", "Allotrope of carbon."),
            ("Chemistry", "Inorganic", "Medium", "Bauxite is ore of?", "Aluminium", "Iron", "Copper", "Zinc", "A", "Al source."),
            ("Chemistry", "Inorganic", "Hard", "Ozone formula?", "O3", "O2", "O", "O4", "A", "Trioxygen."),
            ("Chemistry", "Inorganic", "Medium", "Hardest substance?", "Diamond", "Steel", "Graphite", "Iron", "A", "Natural hardness."),

            # Physical (10 questions)
            ("Chemistry", "Physical", "Easy", "SI unit of Temp?", "Kelvin", "Celsius", "Fahrenheit", "Rankine", "A", "Kelvin."),
            ("Chemistry", "Physical", "Medium", "Boyle's Law relates?", "P and V", "V and T", "P and T", "V and n", "A", "Inverse relationship."),
            ("Chemistry", "Physical", "Hard", "Order of reaction depends on?", "Experiment", "Coefficients", "Equation", "None", "A", "Must be determined experimentally."),
            ("Chemistry", "Physical", "Easy", "Electron charge?", "-1.6e-19 C", "1 C", "0", "10 C", "A", "Elementary charge."),
            ("Chemistry", "Physical", "Medium", "Catalyst changes?", "Rate", "Equilibrium", "Product", "Reactant", "A", "Speeds up reaction without being consumed."),
            ("Chemistry", "Physical", "Hard", "Gibbs free energy for spontaneous?", "Negative", "Positive", "Zero", "None", "A", "Delta G < 0."),
            ("Chemistry", "Physical", "Easy", "Gas to Liquid is?", "Condensation", "Evaporation", "Sublimation", "Freezing", "A", "Phase change."),
            ("Chemistry", "Physical", "Medium", "Ideal Gas equation?", "PV=nRT", "P=mq", "V=IR", "F=ma", "A", "Standard equation."),
            ("Chemistry", "Physical", "Hard", "Hess's Law relates to?", "Enthalpy", "Entropy", "Speed", "Mass", "A", "State function additivity."),
            ("Chemistry", "Physical", "Medium", "Molarity is?", "Moles/Liter", "Moles/Kg", "Grams/Liter", "None", "A", "Concentration."),

            # Biochemistry (10 questions)
            ("Chemistry", "Biochemistry", "Easy", "Source of Vitamin C?", "Citrus", "Meat", "Bread", "Oil", "A", "Lemons, oranges."),
            ("Chemistry", "Biochemistry", "Medium", "Which sugar in milk?", "Lactose", "Sucrose", "Glucose", "Fructose", "A", "Milk sugar."),
            ("Chemistry", "Biochemistry", "Hard", "Lock and Key model is for?", "Enzymes", "DNA", "Cells", "Fats", "A", "Enzyme specificity."),
            ("Chemistry", "Biochemistry", "Easy", "Human body mostly?", "Water", "Carbon", "Bone", "Iron", "A", "~60% water."),
            ("Chemistry", "Biochemistry", "Medium", "Insulin regulates?", "Blood Sugar", "Heart", "Lungs", "Brain", "A", "Glucose levels."),
            ("Chemistry", "Biochemistry", "Hard", "ATP produced in?", "Mitochondria", "Nucleus", "Ribosome", "Golgi", "A", "Powerhouse of cell."),
            ("Chemistry", "Biochemistry", "Easy", "Proteins are made of?", "Amino Acids", "Sugars", "Fats", "Salts", "A", "Polypeptide chains."),
            ("Chemistry", "Biochemistry", "Medium", "Fat soluble vitamin?", "A", "C", "B", "None", "A", "A, D, E, K."),
            ("Chemistry", "Biochemistry", "Hard", "Base pair A goes with?", "T", "G", "C", "U", "A", "Adenine-Thymine."),
            ("Chemistry", "Biochemistry", "Medium", "Hemoglobin carries?", "Oxygen", "Water", "Food", "Waste", "A", "In red blood cells.")
        ]

        print(f"   ⏳ Inserting {len(extra_questions)} questions...")
        
        for subject, topic, difficulty, q_text, op_a, op_b, op_c, op_d, correct, explanation in extra_questions:
            # Get topic_id (must exist from initial seed)
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
            else:
                print(f"   ⚠️ Topic not found: {subject} -> {topic}")
        
        print(f"   ✅ Processed {len(extra_questions)} extra questions.")

        conn.commit()
        cur.close()
        conn.close()
        print("\n✨ EXTRA QUESTIONS SEEDED SUCCESSFULLY! ✨")

    except Exception as e:
        print("\n❌ Error Seeding Extra Questions:")
        print(e)

if __name__ == "__main__":
    seed_extra_questions()
