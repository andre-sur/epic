import sqlite3

def init_db():
    conn = sqlite3.connect("epic_crm.db")
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de données initialisée.")
