
import pytest
from app import app
import json
import random
import sys

def test_signup_flow():
    with app.test_client() as client:
        # Generate random email
        email = f"auto_test_{random.randint(100000,999999)}@example.com"
        password = "testpassword123"
        
        try:
            response = client.post('/api/signup', 
                data=json.dumps({
                    "email": email,
                    "password": password,
                    "data": {"role": "student", "full_name": "Auto Test"}
                }),
                content_type='application/json'
            )
            
            data = response.get_json()
            
            with open("test_signup_error.log", "w") as f:
                f.write(f"Status: {response.status_code}\n")
                f.write(f"Data: {json.dumps(data, indent=2)}\n")
                
            print(f"Logged to test_signup_error.log")
            
        except Exception as e:
            with open("test_signup_error.log", "w") as f:
                f.write(f"Exception: {e}\n")

if __name__ == "__main__":
    test_signup_flow()
