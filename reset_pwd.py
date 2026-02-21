import hashlib
import json
import datetime
import os

SALT = "smartbuddy_salt_2024"
pwd = "123"
h = hashlib.sha256((pwd + SALT).encode()).hexdigest()

data = {
    "password_hash": h,
    "last_changed": datetime.datetime.now().isoformat()
}

path = r"d:\smartbuddyremastered\smartbuddy\data\chatbot_auth.json"
with open(path, "w") as f:
    json.dump(data, f, indent=4)
    
print(f"Reset password to '123' (Hash: {h})")
