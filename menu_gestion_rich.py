import sqlite3
from datetime import datetime
from rich import print
from rich.console import Console
from rich.table import Table

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

def afficher_menu_gestion(utilisateur):
    if utilisateur["role"] != "gestion":
        print("[red]Accès refusé : ce menu est réservé aux gestionnaires.[/red]")
        return

    while True:
        console.print(f"\n[bold cyan]Menu Gestion – Bienvenue {utilisateur['name']}[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Option", justify="center")
        table.add_column("Description")
        table.add_row("1", "Créer un collaborateur")
        table.add_row("2", "Mettre à jour un collaborateur")
        table.add_row("3", "Supprimer un collaborateur")
        table.add_row("4", "Afficher tous les collaborateurs")
        table.add_row("5", "Créer un contrat")
        table.add_row("6", "Modifier un contrat")
        table.add_row("7", "Afficher événement non supporté")
        table.add_row("8", "Ajouter un support à un événement")
        console.print(table)

        choix = input("Veuillez entrer votre choix: ")

        if choix == "1":
            creer_collaborateur()
        elif choix == "2":
            mettre_a_jour_collaborateur()
        elif choix == "3":
            supprimer_collaborateur()
        elif choix == "4":
            afficher_collaborateurs()
        elif choix == "5":
            creer_contrat()
        elif choix == "6":
            modifier_contrat()
        elif choix == "7":
            afficher_events_sans_user()
        elif choix == "8":
            ajouter_support_evenement()
        else:
            print("[red]Choix invalide. Veuillez réessayer.[/red]")

