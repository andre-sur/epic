import sqlite3

# Connexion à la base de données
def connect_db():
    return sqlite3.connect('epic_events.db')

# Menu principal pour les supports
def afficher_menu_support():
    while True:
        print("\n=== Menu Support ===")
        print("1. Voir les événements qui me sont attribués")
        print("2. Mettre à jour un événement")
        print("3. Afficher tous les événements")
        print("4. Retour au menu principal")

        choix = input("Veuillez entrer votre choix: ")

        if choix == '1':
            voir_evenements_attribues()
        elif choix == '2':
            mettre_a_jour_evenement()
        elif choix == '3':
            afficher_evenements()
        elif choix == '4':
            break  # Retourne au menu principal
        else:
            print("Choix invalide. Veuillez réessayer.")

# Fonction pour voir les événements attribués au support
def voir_evenements_attribues():
    support_id = 1  # ID de l'utilisateur actuellement connecté (assurez-vous de le gérer dans un vrai cas)

    conn = connect_db()
    cursor = conn.cursor()

    print(f"=== Événements attribués au support ID: {support_id} ===")
    cursor.execute("SELECT * FROM event WHERE support_id = ?", (support_id,))
    events = cursor.fetchall()

    for event in events:
        print(f"ID: {event[0]}, Contract ID: {event[1]}, Start: {event[3]}, Location: {event[5]}")

    conn.close()

# Fonction pour mettre à jour un événement
def mettre_a_jour_evenement():
    event_id = input("ID de l'événement à mettre à jour: ")

    conn = connect_db()
    cursor = conn.cursor()

    print("=== Mise à jour d'un événement ===")
    start_date = input("Nouvelle date de début (laisser vide pour ne pas modifier): ")
    end_date = input("Nouvelle date de fin (laisser vide pour ne pas modifier): ")
    location = input("Nouveau lieu (laisser vide pour ne pas modifier): ")

    # Mettre à jour uniquement les champs non vides
    if start_date:
        cursor.execute("UPDATE event SET start_date = ? WHERE id = ?", (start_date, event_id))
    if end_date:
        cursor.execute("UPDATE event SET end_date = ? WHERE id = ?", (end_date, event_id))
    if location:
        cursor.execute("UPDATE event SET location = ? WHERE id = ?", (location, event_id))

    conn.commit()
    print("Événement mis à jour avec succès !")
    conn.close()

# Fonction pour afficher tous les événements
def afficher_evenements():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Liste de tous les événements ===")
    cursor.execute("SELECT * FROM event")
    events = cursor.fetchall()

    for event in events:
        print(f"ID: {event[0]}, Contract ID: {event[1]}, Start: {event[3]}, Location: {event[5]}")

    conn.close()
