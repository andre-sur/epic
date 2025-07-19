import sqlite3
from models import Client

def connect_db():
    return sqlite3.connect('epic_crm.db')

def add_client(client):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO client (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client.full_name, client.email, client.phone, client.company_name, client.created_date, client.last_contact_date, client.commercial_id))
    conn.commit()
    conn.close()

def get_client_by_id(client_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client WHERE id = ?", (client_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Client(*row)
    return None

def update_client(client):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE client SET
            full_name = ?,
            email = ?,
            phone = ?,
            company_name = ?,
            created_date = ?,
            last_contact_date = ?,
            commercial_id = ?
        WHERE id = ?
    """, (client.full_name, client.email, client.phone, client.company_name, client.created_date, client.last_contact_date, client.commercial_id, client.id))
    conn.commit()
    conn.close()

def delete_client(client_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM client WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()

def get_all_clients():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client")
    rows = cursor.fetchall()
    conn.close()
    return [Client(*row) for row in rows]

def get_clients_by_commercial(commercial_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client WHERE commercial_id = ?", (commercial_id,))
    rows = cursor.fetchall()
    conn.close()
    return [Client(*row) for row in rows]
