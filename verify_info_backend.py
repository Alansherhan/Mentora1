import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_add_section():
    print("Testing Add Section...")
    payload = {'category': 'Test Section Backend'}
    try:
        r = requests.post(f"{BASE_URL}/add_section", json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
        if r.json().get('success'):
            print("PASS")
        else:
            print("FAIL")
    except Exception as e:
        print(f"Error: {e}")

def test_edit_section():
    print("\nTesting Edit Section...")
    payload = {
        'original_category': 'Test Section Backend',
        'new_category': 'Test Section Backend Renamed'
    }
    try:
        r = requests.post(f"{BASE_URL}/edit_section", json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
        if r.json().get('success'):
            print("PASS")
        else:
            print("FAIL")
    except Exception as e:
        print(f"Error: {e}")

def test_add_item():
    print("\nTesting Add Item...")
    payload = {
        'section': 'Test Section Backend Renamed',
        'title': 'Test Item',
        'content': 'Test Content',
        'keywords': 'k1, k2'
    }
    try:
        r = requests.post(f"{BASE_URL}/add_info_item", json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
        if r.json().get('success'):
            print("PASS")
        else:
            print("FAIL")
    except Exception as e:
        print(f"Error: {e}")

def cleanup():
    print("\nCleaning up...")
    payload = {'category': 'Test Section Backend Renamed'}
    requests.post(f"{BASE_URL}/delete_section", json=payload)
    print("Cleanup done.")

if __name__ == "__main__":
    test_add_section()
    test_edit_section()
    test_add_item()
    cleanup()
