# generic_dao.py

import sqlite3

DB_NAME = "epic_crm.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create(table_name, obj, fields):
    conn = connect_db()
    cursor = conn.cursor()
    placeholders = ', '.join(['?'] * len(fields))
    field_list = ', '.join(fields)
    values = tuple(getattr(obj, field) for field in fields)
    cursor.execute(f"""
        INSERT INTO {table_name} ({field_list})
        VALUES ({placeholders})
    """, values)
    conn.commit()
    conn.close()

def get_by_id(table_name, model_class, obj_id):
    conn = connect_db()
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name} WHERE id = ?"
    cursor.execute(query, (obj_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return model_class(*row)
    return None

def update(table_name, obj, fields):
    conn = connect_db()
    cursor = conn.cursor()
    set_clause = ', '.join([f"{field} = ?" for field in fields])
    values = tuple(getattr(obj, field) for field in fields)
    cursor.execute(f"""
        UPDATE {table_name}
        SET {set_clause}
        WHERE id = ?
    """, values + (obj.id,))
    conn.commit()
    conn.close()

def delete(table_name, obj_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (obj_id,))
    conn.commit()
    conn.close()

def get_all(table_name, model_class):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    return [model_class(*row) for row in rows]

def get_all_filtered(table_name, model_class, filter_field, filter_value):
    conn = connect_db()
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name} WHERE {filter_field} = ?"
    cursor.execute(query, (filter_value,))
    rows = cursor.fetchall()
    conn.close()
    return [model_class(*row) for row in rows]
