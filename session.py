import json
import os
from datetime import datetime, timedelta

SESSION_FILE = '.epic_crm_auth'

def save_session(user_id):
    data = {
        'user_id': user_id,
        'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()  # session valide 1 heure
    }
    with open(SESSION_FILE, 'w') as f:
        json.dump(data, f)

def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, 'r') as f:
        data = json.load(f)
    expires_at = datetime.fromisoformat(data['expires_at'])
    if datetime.now() > expires_at:
        os.remove(SESSION_FILE)
        return None
    return data['user_id']

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
