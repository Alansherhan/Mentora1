import hashlib
import json
import datetime
from pathlib import Path

DATA_DIR = Path('data')
SALT = "smartbuddy_salt_2024"
pwd = "123"
h = hashlib.sha256((pwd + SALT).encode()).hexdigest()

data = {
    "password_hash": h,
    "last_changed": datetime.datetime.now().isoformat()
}

with open(DATA_DIR / 'chatbot_auth.json', 'w') as f:
    json.dump(data, f, indent=4)

print(f"Reset chatbot password to '123' (Hash: {h})")
