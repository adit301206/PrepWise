
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Missing SUPABASE_URL or SUPABASE_KEY in .env")
    exit(1)

try:
    supabase: Client = create_client(url, key)
    print("Supabase client initialized.")
    
    # Test Data
    test_email = "test_user@example.com"
    test_name = "Test User"
    
    print(f"Invoking 'send-welcome-email' for {test_email}...")
    
    response = supabase.functions.invoke("send-welcome-email", invoke_options={
        "body": {"email": test_email, "name": test_name}
    })
    
    print("Function Response:", response)
    
except Exception as e:
    print(f"Error invoking function: {e}")
