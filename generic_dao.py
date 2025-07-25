# generic_dao.py

import sqlite3
from database import get_connection


DB_NAME = "epic_crm.db"

def connect_db():
    return sqlite3.connect(DB_NAME)


def create(table_name, obj, fields):
    """
    Insère un objet dans la table donnée et assigne l'ID généré automatiquement.
    
    :param table_name: Nom de la table dans la base de données.
    :param obj: Objet Python à insérer.
    :param fields: Liste des attributs de l'objet à insérer.
    :return: L'objet avec l'ID mis à jour.
    """
    conn = get_connection()
    cur = conn.cursor()

    columns = ", ".join(fields)
    placeholders = ", ".join(["?"] * len(fields))
    values = [getattr(obj, field) for field in fields]

    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    try:
        cur.execute(query, values)
        conn.commit()
        obj.id = cur.lastrowid  # Assigne l'ID généré à l'objet
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion dans {table_name} : {e}")
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

    return obj

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

def get_all_filtered(model_name, model_class, field, value, operator="="):
    conn = get_connection()
    cur = conn.cursor()
    query = f"SELECT * FROM {model_name} WHERE {field} {operator} ?"
    cur.execute(query, (value,))
    rows = cur.fetchall()
    conn.close()
    return [model_class(*row) for row in rows]

