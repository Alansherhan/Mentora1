import requests
import json

url = 'http://localhost:5000/api/delete_feedback'
# Exact data from user's file
payload = {
    "text": "ffff",
    "submitted_at": "2026-01-08T21:50:43.143503"
}
headers = {'Content-Type': 'application/json'}

try:
    print(f"Sending payload: {payload}")
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
