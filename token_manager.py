import sqlite3
import uuid
import os
import json

DB_PATH = 'epic_crm.db'
SESSION_FILE = '.session'

def make_token(user_id):
    token = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET token = ? WHERE id = ?", (token, user_id))
    conn.commit()
    conn.close()
    return token

def clear_token(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET token = NULL WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def save_session(user_id, token, role, name):
    with open(SESSION_FILE, 'w') as f:
        json.dump({'user_id': user_id, 'token': token, 'role': role, 'name': name}, f)

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
