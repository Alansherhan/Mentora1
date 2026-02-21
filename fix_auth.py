from server import DataManager, DATA_DIR
import datetime

dm = DataManager()
# Reset to default '123'
new_auth = {
    'password_hash': dm.hash_password('123'),
    'last_changed': datetime.datetime.now().isoformat()
}

dm.save_json(DATA_DIR / 'chatbot_auth.json', new_auth)
print("Reset chatbot_auth.json to single password '123'")
