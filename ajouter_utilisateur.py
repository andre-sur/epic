import bcrypt
import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('epic_crm.db')
cursor = conn.cursor()

print("=== Création d’un nouvel utilisateur ===")

# Demande des informations à l'utilisateur
name = input("Nom complet : ").strip()
email = input("Adresse email : ").strip()
password_clair = input("Mot de passe : ").strip()

# Vérification du rôle
roles_valides = ['gestion', 'commercial', 'support']
role = ""
while role not in roles_valides:
    role = input("Rôle (gestion, commercial, support) : ").strip().lower()
    if role not in roles_valides:
        print("❌ Rôle invalide. Choisissez parmi : gestion, commercial, support.")

# Hachage du mot de passe
hashed_password = bcrypt.hashpw(password_clair.encode('utf-8'), bcrypt.gensalt())

# Insertion dans la base
try:
    cursor.execute("""
        INSERT INTO user (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (name, email, hashed_password.decode('utf-8'), role))
    conn.commit()
    print("\n✅ Utilisateur ajouté avec succès.")
except sqlite3.IntegrityError as e:
    print(f"\n❌ Erreur lors de l'ajout de l'utilisateur : {e}")

# Fermeture de la connexion
conn.close()
