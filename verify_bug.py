import requests
import time
import json

BASE_URL = "http://localhost:5000/api"

def run_repro():
    print("Running Reproduction Script...")
    s = requests.Session()
    
    # 0. Admin Login (to add items)
    print("Logging in as Admin...")
    s.post(f"{BASE_URL}/admin/login", json={'password': '123'})
    
    # 1. Add Info Section & Item
    print("Adding Test Section...")
    s.post(f"{BASE_URL}/add_section", json={'category': 'Bug Repro Section'})
    
    print("Adding Test Item with Keyword 'bugtoken'...")
    s.post(f"{BASE_URL}/add_info_item", json={
        'section': 'Bug Repro Section',
        'title': '',
        'content': 'This is the content for the bug token test.',
        'keywords': 'bugtoken'
    })
    
    # 2. Chatbot Login (to search)
    print("Logging in as Chatbot...")
    auth_resp = requests.post(f"{BASE_URL}/chatbot/login", json={'password': '123'}).json()
    if not auth_resp.get('success'):
        print(f"Chatbot Login Failed: {auth_resp}")
        return
        
    login_ts = auth_resp.get('login_timestamp')
    print(f"Chatbot logged in, TS: {login_ts}")
    
    # 3. Query Chatbot
    print("Querying chatbot for 'bugtoken'...")
    # Chat endpoint expects login_timestamp in header or body
    headers = {'X-Login-Timestamp': login_ts}
    resp = requests.post(f"{BASE_URL}/chat", json={'message': 'bugtoken'}, headers=headers)
    data = resp.json()
    message = data.get('message', '')
    
    print(f"Response Type: {data.get('type')}")
    print(f"Response Message: {message}")
    
    if "This is the content" in message:
        print("PASS: Search found the item by keyword.")
    else:
        print("FAIL: Search did NOT find the item.")

if __name__ == "__main__":
    try:
        run_repro()
    except Exception as e:
        print(f"Error: {e}")
