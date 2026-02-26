import requests
import json
import jwt
from datetime import datetime, timedelta

# Test Backend Direct
backend_url = "http://127.0.0.1:8000/chat/new"
secret = "your-super-secret-jwt-key-here-make-it-long-and-random"
bridge_user_id = "658af0c1e4b0a1a2b3c4d5e6"

payload_jwt = {
    "id": bridge_user_id,
    "email": "bridge@internal.ai",
    "role": "admin",
    "exp": datetime.utcnow() + timedelta(hours=1)
}
token = jwt.encode(payload_jwt, secret, algorithm="HS256")

payload = {
    "message": "Hello from Bridge Test",
    "userId": bridge_user_id,
    "chatbotId": "658af0c1e4b0a1a2b3c4d5e7"
}
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

print(f"Testing Backend at {backend_url}...")
try:
    response = requests.post(backend_url, json=payload, headers=headers, timeout=5)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
