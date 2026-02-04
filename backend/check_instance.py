
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

try:
    cur.execute("SELECT * FROM auth.instances;")
    print("Instances:", cur.fetchall())
except Exception as e:
    print("No auth.instances:", e)

try:
    cur.execute("SELECT * FROM auth.schema_migrations ORDER BY version DESC LIMIT 5;")
    print("Migrations:", cur.fetchall())
except Exception as e:
    print("No migrations:", e)

conn.close()
