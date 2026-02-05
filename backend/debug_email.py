
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

with open("debug_output.txt", "w") as f:
    if not url or not key:
        f.write("Missing URL or KEY\n")
        exit(1)

    try:
        supabase: Client = create_client(url, key)
        f.write("Supabase client initialized.\n")
    except Exception as e:
        f.write(f"Failed to init client: {e}\n")
        exit(1)

    # Test Signup with a RANDOM email to avoid "User already registered" if previous one worked partially
    import random
    email = f"test_debug_{random.randint(1000,9999)}@example.com"
    password = "password123"

    f.write(f"Attempting signup for {email}...\n")

    try:
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        f.write("Signup call completed.\n")
        f.write(f"User ID: {auth_response.user.id if auth_response.user else 'None'}\n")
        f.write(f"Session: {auth_response.session}\n")
    except Exception as e:
        f.write(f"Signup FAILED: {e}\n")
