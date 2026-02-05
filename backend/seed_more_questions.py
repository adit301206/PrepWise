import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

def seed_more_questions():
    try:
        print("🌱 Seeding Even More Questions (Batch 2)...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Format: (Subject, Topic, Difficulty, Question, A, B, C, D, Correct, Explanation)
        more_questions = [
            # --- COMPUTERS ---
            # Data Structures
            ("Computers", "Data Structures", "Hard", "Red-Black Tree height is?", "O(log n)", "O(n)", "O(1)", "O(n^2)", "A", "Red-Black trees are balanced BSTs."),
            ("Computers", "Data Structures", "Medium", "Deque stands for?", "Double Ended Queue", "Dual Entry Queue", "Direct Entry Queue", "None", "A", "Allows insertion/deletion at both ends."),
            ("Computers", "Data Structures", "Easy", "Max number of children in binary tree?", "2", "3", "1", "Unlimited", "A", "Binary means at most 2."),
            ("Computers", "Data Structures", "Hard", "Trie is used for?", "String searching", "Sorting", "Graph", "Matrix", "A", "Efficient for prefix based search."),
            ("Computers", "Data Structures", "Medium", "Bloom filter gives?", "False positives", "False negatives", "Exact match", "None", "A", "Probabilistic data structure."),
            ("Computers", "Data Structures", "Easy", "In LIFO, element inserted last is?", "First out", "Last out", "Middle", "None", "A", "Last In First Out."),
            ("Computers", "Data Structures", "Hard", "Time complexity of Skip List search?", "O(log n)", "O(n)", "O(1)", "O(n^2)", "A", "Skip lists offer O(log n) expected time."),
            ("Computers", "Data Structures", "Medium", "Graph traversal without recursion?", "BFS", "DFS (Stack)", "Both", "None", "C", "Both can be iterative."),
            ("Computers", "Data Structures", "Easy", "Array index starts at?", "0", "1", "-1", "None", "A", "0-indexed in most languages."),
            ("Computers", "Data Structures", "Hard", "Disjoint Set Union (DSU) operations?", "Find & Union", "Push & Pop", "Insert & Delete", "None", "A", "Used for set merging."),

            # Algorithms
            ("Computers", "Algorithms", "Medium", "Huffman coding is?", "Greedy", "Dynamic", "Divide & Conquer", "Backtracking", "A", "Greedy approach for compression."),
            ("Computers", "Algorithms", "Easy", "GCD(8, 12)?", "4", "2", "8", "6", "A", "Highest common factor is 4."),
            ("Computers", "Algorithms", "Hard", "Bellman-Ford handles?", "Negative weights", "Only positive", "Cycles", "None", "A", "Can handle negative edge weights."),
            ("Computers", "Algorithms", "Medium", "Rabin-Karp is for?", "Pattern matching", "Sorting", "Graph", "Tree", "A", "String searching algorithm."),
            ("Computers", "Algorithms", "Easy", "Fibonacci(0)?", "0", "1", "2", "None", "A", "Base case is 0."),
            ("Computers", "Algorithms", "Hard", "Traveling Salesman Problem is?", "NP-Hard", "P", "Linear", "O(1)", "A", "computationally hard."),
            ("Computers", "Algorithms", "Medium", "Master Theorem solves?", "Recurrences", "Sorting", "Graphs", "None", "A", "Analyzes divide and conquer."),
            ("Computers", "Algorithms", "Easy", "Factorial of 3?", "6", "3", "9", "2", "A", "3*2*1=6."),
            ("Computers", "Algorithms", "Hard", "Topological sort works on?", "DAG", "Cyclic Graph", "Tree", "Any Graph", "A", "DAG: Directed Acyclic Graph."),
            ("Computers", "Algorithms", "Medium", "KMP Algorithm complexity?", "O(n)", "O(n^2)", "O(log n)", "O(1)", "A", "Linear time pattern matching."),

            # Operating Systems
            ("Computers", "Operating Systems", "Easy", "Ctrl+C does what?", "Interrupt", "Paste", "Copy", "Cut", "A", "Sends SIGINT."),
            ("Computers", "Operating Systems", "Medium", "Race condition occurs in?", "Concurrency", "Sequential", "Single thread", "None", "A", "Concurrent access to shared resources."),
            ("Computers", "Operating Systems", "Hard", "Dining Philosophers is a?", "Synchronization problem", "Algorithm", "Virus", "Game", "A", "Classic synchronization problem."),
            ("Computers", "Operating Systems", "Easy", "RAM is?", "Volatile", "Non-volatile", "Permanent", "Slow", "A", "Loses data without power."),
            ("Computers", "Operating Systems", "Medium", "SPOOLing stands for?", "Simultaneous Peripheral Operations On-Line", "System P", "Simple P", "None", "A", "Mainly for printers."),
            ("Computers", "Operating Systems", "Hard", "Belady's Anomaly affects?", "FIFO", "LRU", "Optimal", "LFU", "A", "More frames -> more page faults."),
            ("Computers", "Operating Systems", "Easy", "BIOS is?", "Basic Input Output System", "Basic In Out", "Binary OS", "None", "A", "Firmware."),
            ("Computers", "Operating Systems", "Medium", "Mutex is?", "Lock", "Key", "User", "Process", "A", "Mutual Exclusion object."),
            ("Computers", "Operating Systems", "Hard", "Zombie process is?", "Dead but in table", "Running", "Sleeping", "Virus", "A", "Finished execution but parent hasn't waited."),
            ("Computers", "Operating Systems", "Medium", "Command interpreter is?", "Shell", "Kernel", "Bus", "Port", "A", "Interprets user commands."),

            # Networking
            ("Computers", "Networking", "Easy", "WiFi stands for?", "Wireless Fidelity", "Wireless Fiber", "Wire Fine", "None", "A", "Marketing term."),
            ("Computers", "Networking", "Medium", "DHCP gives?", "Dynamic IP", "Static IP", "MAC", "DNS", "A", "Dynamic Host Configuration Protocol."),
            ("Computers", "Networking", "Hard", "Subnet mask 255.255.255.0 is?", "/24", "/16", "/8", "/32", "A", "24 bits for network."),
            ("Computers", "Networking", "Easy", "Google is a?", "Search Engine", "Browser", "OS", "Protocol", "A", "Search engine."),
            ("Computers", "Networking", "Medium", "FTP port?", "21", "80", "443", "25", "A", "Standard FTP control port."),
            ("Computers", "Networking", "Hard", "OSPF is?", "Link State Protocol", "Distance Vector", "Path Vector", "None", "A", "Open Shortest Path First."),
            ("Computers", "Networking", "Easy", "URL stands for?", "Uniform Resource Locator", "Universal R L", "United R L", "None", "A", "Web address."),
            ("Computers", "Networking", "Medium", "NAT stands for?", "Network Address Translation", "New Add Trans", "Net Alloc Table", "None", "A", "Maps private to public IP."),
            ("Computers", "Networking", "Hard", "Three way handshake uses?", "SYN, SYN-ACK, ACK", "ACK, SYN, FIN", "RST, PSH, URG", "None", "A", "TCP connection establishment."),
            ("Computers", "Networking", "Easy", "Bluetooth is?", "PAN", "LAN", "WAN", "MAN", "A", "Personal Area Network."),

            # Database Management
            ("Computers", "Database Management", "Easy", "DB stands for?", "Database", "Data Bus", "Data Bank", "None", "A", "Database."),
            ("Computers", "Database Management", "Medium", "JOIN combines?", "Tables", "Rows like Union", "Columns randomly", "None", "A", "Combines based on related column."),
            ("Computers", "Database Management", "Hard", "CAP theorem stands for?", "Consistency, Availability, Partition tolerance", "C, A, Performance", "C, Accuracy, P", "None", "A", "Distributed systems trade-offs."),
            ("Computers", "Database Management", "Easy", "SELECT * means?", "Select All", "Select One", "Select None", "Delete", "A", "Select all columns."),
            ("Computers", "Database Management", "Medium", "Stored Procedure is?", "Code in DB", "External code", "Table", "View", "A", "Precompiled SQL code."),
            ("Computers", "Database Management", "Hard", "Sharding is?", "Horizontal partitioning", "Vertical", "Replication", "Backup", "A", "Splitting data across servers."),
            ("Computers", "Database Management", "Easy", "CSV stands for?", "Comma Separated Values", "Common S V", "Computer S V", "None", "A", "Data format."),
            ("Computers", "Database Management", "Medium", "Trigger runs?", "Automatically", "Manually", "Never", "Randomly", "A", "On specific DB events."),
            ("Computers", "Database Management", "Hard", "WAL stands for?", "Write Ahead Logging", "Write After Log", "Web App Log", "None", "A", "For atomicity and durability."),
            ("Computers", "Database Management", "Easy", "Maximum rows in table?", "Depends on storage", "100", "1 million", "Unlimited", "A", "Limited by disk/system."),

            # Web Development
            ("Computers", "Web Development", "Easy", "JS is compiled?", "No, Interpreted", "Yes", "Maybe", "Partially", "A", "Generally JIT compiled/interpreted."),
            ("Computers", "Web Development", "Medium", "REST stands for?", "Representational State Transfer", "Real State T", "Random S T", "None", "A", "API architecture."),
            ("Computers", "Web Development", "Hard", "CORS stands for?", "Cross-Origin Resource Sharing", "Cross Origin R S", "Code Origin R S", "None", "A", "Browser security feature."),
            ("Computers", "Web Development", "Easy", "Tag for image?", "<img>", "<image>", "<pic>", "<i>", "A", "Image tag."),
            ("Computers", "Web Development", "Medium", "JSON stands for?", "JavaScript Object Notation", "Java S O N", "JS On Net", "None", "A", "Data interchange format."),
            ("Computers", "Web Development", "Hard", "WebSockets are?", "Bidirectional", "Unidirectional", "Stateless", "Slow", "A", "Full-duplex communication."),
            ("Computers", "Web Development", "Easy", "CSS class selector?", ".", "#", "$", "*", "A", "Dot notation."),
            ("Computers", "Web Development", "Medium", "Cookie is stored in?", "Browser", "Server", "Cloud", "None", "A", "Client-side storage."),
            ("Computers", "Web Development", "Hard", "GraphQL is?", "Query Language", "Database", "Framework", "OS", "A", "Alternative to REST."),
            ("Computers", "Web Development", "Easy", "Tag for link?", "<a>", "<link>", "<href>", "<url>", "A", "Anchor tag."),

            # Artificial Intelligence
            ("Computers", "Artificial Intelligence", "Easy", "Siri is?", "AI Assistant", "Robot", "Car", "None", "A", "Apple's assistant."),
            ("Computers", "Artificial Intelligence", "Medium", "Supervised Learning needs?", "adfaLbeled Data", "Unlabeled Data", "No Data", "Random Data", "A", "Input-output pairs."),
            ("Computers", "Artificial Intelligence", "Hard", "Backpropagation updates?", "Weights", "Inputs", "Outputs", "Layers", "A", "Minimizes error."),
            ("Computers", "Artificial Intelligence", "Easy", "Neural Net node is called?", "Neuron", "Cell", "Point", "Dot", "A", "Inspired by brain."),
            ("Computers", "Artificial Intelligence", "Medium", "Overfitting means?", "Model learns noise", "Model is perfect", "Model is simple", "None", "A", "Poor generalization."),
            ("Computers", "Artificial Intelligence", "Hard", "GAN stands for?", "Generative Adversarial Network", "Graph A N", "General A N", "None", "A", "Two nets competing."),
            ("Computers", "Artificial Intelligence", "Easy", "Tesla Autopilot is?", "AI", "Magic", "Manual", "None", "A", "Uses AI/Computer Vision."),
            ("Computers", "Artificial Intelligence", "Medium", "Support Vector Machine is?", "Classifier", "Robot", "Network", "Hardware", "A", "ML algorithm."),
            ("Computers", "Artificial Intelligence", "Hard", "Reinforcement Learning key?", "Reward/Penalty", "Labels", "Clusters", "Regression", "A", "Learning from environment."),
            ("Computers", "Artificial Intelligence", "Medium", "Clustering is?", "Unsupervised", "Supervised", "Rule based", "None", "A", "Grouping data."),

            # Cyber Security
            ("Computers", "Cyber Security", "Easy", "Hacker is?", "Someone who breaks info systems", "Cook", "Driver", "None", "A", "General term."),
            ("Computers", "Cyber Security", "Medium", "Salting prevents?", "Rainbow Table attacks", "Brute force", "Phishing", "None", "A", "Adds random data to hash."),
            ("Computers", "Cyber Security", "Hard", "Zero-day exploit is?", "Unknown vulnerability", "Old bug", "Fixed bug", "None", "A", "No patch available yet."),
            ("Computers", "Cyber Security", "Easy", "Lock icon in browser?", "SSL/TLS secure", "Locked site", "Broken", "None", "A", "HTTPS connection."),
            ("Computers", "Cyber Security", "Medium", "Keylogger records?", "Keystrokes", "Screen", "Audio", "Video", "A", "Spyware."),
            ("Computers", "Cyber Security", "Hard", "Penetration testing is?", "Ethical Hacking", "Bad Hacking", "Building PC", "None", "A", "Testing security."),
            ("Computers", "Cyber Security", "Easy", "Backup prevents?", "Data Loss", "Virus", "Hacking", "Spam", "A", "Recovery method."),
            ("Computers", "Cyber Security", "Medium", "Social Engineering is?", "Manipulating people", "Coding", "Network design", "None", "A", "Human hacking."),
            ("Computers", "Cyber Security", "Hard", "Worr (Write Once Read Many)?", "Blockchain/Storage", "RAM", "CPU", "None", "A", "Immutability."),
            ("Computers", "Cyber Security", "Medium", "Botnet is?", "Network of infected PCs", "Robot network", "Good net", "None", "A", "Used for DDoS etc."),

            # --- MATHEMATICS ---
            # Algebra
            ("Mathematics", "Algebra", "Easy", "5 + (-3)?", "2", "8", "-2", "15", "A", "2."),
            ("Mathematics", "Algebra", "Medium", "Slope of horizontal line?", "0", "1", "Undefined", "Infinite", "A", "y = c."),
            ("Mathematics", "Algebra", "Hard", "Log(1)?", "0", "1", "10", "Undefined", "A", "Any base log(1)=0."),
            ("Mathematics", "Algebra", "Easy", "Which is even?", "4", "3", "1", "5", "A", "Divisible by 2."),
            ("Mathematics", "Algebra", "Medium", "Vertex of y=x^2?", "(0,0)", "(1,1)", "(-1,-1)", "(0,1)", "A", "Origin."),
            ("Mathematics", "Algebra", "Hard", "Matrix determinant of identity?", "1", "0", "n", "-1", "A", "Det(I) = 1."),
            ("Mathematics", "Algebra", "Easy", "x/0 is?", "Undefined", "0", "1", "x", "A", "Cannot divide by zero."),
            ("Mathematics", "Algebra", "Medium", "G.P. series ratio?", "Common Ratio", "Difference", "Sum", "Mean", "A", "Geometric Progression."),
            ("Mathematics", "Algebra", "Hard", "Eigenvalues belong to?", "Matrices", "Polynomials", "Circles", "None", "A", "Linear algebra."),
            ("Mathematics", "Algebra", "Medium", "Real numbers include?", "Rationals & Irrationals", "Only Integers", "Only Fractions", "None", "A", "All points on line."),

            # Calculus
            ("Mathematics", "Calculus", "Easy", "Integral of 0?", "Constant", "0", "x", "1", "A", "C."),
            ("Mathematics", "Calculus", "Medium", "L'Hopital's Rule for?", "0/0 limits", "Products", "Sums", "None", "A", "Indeterminate forms."),
            ("Mathematics", "Calculus", "Hard", "Gradient vector points to?", "Max increase", "Min increase", "Zero", "Level", "A", "Steepest ascent."),
            ("Mathematics", "Calculus", "Easy", "Derivative of x?", "1", "x", "0", "2", "A", "Linear slope."),
            ("Mathematics", "Calculus", "Medium", "Critical point when?", "Derivative is 0 or undefined", "Integral 0", "X is 0", "None", "A", "Max/Min candidates."),
            ("Mathematics", "Calculus", "Hard", "Laplace transform of 1?", "1/s", "s", "1", "0", "A", "Standard transform."),
            ("Mathematics", "Calculus", "Easy", "dy/dx is?", "Derivative", "Fraction", "Integral", "Limit", "A", "Leibniz notation."),
            ("Mathematics", "Calculus", "Medium", "Inflection point?", "Concavity changes", "Slope 0", "Max", "Min", "A", "Second derivative."),
            ("Mathematics", "Calculus", "Hard", "Divergence of curl?", "0", "1", "Vector", "Goes to infinity", "A", "Vector identity."),
            ("Mathematics", "Calculus", "Medium", "Product rule?", "udv + vdu", "udv - vdu", "uv", "u/v", "A", "(uv)' = u'v + uv'."),

            # Geometry
            ("Mathematics", "Geometry", "Easy", "Circle degrees?", "360", "180", "90", "100", "A", "Full rotation."),
            ("Mathematics", "Geometry", "Medium", "Equilateral triangle angle?", "60", "45", "90", "30", "A", "All equal."),
            ("Mathematics", "Geometry", "Hard", "Area of Ellipse?", "pi*a*b", "pi*r^2", "a*b", "2pi*a", "A", "a and b are semi-axes."),
            ("Mathematics", "Geometry", "Easy", "Shape with 6 sides?", "Hexagon", "Pentagon", "Octagon", "Square", "A", "Hexa = 6."),
            ("Mathematics", "Geometry", "Medium", "Chord vs Diameter?", "Diameter is longest chord", "Chord is longer", "Same", "No relation", "A", "Diameter passes center."),
            ("Mathematics", "Geometry", "Hard", "Topology studies?", "Properties preserved under shrinking/stretching", "Angles", "Lengths", "Areas", "A", "Rubber sheet geometry."),
            ("Mathematics", "Geometry", "Easy", "Parallel lines meet?", "Never", "At infinity", "At 90 deg", "Eventually", "A", "By definition."),
            ("Mathematics", "Geometry", "Medium", "Centroid is intersection of?", "Medians", "Altitudes", "Bisectors", "Perpendiculars", "A", "Center of mass."),
            ("Mathematics", "Geometry", "Hard", "Non-Euclidean geometry?", "Curved space", "Flat space", "Box", "Line", "A", "Spherical/Hyperbolic."),
            ("Mathematics", "Geometry", "Medium", "Hypotenuse is?", "Opposite right angle", "Shortest side", "Adjacent", "None", "A", "Longest side."),

            # Statistics
            ("Mathematics", "Statistics", "Easy", "Average is also?", "Mean", "Mode", "Median", "Range", "A", "Mean."),
            ("Mathematics", "Statistics", "Medium", "Sample vs Population?", "Sample is subset", "Same", "Sample is larger", "None", "A", "Subgroup."),
            ("Mathematics", "Statistics", "Hard", "Type I error?", "False Positive", "False Negative", "Correct", "None", "A", "Reject true null."),
            ("Mathematics", "Statistics", "Easy", "Coin toss heads chance?", "50%", "100%", "25%", "0%", "A", "Fair coin."),
            ("Mathematics", "Statistics", "Medium", "Histogram shows?", "Frequency distribution", "Time series", "Correlation", "Map", "A", "Bar chart for frequency."),
            ("Mathematics", "Statistics", "Hard", "Central Limit Theorem?", "Approaches Normal dist", "Approaches Uniform", "Stay same", "None", "A", "Sum of random variables."),
            ("Mathematics", "Statistics", "Easy", "Dice roll sides?", "6", "5", "4", "2", "A", "Standard cube."),
            ("Mathematics", "Statistics", "Medium", "Percentile?", "Value below which percent falls", "Percentage", "Average", "None", "A", "Ranking."),
            ("Mathematics", "Statistics", "Hard", "Poisson distribution?", "Events in time/space interval", "Coin toss", "Height", "None", "A", "Rare events count."),
            ("Mathematics", "Statistics", "Medium", "Skewness measures?", "Asymmetry", "Height", "Width", "Center", "A", "Tail direction."),

            # --- PHYSICS ---
            # Mechanics
            ("Physics", "Mechanics", "Easy", "Speed formula?", "d/t", "d*t", "t/d", "m*a", "A", "Distance over time."),
            ("Physics", "Mechanics", "Medium", "Scalar has?", "Magnitude only", "Direction", "Both", "None", "A", "Like mass, speed."),
            ("Physics", "Mechanics", "Hard", "Bernoulli's principle?", "Fluid dynamics", "Solids", "Gases only", "Gravity", "A", "Speed vs Pressure."),
            ("Physics", "Mechanics", "Easy", "Earth orbits?", "Sun", "Moon", "Mars", "Jupiter", "A", "Heliocentric."),
            ("Physics", "Mechanics", "Medium", "Terminal velocity?", "Constant max fall speed", "Start speed", "Zero", "None", "A", "Drag equals gravity."),
            ("Physics", "Mechanics", "Hard", "Lagrangian mechanics uses?", "Energy (T-V)", "Forces", "Momentum", "Friction", "A", "Alternative to Newtonian."),
            ("Physics", "Mechanics", "Easy", "Unit of Time?", "Second", "Hour", "Day", "Year", "A", "SI unit."),
            ("Physics", "Mechanics", "Medium", "Centripetal force direction?", "Center", "Outward", "Tangent", "Down", "A", "Towards center."),
            ("Physics", "Mechanics", "Hard", "Coriolis effect?", "Deflection due to rotation", "Gravity", "Magnetic", "Friction", "A", "Earth's rotation."),
            ("Physics", "Mechanics", "Medium", "Impulse is?", "Change in momentum", "Force", "Energy", "Power", "A", "Force * Delta t."),

            # Thermodynamics
            ("Physics", "Thermodynamics", "Easy", "Sun gives?", "Heat & Light", "Cold", "Wind", "Water", "A", "Energy source."),
            ("Physics", "Thermodynamics", "Medium", "Convection works in?", "Fluids", "Solids", "Vacuum", "None", "A", "Movement of matter."),
            ("Physics", "Thermodynamics", "Hard", "Third law of thermo?", "Entropy at 0K is 0", "Entropy increases", "Energy conserved", "None", "A", "Perfect crystal."),
            ("Physics", "Thermodynamics", "Easy", "Ice melts to?", "Water", "Gas", "Solid", "Plasma", "A", "Phase transition."),
            ("Physics", "Thermodynamics", "Medium", "Thermal expansion?", "Objects expand when hot", "Shrink", "Stay same", "None", "A", "Atoms vibrate more."),
            ("Physics", "Thermodynamics", "Hard", "Enthalpy symbol?", "H", "E", "S", "G", "A", "H = U + PV."),
            ("Physics", "Thermodynamics", "Easy", "Toaster uses?", "Heat", "Cold", "Wind", "Water", "A", "Electric heating."),
            ("Physics", "Thermodynamics", "Medium", "Black body absorbs?", "All radiation", "None", "Some", "White light", "A", "Ideal absorber."),
            ("Physics", "Thermodynamics", "Hard", "Maxwell-Boltzmann distribution?", "Gas speeds", "Solids", "Liquids", "Gravity", "A", "Statistical mechanics."),
            ("Physics", "Thermodynamics", "Medium", "Triple point?", "S,L,G coexist", "Boiling", "Freezing", "None", "A", "Specific P and T."),

            # Electromagnetism
            ("Physics", "Electromagnetism", "Easy", "Battery provides?", "Voltage", "AC", "Heat", "Light", "A", "DC Source."),
            ("Physics", "Electromagnetism", "Medium", "AC vs DC?", "Alternating vs Direct", "Same", "Amp vs Volt", "None", "A", "Current direction."),
            ("Physics", "Electromagnetism", "Hard", "Gausss Law?", "Flux = q/epsilon", "V=IR", "F=ma", "None", "A", "Electric flux."),
            ("Physics", "Electromagnetism", "Easy", "Lightning is?", "Electricity", "Fire", "Wind", "Sound", "A", "Discharge."),
            ("Physics", "Electromagnetism", "Medium", "Galvanometer detects?", "Small currents", "Voltage", "Heat", "Pressure", "A", "Sensitive."),
            ("Physics", "Electromagnetism", "Hard", "Biot-Savart Law?", "Magnetic field by wire", "Electric field", "Force", "Flux", "A", "Current segment -> B-field."),
            ("Physics", "Electromagnetism", "Easy", "Unit of Resistance?", "Ohm", "Volt", "Amp", "Watt", "A", "Resistance."),
            ("Physics", "Electromagnetism", "Medium", "Superconductor resistance?", "Zero", "High", "Infinite", "Normal", "A", "At low temp."),
            ("Physics", "Electromagnetism", "Hard", "Poynting vector?", "Energy flux", "Force", "Momentum", "Charge", "A", "Direction of energy flow."),
            ("Physics", "Electromagnetism", "Medium", "Dielectric is?", "Insulator", "Conductor", "Semiconductor", "Magnet", "A", "Polarizable."),

            # Optics
            ("Physics", "Optics", "Easy", "Telescope sees?", "Far objects", "Small objects", "Bacteria", "Atoms", "A", "Magnifies distant."),
            ("Physics", "Optics", "Medium", "Prism creates?", "Spectrum", "Laser", "Fire", "Wind", "A", "Dispersion."),
            ("Physics", "Optics", "Hard", "Fermat's Principle?", "Least Time path", "Least Distance", "Most Time", "None", "A", "Light path."),
            ("Physics", "Optics", "Easy", "Microscope sees?", "Small objects", "Stars", "Planets", "People", "A", "Magnifies small."),
            ("Physics", "Optics", "Medium", "Optical fiber uses?", "TIR", "Refraction", "Diffraction", "Reflection", "A", "Total Internal Reflection."),
            ("Physics", "Optics", "Hard", "Huygens Principle?", "Wavelets", "Particles", "Rays", "None", "A", "Wave propagation."),
            ("Physics", "Optics", "Easy", "Shadows caused by?", "Light blocking", "Darkness", "Sun", "Moon", "A", "Rectilinear prop."),
            ("Physics", "Optics", "Medium", "Astigmatism is?", "Eye defect", "Lens", "Mirror", "Color", "A", "Blurred vision."),
            ("Physics", "Optics", "Hard", "Brewster's angle?", "Polarization", "Reflection", "Refraction", "Diffraction", "A", "No reflection of p-polarized."),
            ("Physics", "Optics", "Medium", "Laser light is?", "Coherent", "Scattered", "Weak", "White", "A", "Monochromatic/Coherent."),

            # --- CHEMISTRY ---
            # Organic
            ("Chemistry", "Organic", "Easy", "Oil comes from?", "Fossils", "Rocks", "Water", "Air", "A", "Hydrocarbons."),
            ("Chemistry", "Organic", "Medium", "Aromatic means?", "Ring structure (stable)", "Smell", "Straight chain", "None", "A", "Huckel's rule."),
            ("Chemistry", "Organic", "Hard", "Chirality?", "Handedness", "Footedness", "Symmetry", "Color", "A", "Mirror images not superimposable."),
            ("Chemistry", "Organic", "Easy", "Sugar is?", "Carbohydrate", "Fat", "Protein", "Salt", "A", "Succrose etc."),
            ("Chemistry", "Organic", "Medium", "Polymerization makes?", "Plastic", "Gas", "Water", "Metal", "A", "Long chains."),
            ("Chemistry", "Organic", "Hard", "Grignard reagent?", "R-Mg-X", "Acid", "Base", "Salt", "A", "Strong nucleophile."),
            ("Chemistry", "Organic", "Easy", "Plastic is?", "Synthetic polymer", "Natural", "Metal", "Stone", "A", "Moldable."),
            ("Chemistry", "Organic", "Medium", "Ether formula?", "R-O-R", "R-OH", "R-COOH", "R-H", "A", "Oxygen bridge."),
            ("Chemistry", "Organic", "Hard", "SN1 vs SN2?", "Substitution mechanisms", "Elimination", "Addition", "None", "A", "Nucleophilic substitution."),
            ("Chemistry", "Organic", "Medium", "Soap is?", "Salt of fatty acid", "Acid", "Base", "Sugar", "A", "Cleaning agent."),

            # Inorganic
            ("Chemistry", "Inorganic", "Easy", "H is symbol for?", "Hydrogen", "Helium", "Hafnium", "Heat", "A", "First element."),
            ("Chemistry", "Inorganic", "Medium", "Alloy of Iron + Carbon?", "Steel", "Brass", "Bronze", "Gold", "A", "Common construction material."),
            ("Chemistry", "Inorganic", "Hard", "Lanthanides are?", "Rare Earths", "Gases", "Liquids", "Non-metals", "A", "f-block."),
            ("Chemistry", "Inorganic", "Easy", "Coin metal?", "Copper/Silver/Gold", "Iron", "Lead", "Mercury", "A", "Minting."),
            ("Chemistry", "Inorganic", "Medium", "Halogens group?", "17", "1", "18", "2", "A", "F, Cl, Br, I."),
            ("Chemistry", "Inorganic", "Hard", "Crystal Field Theory?", "d-orbital splitting", "s-orbital", "Bonds", "None", "A", "Coordination complexes."),
            ("Chemistry", "Inorganic", "Easy", "Mercury is?", "Liquid metal", "Gas", "Solid", "Plastic", "A", "Hg."),
            ("Chemistry", "Inorganic", "Medium", "Rust is?", "Iron Oxide", "Carbon", "Gold", "Silver", "A", "Oxidation."),
            ("Chemistry", "Inorganic", "Hard", "VSEPR theory?", "Molecular Logic/Shape", "Energy", "Mass", "None", "A", "Valence Shell Electron Pair Repulsion."),
            ("Chemistry", "Inorganic", "Medium", "Metalloid example?", "Silicon", "Iron", "Gas", "Water", "A", "Semi-metal property."),

            # Physical
            ("Chemistry", "Physical", "Easy", "Ice floating?", "Less dense than water", "More dense", "Same", "Magic", "A", "Water expands when freezing."),
            ("Chemistry", "Physical", "Medium", "Exothermic releases?", "Heat", "Cold", "Light", "Sound", "A", "Delta H negative."),
            ("Chemistry", "Physical", "Hard", "Schrodinger equation?", "Quantum wave function", "Motion", "Gravity", "Heat", "A", "Quantum mechanics."),
            ("Chemistry", "Physical", "Easy", "Boiling needs?", "Heat", "Cold", "Ice", "Wind", "A", "Vaporization."),
            ("Chemistry", "Physical", "Medium", "Buffer solution?", "Resists pH change", "Changes pH", "Neutral", "Acid", "A", "Maintenance."),
            ("Chemistry", "Physical", "Hard", "Raoult's Law?", "Vapor pressure", "Gas pressure", "Osmosis", "None", "A", "Solutions."),
            ("Chemistry", "Physical", "Easy", "Evaporation causes?", "Cooling", "Heating", "Burning", "None", "A", "High energy molecules leave."),
            ("Chemistry", "Physical", "Medium", "Diffusion?", "High to Low conc", "Low to High", "Static", "None", "A", "Spreading out."),
            ("Chemistry", "Physical", "Hard", "Activation Energy?", "Min energy to react", "Max energy", "Zero", "Total", "A", "Barrier."),
            ("Chemistry", "Physical", "Medium", "Half-life?", "Time for half decay", "Full decay", "Double", "None", "A", "Radioactivity/Kinetics."),

            # Biochemistry
            ("Chemistry", "Biochemistry", "Easy", "Carrots have?", "Vitamin A", "Vitamin C", "Fat", "Protein", "A", "Good for eyes."),
            ("Chemistry", "Biochemistry", "Medium", "RNA vs DNA?", "Single vs Double strand", "Same", "Triple", "None", "A", "Genetic material."),
            ("Chemistry", "Biochemistry", "Hard", "Krebs Cycle?", "Energy production", "Digestion", "Thinking", "Moving", "A", "Cellular respiration."),
            ("Chemistry", "Biochemistry", "Easy", "Muscle needs?", "Protein", "Fat", "Sugar", "Salt", "A", "Building block."),
            ("Chemistry", "Biochemistry", "Medium", "Antibodies fight?", "Antigens/Pathogens", "Cells", "Food", "Water", "A", "Immune system."),
            ("Chemistry", "Biochemistry", "Hard", "Peptide bond links?", "Amino acids", "Sugars", "Fats", "DNA", "A", "Protein structure."),
            ("Chemistry", "Biochemistry", "Easy", "Calcium good for?", "Bones", "Eyes", "Hair", "Skin", "A", "Skeleton."),
            ("Chemistry", "Biochemistry", "Medium", "Hormones are?", "Chemical messengers", "Cells", "Genes", "Bones", "A", "Regulation."),
            ("Chemistry", "Biochemistry", "Hard", "Glycolysis occurs in?", "Cytoplasm", "Nucleus", "Mitochondria", "Blood", "A", "Glucose breakdown."),
            ("Chemistry", "Biochemistry", "Medium", "Cholesterol is?", "Lipid/Fat", "Protein", "Sugar", "Vitamin", "A", "Cell membranes.")
        ]

        print(f"   ⏳ Inserting {len(more_questions)} more questions (Batch 2)...")
        
        for subject, topic, difficulty, q_text, op_a, op_b, op_c, op_d, correct, explanation in more_questions:
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
        
        print(f"   ✅ Processed {len(more_questions)} more questions.")

        conn.commit()
        cur.close()
        conn.close()
        print("\n✨ BATCH 2 QUESTIONS SEEDED SUCCESSFULLY! ✨")

    except Exception as e:
        print("\n❌ Error Seeding More Questions:")
        print(e)

if __name__ == "__main__":
    seed_more_questions()
