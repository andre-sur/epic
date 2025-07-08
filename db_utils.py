# db_utils.py
import sqlite3
def connect_db():
    return sqlite3.connect('epic_crm.db')
