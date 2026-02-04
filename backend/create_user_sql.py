
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import uuid

load_dotenv()

DB_URL = os.environ.get("DATABASE_URL")

email = "test_sql_user@example.com"
password = "password123"

try:
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    # 1. Check if pgcrypto exists (needed for hashing)
    cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    
    # 2. Insert user into auth.users
    # detailed manual insertion for Supabase Auth
    user_id = str(uuid.uuid4())
    
    sql = """
    INSERT INTO auth.users (
        instance_id,
        id,
        aud,
        role,
        email,
        encrypted_password,
        email_confirmed_at,
        recovery_sent_at,
        last_sign_in_at,
        raw_app_meta_data,
        raw_user_meta_data,
        is_super_admin,
        created_at,
        updated_at,
        confirmation_token
    ) VALUES (
        '00000000-0000-0000-0000-000000000000',
        %s,
        'authenticated',
        'authenticated',
        %s,
        crypt(%s, gen_salt('bf')),
        now(),
        NULL,
        NULL,
        '{"provider": "email", "providers": ["email"]}',
        '{"full_name": "SQL Test User"}',
        FALSE,
        now(),
        now(),
        ''
    ) RETURNING id;
    """
    
    print(f"Attempting to create user {email} via SQL...")
    cur.execute(sql, (user_id, email, password))
    new_id = cur.fetchone()[0]
    print(f"Success! Created user with ID: {new_id}")
    
    # 3. Insert into public.users if your app uses a separate profile table
    # (Checking app.py implies we might not strictly need it, but good practice if the app relies on it)
    # app.py doesn't seem to insert into a public table explicitly in the signup route, it just calls Supabase.
    
    cur.close()
    conn.close()

except Exception as e:
    print(f"SQL Creation FAILED: {e}")
