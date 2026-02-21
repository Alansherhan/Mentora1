import requests
import json
import time

BASE_URL = 'http://localhost:5000/api'
CHAT_URL = 'http://localhost:5000/api/chat'
LOGIN_URL = 'http://localhost:5000/api/chatbot/login'

def login():
    print("Logging in...")
    try:
        r = requests.post(LOGIN_URL, json={'password': '123'})
        data = r.json()
        if data.get('success'):
            print("Login successful.")
            return data.get('login_timestamp')
        else:
            print(f"Login failed: {data.get('error')}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def setup_test_data():
    print("Setting up test data...")
    # Add Section
    requests.post(f"{BASE_URL}/add_section", json={'category': 'Test Search Section'})
    
    # Add Item 1 (No Title)
    requests.post(f"{BASE_URL}/add_info_item", json={
        'section': 'Test Search Section',
        'title': '', # Empty title
        'content': 'Content for item 1',
        'keywords': 'shared_keyword, unique_1'
    })
    
    # Add Item 2
    requests.post(f"{BASE_URL}/add_info_item", json={
        'section': 'Test Search Section',
        'title': 'Test Item 2',
        'content': 'Content for item 2',
        'keywords': 'shared_keyword, unique_2'
    })
    print("Test data setup complete.")

def test_search(timestamp):
    print("\nTesting Search Logic...")
    
    if not timestamp:
        print("Skipping search test due to login failure.")
        return

    # Login headers
    headers = {'X-Login-Timestamp': timestamp}
    
    # Query with shared keyword
    payload = {'message': 'shared_keyword'}
    
    try:
        r = requests.post(CHAT_URL, json=payload, headers=headers)
        response = r.json()
        
        print(f"Query: 'shared_keyword'")
        print(f"Response Type: {response.get('type')}")
        message = response.get('message', '')
        print(f"Message Preview: {message[:100]}...")
        
        # Verification - CLEAN RESPONSE
        if "Found" in message:
             print("FAIL: Header 'Found X results' is still present.")
        elif "Test Item 1" in message: # Title shouldn't be there unless it's in content
             print("WARNING: Item Title found - check if this is intended (it shouldn't be explicitly added by server).")
             
        if "Content for item 1" in message and "Content for item 2" in message:
            print("PASS: Found both item contents!")
        else:
            print("FAIL: Did not find both item contents.")
            print(f"Full Message: {message}")
            
    except Exception as e:
        print(f"Error: {e}")

def cleanup():
    print("\nCleaning up...")
    requests.post(f"{BASE_URL}/delete_section", json={'category': 'Test Search Section'})
    print("Cleanup done.")

if __name__ == "__main__":
    time.sleep(2) # Wait for server to be fully ready
    ts = login()
    setup_test_data()
    test_search(ts)
    cleanup()
