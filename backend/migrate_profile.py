import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Check if columns exist
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND table_schema = 'public';")
    existing_columns = [row[0] for row in cur.fetchall()]
    
    alter_commands = []
    
    if 'bio' not in existing_columns:
        alter_commands.append("ADD COLUMN bio TEXT")
    if 'phone' not in existing_columns:
        alter_commands.append("ADD COLUMN phone VARCHAR(20)")
    if 'birthdate' not in existing_columns:
        alter_commands.append("ADD COLUMN birthdate DATE")
    if 'avatar_url' not in existing_columns:
        alter_commands.append("ADD COLUMN avatar_url TEXT")
        
    if alter_commands:
        full_command = f"ALTER TABLE users {', '.join(alter_commands)};"
        print(f"Executing: {full_command}")
        cur.execute(full_command)
        conn.commit()
        print("Migration successful: Columns added.")
    else:
        print("No migration needed: Columns already exist.")
        
    conn.close()
except Exception as e:
    print(f"Migration Error: {e}")
