import sqlite3

# Connexion à la base de données
def connect_db():
    return sqlite3.connect('epic_crm.db')

# Menu principal pour les gestionnaires
def afficher_menu_gestion(utilisateur):
    while True:
        print("\n=== Menu Gestion ===")
        print("1. Créer un collaborateur")
        print("2. Mettre à jour un collaborateur")
        print("3. Afficher tous les collaborateurs")
        print("4. Créer un événement")
        print("5. Filtrer les événements")
        print("6. Retour au menu principal")

        choix = input("Veuillez entrer votre choix: ")

        if choix == '1':
            creer_collaborateur()
        elif choix == '2':
            mettre_a_jour_collaborateur()
        elif choix == '3':
            afficher_collaborateurs()
        elif choix == '4':
            creer_evenement()
        elif choix == '5':
            filtrer_evenements()
        elif choix == '6':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

# Fonction pour créer un collaborateur
def creer_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un collaborateur ===")
    name = input("Nom du collaborateur: ")
    email = input("Email du collaborateur: ")
    password = input("Mot de passe du collaborateur: ")
    role = input("Rôle (gestion, commercial, support): ")

    cursor.execute("""
        INSERT INTO user (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (name, email, password, role))

    conn.commit()
    print("Collaborateur ajouté avec succès !")
    conn.close()

# Fonction pour mettre à jour un collaborateur
def mettre_a_jour_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Mise à jour d'un collaborateur ===")
    collaborator_id = input("ID du collaborateur à mettre à jour: ")

    # Vérifier s'il existe
    cursor.execute("SELECT * FROM user WHERE id = ?", (collaborator_id,))
    user = cursor.fetchone()

    if not user:
        print("Aucun collaborateur avec cet ID.")
        conn.close()
        return

    name = input("Nouveau nom (laisser vide pour ne pas modifier): ")
    email = input("Nouveau email (laisser vide pour ne pas modifier): ")

    if name:
        cursor.execute("UPDATE user SET name = ? WHERE id = ?", (name, collaborator_id))
    if email:
        cursor.execute("UPDATE user SET email = ? WHERE id = ?", (email, collaborator_id))

    conn.commit()
    print("Collaborateur mis à jour avec succès.")
    conn.close()

# Fonction pour afficher tous les collaborateurs
def afficher_collaborateurs():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Liste des collaborateurs ===")
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()

    if not users:
        print("Aucun collaborateur trouvé.")
    else:
        for user in users:
            print(f"ID: {user[0]}, Nom: {user[1]}, Email: {user[2]}, Rôle: {user[4]}")

    conn.close()

# Fonction pour créer un événement
def creer_evenement():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un événement ===")
    contract_id = input("ID du contrat lié à cet événement: ")
    support_id = input("ID du collaborateur du support responsable: ")
    start_date = input("Date de début (format AAAA-MM-JJ HH:MM): ")
    end_date = input("Date de fin (format AAAA-MM-JJ HH:MM): ")
    location = input("Lieu de l'événement: ")
    attendees = int(input("Nombre d'attendees: "))
    notes = input("Notes supplémentaires: ")

    cursor.execute("""
        INSERT INTO event (contract_id, support_id, start_date, end_date, location, attendees, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (contract_id, support_id, start_date, end_date, location, attendees, notes))

    conn.commit()
    print("Événement créé avec succès !")
    conn.close()

# Fonction pour filtrer les événements
def filtrer_evenements():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Filtrer les événements ===")
    filtre = input("Filtrer par date de début (ex: 2023-05-01): ")

    cursor.execute("SELECT * FROM event WHERE start_date >= ?", (filtre,))
    events = cursor.fetchall()

    if not events:
        print("Aucun événement trouvé pour cette date.")
    else:
        for event in events:
            print(f"ID: {event[0]}, Contract ID: {event[1]}, Start: {event[3]}, Location: {event[5]}")

    conn.close()
