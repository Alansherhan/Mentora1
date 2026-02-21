import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"
DATA_DIR = Path("data")
UNANSWERED_FILE = DATA_DIR / "unanswered_queries.json"

def test_delete_unanswered():
    print("--- Testing Unanswered Query Deletion ---")
    
    # 1. Add a test query if none exist
    test_query = "Test query for deletion " + str(os.urandom(4).hex())
    
    # Ensure data dir exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # Load existing
    if UNANSWERED_FILE.exists():
        with open(UNANSWERED_FILE, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []
        
    # Add dummy
    data.append({"query": test_query, "asked_at": "2026-02-09T00:00:00"})
    
    with open(UNANSWERED_FILE, 'w') as f:
        json.dump(data, f)
    
    print(f"Added test query: {test_query}")
    
    # 2. Call the delete API
    print(f"Calling DELETE /api/delete_unanswered for: {test_query}")
    try:
        response = requests.post(
            f"{API_URL}/delete_unanswered",
            json={"query": test_query}
        )
        print(f"Response Status: {response.status_code}")
        print(f"Response JSON: {response.json()}")
        
        if response.status_code == 200 and response.json().get('success'):
            print("SUCCESS: Backend delete successful.")
        else:
            print("FAILURE: Backend delete failed.")
            return False
            
    except Exception as e:
        print(f"ERROR: Backend call failed: {e}")
        return False
        
    # 3. Verify file content
    with open(UNANSWERED_FILE, 'r') as f:
        data = json.load(f)
        
    found = any(q['query'] == test_query for q in data)
    if not found:
        print("SUCCESS: Query actually removed from file.")
    else:
        print("FAILURE: Query still exists in file.")
        return False
        
    return True

if __name__ == "__main__":
    test_delete_unanswered()
