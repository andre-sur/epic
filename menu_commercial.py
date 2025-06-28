import sqlite3

# Connexion à la base de données
def connect_db():
    return sqlite3.connect('epic_events.db')


# Fonction pour afficher le menu commercial (avec utilisateur connecté)
def afficher_menu_commercial(utilisateur):
    while True:
        print(f"\n=== Menu Commercial – Bienvenue {utilisateur['name']} ===")
        print("1. Créer un client")
        print("2. Modifier un client")
        print("3. Créer un contrat")
        print("4. Afficher vos clients")
        print("5. Afficher vos contrats")
        print("6. Retour au menu principal")

        choix = input("Veuillez entrer votre choix: ")

        if choix == '1':
            creer_client(utilisateur)
        elif choix == '2':
            modifier_client(utilisateur)
        elif choix == '3':
            creer_contrat(utilisateur)
        elif choix == '4':
            afficher_clients(utilisateur)
        elif choix == '5':
            afficher_contrats(utilisateur)
        elif choix == '6':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")


# Fonction pour créer un client
def creer_client(utilisateur):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un client ===")
    full_name = input("Nom complet du client: ")
    email = input("Email du client: ")
    phone = input("Numéro de téléphone du client: ")
    company_name = input("Nom de l'entreprise: ")
    created_date = input("Date de création (AAAA-MM-JJ): ")
    last_contact_date = input("Date du dernier contact (AAAA-MM-JJ): ")
    commercial_id = utilisateur['id']  # Récupéré automatiquement

    cursor.execute("""
        INSERT INTO client (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id))

    conn.commit()
    print("Client ajouté avec succès !")
    conn.close()


# Fonction pour modifier un client uniquement s'il est lié au commercial
def modifier_client(utilisateur):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Modification d'un client ===")
    client_id = input("ID du client à modifier: ")

    # Vérifie si le client existe
    cursor.execute("SELECT * FROM client WHERE id = ?", (client_id,))
    client_existe = cursor.fetchone()

    if not client_existe:
        print("Ce client n'existe pas.")
        conn.close()
        return

    # Vérifie que le client appartient bien à ce commercial
    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, utilisateur['id']))
    client = cursor.fetchone()

    if not client:
        print("Vous n'avez pas la permission de modifier ce client.")
        conn.close()
        return

    # Modification possible
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
def creer_contrat(utilisateur):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un contrat ===")
    client_id = input("ID du client associé au contrat: ")

    # Vérifie que le client est bien lié à ce commercial
    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, utilisateur['id']))
    client = cursor.fetchone()
    if not client:
        print("Ce client ne vous est pas associé. Vous ne pouvez pas créer de contrat pour lui.")
        conn.close()
        return

    commercial_id = utilisateur['id']
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


# Fonction pour afficher uniquement les clients du commercial
def afficher_clients(utilisateur):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Liste des clients ===")
    cursor.execute("SELECT * FROM client WHERE commercial_id = ?", (utilisateur['id'],))
    clients = cursor.fetchall()

    if not clients:
        print("Aucun client trouvé.")
    else:
        for client in clients:
            print(f"ID: {client[0]}, Nom: {client[1]}, Email: {client[2]}, Entreprise: {client[4]}")

    conn.close()



# Fonction pour afficher uniquement les contrats du commercial
def afficher_contrats(utilisateur):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Liste des contrats ===")
    cursor.execute("SELECT * FROM contract WHERE commercial_id = ?", (utilisateur['id'],))
    contrats = cursor.fetchall()

    if not contrats:
        print("Aucun contrat trouvé.")
    else:
        for contrat in contrats:
            print(f"ID: {contrat[0]}, Client ID: {contrat[1]}, Montant total: {contrat[3]}, Montant dû: {contrat[4]}, Signé: {'Oui' if contrat[6] else 'Non'}")

    conn.close()

