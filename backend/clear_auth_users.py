
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

def clear_auth_users():
    try:
        print("🚀 Connecting to Supabase for Auth Cleanup...")
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()

        print("🔥 Deleting all users from auth.users...")
        # Be careful: This deletes ALL users in Auth
        cur.execute("DELETE FROM auth.users;")
        deleted_count = cur.rowcount
        print(f"   🗑️ Deleted {deleted_count} users from auth.users.")

        cur.close()
        conn.close()
        print("✨ Auth Users Cleared! ✨")

    except Exception as e:
        print("\n❌ Error Clearing Auth Users:")
        print(e)
        print("Note: You might need rights to delete from auth.users. If this fails, delete users manually in Supabase Dashboard.")

if __name__ == "__main__":
    clear_auth_users()
