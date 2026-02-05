import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"--- DEBUGGING RAW REQUEST ---")
print(f"Target URL Base: {url}")

function_url = f"{url}/functions/v1/send-welcome-email"
print(f"Function Endpoint: {function_url}")

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

payload = {
    "email": "debug_raw@example.com",
    "name": "Raw Debugger"
}

try:
    print("Sending POST request...")
    response = requests.post(function_url, json=payload, headers=headers)
    
    print(f"\nSTATUS CODE: {response.status_code}")
    print(f"RESPONSE TEXT: {response.text}")
    print(f"RESPONSE HEADERS: {response.headers}")

except Exception as e:
    print(f"CRITICAL FAILURE: {e}")
