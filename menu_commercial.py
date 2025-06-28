import sqlite3

# Connexion à la base de données
def connect_db():
    return sqlite3.connect('epic_events.db')

# Fonction pour afficher le menu commercial
def afficher_menu_commercial():
    while True:
        print("\n=== Menu Commercial ===")
        print("1. Créer un client")
        print("2. Modifier un client")
        print("3. Créer un contrat")
        print("4. Afficher tous les clients")
        print("5. Afficher tous les contrats")
        print("6. Retour au menu principal")

        choix = input("Veuillez entrer votre choix: ")

        if choix == '1':
            creer_client()
        elif choix == '2':
            modifier_client()
        elif choix == '3':
            creer_contrat()
        elif choix == '4':
            afficher_clients()
        elif choix == '5':
            afficher_contrats()
        elif choix == '6':
            break  # Retourne au menu principal
        else:
            print("Choix invalide. Veuillez réessayer.")

# Fonction pour créer un client
def creer_client():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un client ===")
    full_name = input("Nom complet du client: ")
    email = input("Email du client: ")
    phone = input("Numéro de téléphone du client: ")
    company_name = input("Nom de l'entreprise: ")
    created_date = input("Date de création (AAAA-MM-JJ): ")
    last_contact_date = input("Date du dernier contact (AAAA-MM-JJ): ")
    commercial_id = input("ID du commercial associé: ")

    cursor.execute("""
        INSERT INTO client (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id))

    conn.commit()
    print("Client ajouté avec succès !")
    conn.close()

# Fonction pour modifier un client
def modifier_client():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Modification d'un client ===")
    client_id = input("ID du client à modifier: ")
    full_name = input("Nouveau nom complet (laisser vide pour ne pas modifier): ")
    email = input("Nouvel email (laisser vide pour ne pas modifier): ")

    if full_name:
        cursor.execute("UPDATE client SET full_name = ? WHERE id = ?", (full_name, client_id))
    if email:
        cursor.execute("UPDATE client SET email = ? WHERE id = ?", (email, client_id))

    conn.commit()
    print("Client modifié avec succès !")
    conn.close()

# Fonction pour créer un contrat
def creer_contrat():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un contrat ===")
    client_id = input("ID du client associé au contrat: ")
    commercial_id = input("ID du commercial associé au contrat: ")
    total_amount = float(input("Montant total du contrat: "))
    amount_due = float(input("Montant restant à payer: "))
    created_date = input("Date de création (AAAA-MM-JJ): ")
    is_signed = input("Le contrat est-il signé (0 = non, 1 = oui): ")

    cursor.execute("""
        INSERT INTO contract (client_id, commercial_id, total_amount, amount_due, created_date, is_signed)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (client_id, commercial_id, total_amount, amount_due, created_date, is_signed))

    conn.commit()
    print("Contrat créé avec succès !")
    conn.close()

# Fonction pour afficher tous les clients
def afficher_clients():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Liste des clients ===")
    cursor.execute("SELECT * FROM client")
    clients = cursor.fetchall()

    for client in clients:
        print(f"ID: {client[0]}, Nom: {client[1]}, Email: {client[2]}, Entreprise: {client[3]}")

    conn.close()

# Fonction pour afficher tous les contrats
def afficher_contrats():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Liste des contrats ===")
    cursor.execute("SELECT * FROM contract")
    contrats = cursor.fetchall()

    for contrat in contrats:
        print(f"ID: {contrat[0]}, Client ID: {contrat[1]}, Commercial ID: {contrat[2]}, Montant total: {contrat[3]}")

    conn.close()