def creer_contrat():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un contrat ===")

    # Demander et valider le client
    while True:
        client_id = input("ID du client : ")
        cursor.execute("SELECT full_name FROM client WHERE id = ?", (client_id,))
        client = cursor.fetchone()
        if client:
            print(f"Client trouvé : {client[0]}")
            break
        else:
            print("Client non trouvé, veuillez réessayer.")

    # Demander et valider le commercial
    while True:
        commercial_id = input("ID du commercial : ")
        cursor.execute("SELECT name, role FROM user WHERE id = ?", (commercial_id,))
        commercial = cursor.fetchone()
        if commercial:
            if commercial[1] == "commercial":
                print(f"Commercial trouvé : {commercial[0]}")
                break
            else:
                print("L'utilisateur n'a pas le rôle commercial, veuillez réessayer.")
        else:
            print("Commercial non trouvé, veuillez réessayer.")
    # Ensuite, demander les autres infos du contrat
    while True:
        montant_str = input("Montant total du contrat: ").strip()
        if montant_str:
            try:
                total_amount = float(montant_str)
                break
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        else:
            print("Ce champ ne peut pas être vide.")

    while True:
        amount_due_str = input("Montant restant à payer: ").strip()
        if amount_due_str:
            try:
                amount_due = float(amount_due_str)
                break
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        else:
            print("Ce champ ne peut pas être vide.")


    while True:
        created_date = input("Date de création (AAAA-MM-JJ): ").strip()
        if created_date:
            try:
                # On essaie de parser pour vérifier le format
                datetime.strptime(created_date, "%Y-%m-%d")
                break
            except ValueError:
                print("Format de date invalide. Veuillez entrer la date au format AAAA-MM-JJ.")
        else:
            print("Ce champ ne peut pas être vide.")

    while True:
        is_signed = input("Le contrat est-il signé (0 = non, 1 = oui): ").strip()
        if is_signed in ('0', '1'):
            break
        else:
            print("Veuillez entrer 0 pour non ou 1 pour oui.")

    cursor.execute("""
        INSERT INTO contract (client_id, commercial_id, total_amount, amount_due, created_date, is_signed)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (client_id, commercial_id, total_amount, amount_due, created_date, is_signed))

    conn.commit()
    print("Contrat créé avec succès !")
    conn.close()

import sqlite3
from datetime import datetime

def modifier_contrat():
    conn = sqlite3.connect("epic_crm.db")
    cursor = conn.cursor()

    contract_id = input("ID du contrat à modifier: ").strip()

    cursor.execute("""
        SELECT id, client_id, commercial_id, total_amount, amount_due, created_date, is_signed
        FROM contract
        WHERE id = ?
    """, (contract_id,))
    contrat = cursor.fetchone()

    if contrat is None:
        print("❌ Contrat non trouvé.")
        return

    # contrat = (id, client_id, commercial_id, total_amount, amount_due, created_date, is_signed)
    print("\n--- Modification du contrat ---")

    # total_amount
    while True:
        new_total = input(f"Montant total du contrat [{contrat[3]}]: ").strip()
        if new_total == "":
            total_amount = contrat[3]
            break
        try:
            total_amount = float(new_total)
            break
        except ValueError:
            print("Veuillez entrer un nombre valide.")

    # amount_due
    while True:
        new_due = input(f"Montant restant à payer [{contrat[4]}]: ").strip()
        if new_due == "":
            amount_due = contrat[4]
            break
        try:
            amount_due = float(new_due)
            break
        except ValueError:
            print("Veuillez entrer un nombre valide.")

    # created_date
    while True:
        new_date = input(f"Date de création [{contrat[5]}] (AAAA-MM-JJ): ").strip()
        if new_date == "":
            created_date = contrat[5]
            break
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
            created_date = new_date
            break
        except ValueError:
            print("Format invalide. Utilisez AAAA-MM-JJ.")

    # is_signed
    while True:
        new_signed = input(f"Le contrat est-il signé [{contrat[6]}] (0 = non, 1 = oui): ").strip()
        if new_signed == "":
            is_signed = contrat[6]
            break
        if new_signed in ("0", "1"):
            is_signed = int(new_signed)
            break
        else:
            print("Veuillez entrer 0 ou 1.")

    # Mettre à jour le contrat
    cursor.execute("""
        UPDATE contract
        SET total_amount = ?, amount_due = ?, created_date = ?, is_signed = ?
        WHERE id = ?
    """, (total_amount, amount_due, created_date, is_signed, contract_id))

    conn.commit()
    conn.close()

    print("\n✅ Contrat mis à jour avec succès !")

# Exemple d'appel
if __name__ == "__main__":
    modifier_contrat()



def creer_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un collaborateur ===")
    name = input("Nom du collaborateur: ")
    email = input("Email: ")
    password = input("Mot de passe: ")
    role = input("Rôle (gestion, commercial, support): ").strip().lower()

    if role not in ["gestion", "commercial", "support"]:
        print("[red]Rôle invalide.[/red]")
        conn.close()
        return

    cursor.execute("INSERT INTO user (name, email, password, role) VALUES (?, ?, ?, ?)", (name, email, password, role))
    conn.commit()
    print("[green]Collaborateur ajouté avec succès ![/green]")
    conn.close()

def supprimer_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()

    id_ = input("ID du collaborateur à supprimer: ")

    # Vérifier l'existence
    cursor.execute("SELECT id, name, email, role FROM user WHERE id = ?", (id_,))
    user = cursor.fetchone()

    if not user:
        print("[red]Aucun collaborateur avec cet ID.[/red]")
        conn.close()
        return

    # Afficher récapitulatif
    print(f"Collaborateur trouvé :")
    print(f"Nom : {user[1]}")
    print(f"Email : {user[2]}")
    print(f"Rôle : {user[3]}")

    confirmation = input("Confirmez-vous la suppression ? (oui/non) : ").strip().lower()
    if confirmation == "oui":
        cursor.execute("DELETE FROM user WHERE id = ?", (id_,))
        conn.commit()
        print("[green]Collaborateur supprimé avec succès ![/green]")
    else:
        print("[yellow]Suppression annulée.[/yellow]")

    conn.close()


def mettre_a_jour_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Modification d'un collaborateur ===")
    id_ = input("ID du collaborateur à modifier: ")

    # Récupérer l'utilisateur
    cursor.execute("SELECT id, name, email, password, role FROM user WHERE id = ?", (id_,))
    user = cursor.fetchone()

    if not user:
        print("[red]Aucun collaborateur avec cet ID.[/red]")
        conn.close()
        return

    # user = (id, name, email, password, role)
    print(f"Nom actuel : {user[1]}")
    new_name = input("Nouveau nom (laisser vide pour conserver): ")
    if not new_name:
        new_name = user[1]

    print(f"Email actuel : {user[2]}")
    new_email = input("Nouvel email (laisser vide pour conserver): ")
    if not new_email:
        new_email = user[2]

    print("Mot de passe actuel : ******")
    new_password = input("Nouveau mot de passe (laisser vide pour conserver): ")
    if not new_password:
        new_password = user[3]

    # Mettre à jour la base
    cursor.execute("""
        UPDATE user SET name = ?, email = ?, password = ? WHERE id = ?
    """, (new_name, new_email, new_password, id_))
    conn.commit()
    print("[green]Collaborateur mis à jour avec succès ![/green]")

    conn.close()


def afficher_collaborateurs():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()

    if not users:
        print("[yellow]Aucun collaborateur trouvé.[/yellow]")
    else:
        table = Table(title="Collaborateurs")
        table.add_column("ID", justify="center")
        table.add_column("Nom", justify="left")
        table.add_column("Email", justify="left")
        table.add_column("Rôle", justify="center")

        for u in users:
            table.add_row(str(u[0]), u[1], u[2], u[4])

        console.print(table)

    conn.close()

def creer_evenement():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un événement ===")
    contract_id = input("ID du contrat lié: ")
    support_id = input("ID du support: ")

    cursor.execute("SELECT * FROM contract WHERE id = ?", (contract_id,))
    if not cursor.fetchone():
        print("[red]Contrat introuvable.[/red]")
        conn.close()
        return

    cursor.execute("SELECT * FROM user WHERE id = ? AND role = 'support'", (support_id,))
    if not cursor.fetchone():
        print("[red]Support introuvable.[/red]")
        conn.close()
        return

    start_date = input("Début (AAAA-MM-JJ HH:MM): ")
    end_date = input("Fin (AAAA-MM-JJ HH:MM): ")

    try:
        debut = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        fin = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        if fin <= debut:
            print("[red]La date de fin doit être après la date de début.[/red]")
            conn.close()
            return
    except ValueError:
        print("[red]Format de date invalide.[/red]")
        conn.close()
        return

    location = input("Lieu: ")
    attendees = int(input("Nombre de participants: "))
    notes = input("Notes: ")

    cursor.execute("""
        INSERT INTO event (contract_id, support_id, start_date, end_date, location, attendees, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)""", (contract_id, support_id, start_date, end_date, location, attendees, notes))

    conn.commit()
    print("[green]Événement ajouté avec succès ![/green]")
    conn.close()

def afficher_events_sans_user():
    conn = sqlite3.connect("epic_crm.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, contract_id, start_date, end_date, location, attendees, notes
        FROM event
        WHERE support_id IS NULL
    """)

    events = cursor.fetchall()

    if not events:
        print("Aucun événement sans utilisateur associé.")
    else:
        print("\nÉvénements sans utilisateur associé :\n")
        for ev in events:
            print(f"ID: {ev[0]}, Contrat: {ev[1]}, Du {ev[2]} au {ev[3]}, Lieu: {ev[4]}, Participants: {ev[5]}, Notes: {ev[6]}")

    conn.close()

def filtrer_evenements():
    conn = connect_db()
    cursor = conn.cursor()
    print("=== Filtrer les événements ===")
    filtre = input("Date minimale (AAAA-MM-JJ): ")

    try:
        datetime.strptime(filtre, "%Y-%m-%d")
    except ValueError:
        print("[red]Date invalide.[/red]")
        return

    cursor.execute("SELECT * FROM event WHERE start_date >= ?", (filtre,))
    events = cursor.fetchall()

    if not events:
        print("[yellow]Aucun événement trouvé pour cette date.[/yellow]")
    else:
        table = Table(title="Événements")
        table.add_column("ID")
        table.add_column("Contrat")
        table.add_column("Support")
        table.add_column("Début")
        table.add_column("Fin")
        table.add_column("Lieu")
        table.add_column("Participants")

        for e in events:
            table.add_row(str(e[0]), str(e[1]), str(e[2]), e[3], e[4], e[5], str(e[6]))

        console.print(table)

    conn.close()

import sqlite3

def ajouter_support_evenement():
    conn = sqlite3.connect("epic_crm.db")
    cursor = conn.cursor()

    # Lister d'abord les événements sans support pour aider le choix
    cursor.execute("""
        SELECT id, contract_id, start_date, end_date, location
        FROM event
        WHERE support_id IS NULL
    """)
    events = cursor.fetchall()

    if not events:
        print("✅ Tous les événements ont déjà un support associé.")
        conn.close()
        return

    print("\n=== Événements sans support ===")
    for ev in events:
        print(f"ID: {ev[0]} | Contrat: {ev[1]} | {ev[2]} → {ev[3]} | Lieu: {ev[4]}")

    # Demander à l'utilisateur de choisir un événement
    while True:
        try:
            event_id = int(input("\nID de l'événement à mettre à jour : ").strip())
            cursor.execute("SELECT id FROM event WHERE id = ? AND support_id IS NULL", (event_id,))
            if cursor.fetchone() is None:
                print("❌ Cet événement n'existe pas ou a déjà un support. Réessayez.")
            else:
                break
        except ValueError:
            print("❌ Veuillez entrer un nombre entier valide.")

    # Demander l'ID du support
    while True:
        try:
            support_id = int(input("ID de l'utilisateur à associer comme support : ").strip())
            # Vérifier que cet user existe et a bien le rôle 'support'
            cursor.execute("SELECT id FROM user WHERE id = ? AND role = 'support'", (support_id,))
            if cursor.fetchone() is None:
                print("❌ Utilisateur introuvable ou n'est pas un support. Réessayez.")
            else:
                break
        except ValueError:
            print("❌ Veuillez entrer un nombre entier valide.")

    # Mettre à jour l'événement
    try:
        cursor.execute("""
            UPDATE event
            SET support_id = ?
            WHERE id = ?
        """, (support_id, event_id))
        conn.commit()
        print(f"✅ Support (ID: {support_id}) ajouté à l'événement (ID: {event_id}).")
    except sqlite3.Error as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")

    conn.close()
