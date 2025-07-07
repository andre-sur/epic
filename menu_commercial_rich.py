import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

def afficher_menu_commercial(utilisateur):
    while True:
        console.clear()
        console.rule(f"[bold cyan]Menu Commercial – Bienvenue {utilisateur['name']}[/bold cyan]")

        table = Table(show_header=False, show_edge=False)
        table.add_row("1.", "Créer un client")
        table.add_row("2.", "Modifier un client")
        table.add_row("3.", "Créer un contrat")
        table.add_row("4.", "Afficher vos clients")
        table.add_row("5.", "Afficher vos contrats")
        table.add_row("6.", "Afficher les contrats impayés")
        table.add_row("7.", "Afficher les contrats non signés")
        table.add_row("8.", "Mise à jour d'un contrat")
        table.add_row("9.", "Créer un événement")
        console.print(table)

        choix = Prompt.ask("Veuillez entrer votre choix", choices=[str(i) for i in range(1,10)])

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
            display_contracts_overdue(utilisateur)
        elif choix == '7':
            display_contracts_not_signed(utilisateur)
        elif choix == '8':
            update_contract(utilisateur)
        elif choix == '9':
            create_event(utilisateur)

def creer_client(utilisateur):
    console.print("[bold green]=== Création d'un client ===[/bold green]")
    full_name = Prompt.ask("Nom complet du client")
    email = Prompt.ask("Email du client")
    phone = Prompt.ask("Numéro de téléphone du client")
    company_name = Prompt.ask("Nom de l'entreprise")
    created_date = Prompt.ask("Date de création (AAAA-MM-JJ)")
    last_contact_date = Prompt.ask("Date du dernier contact (AAAA-MM-JJ)")
    commercial_id = utilisateur['id']

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO client (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id))
    conn.commit()
    conn.close()

    console.print("[bold green]Client ajouté avec succès ![/bold green]")
    console.input("Appuyez sur Entrée pour continuer...")

def modifier_client(utilisateur):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Modification d'un client ===")
    client_id = input("ID du client à modifier: ").strip()

    # Vérifie si le client existe
    cursor.execute("SELECT * FROM client WHERE id = ?", (client_id,))
    client_existe = cursor.fetchone()

    if not client_existe:
        print("❌ Ce client n'existe pas.")
        conn.close()
        return

    # Vérifie que le client appartient à ce commercial
    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, utilisateur['id']))
    client = cursor.fetchone()

    if not client:
        print("❌ Vous n'avez pas la permission de modifier ce client.")
        conn.close()
        return

    # Récupération des champs existants
    colonnes = [desc[0] for desc in cursor.description]
    client_data = dict(zip(colonnes, client))

    print("\n=== Laisser vide pour ne pas modifier ===")

    # Pour chaque champ, afficher valeur actuelle et proposer nouvelle
    champs_modifiables = ['full_name', 'email', 'phone', 'company_name', 'created_date', 'last_contact_date']
    nouvelles_valeurs = {}

    for champ in champs_modifiables:
        valeur_actuelle = client_data[champ] if client_data[champ] is not None else ''
        nouvelle_valeur = input(f"{champ.replace('_', ' ').capitalize()} [{valeur_actuelle}]: ").strip()
        if nouvelle_valeur != '':
            nouvelles_valeurs[champ] = nouvelle_valeur

    # Appliquer les mises à jour
    if nouvelles_valeurs:
        set_clause = ", ".join([f"{champ} = ?" for champ in nouvelles_valeurs])
        valeurs = list(nouvelles_valeurs.values()) + [client_id]
        cursor.execute(f"UPDATE client SET {set_clause} WHERE id = ?", valeurs)
        conn.commit()
        print("✅ Client modifié avec succès !")
    else:
        print("Aucune modification effectuée.")

    conn.close()

def creer_contrat(utilisateur):
    console.print("[bold green]=== Création d'un contrat ===[/bold green]")
    client_id = Prompt.ask("ID du client associé au contrat")

    conn = connect_db()
    cursor = conn.cursor()

    # Vérifier que client appartient au commercial
    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, utilisateur['id']))
    client = cursor.fetchone()
    if not client:
        console.print("[red]Ce client ne vous est pas associé. Vous ne pouvez pas créer de contrat pour lui.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    commercial_id = utilisateur['id']
    total_amount = float(Prompt.ask("Montant total du contrat"))
    amount_due = float(Prompt.ask("Montant restant à payer"))
    created_date = Prompt.ask("Date de création (AAAA-MM-JJ)")
    is_signed = Prompt.ask("Le contrat est-il signé ? (0 = non, 1 = oui)", choices=["0", "1"])

    cursor.execute("""
        INSERT INTO contract (client_id, commercial_id, total_amount, amount_due, created_date, is_signed)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (client_id, commercial_id, total_amount, amount_due, created_date, int(is_signed)))

    conn.commit()
    conn.close()

    console.print("[bold green]Contrat créé avec succès ![/bold green]")
    console.input("Appuyez sur Entrée pour continuer...")

def afficher_clients(utilisateur):
    console.print("[bold green]=== Liste des clients ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, email, company_name FROM client WHERE commercial_id = ?", (utilisateur['id'],))
    clients = cursor.fetchall()
    conn.close()

    if not clients:
        console.print("[yellow]Aucun client trouvé.[/yellow]")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Nom complet")
        table.add_column("Email")
        table.add_column("Entreprise")

        for c in clients:
            table.add_row(str(c[0]), c[1], c[2], c[3])

        console.print(table)

    console.input("Appuyez sur Entrée pour continuer...")

def afficher_contrats(utilisateur):
    console.print("[bold green]=== Liste des contrats ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, client_id, total_amount, amount_due, is_signed FROM contract WHERE commercial_id = ?", (utilisateur['id'],))
    contrats = cursor.fetchall()
    conn.close()

    if not contrats:
        console.print("[yellow]Aucun contrat trouvé.[/yellow]")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Client ID", style="dim", width=10)
        table.add_column("Montant total", justify="right")
        table.add_column("Montant dû", justify="right")
        table.add_column("Signé", justify="center")

        for c in contrats:
            signe = "[green]Oui[/green]" if c[4] else "[red]Non[/red]"
            table.add_row(str(c[0]), str(c[1]), f"{c[2]:.2f} €", f"{c[3]:.2f} €", signe)

        console.print(table)

    console.input("Appuyez sur Entrée pour continuer...")

# Exemple d'appel (à remplacer par l'utilisateur connecté réel)
if __name__ == "__main__":
    utilisateur_exemple = {"id": 1, "name": "André"}
    afficher_menu_commercial(utilisateur_exemple)

def display_contracts_overdue(utilisateur):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Contrats avec montant restant à payer > 0 ===")
    cursor.execute("""
        SELECT c.id, c.client_id, c.total_amount, c.amount_due, c.created_date, c.is_signed, cl.full_name
        FROM contract c
        JOIN client cl ON c.client_id = cl.id
        WHERE c.amount_due > 0
        ORDER BY c.created_date DESC
    """)
    contrats = cursor.fetchall()

    if not contrats:
        print("✅ Tous les contrats sont soldés !")
    else:
        for contrat in contrats:
            print(f"""
Contrat ID: {contrat[0]}
Client ID: {contrat[1]} ({contrat[6]})
Montant total: {contrat[2]}
Montant restant à payer: {contrat[3]}
Date de création: {contrat[4]}
Signé: {'Oui' if contrat[5] else 'Non'}
""")
    conn.close()

def display_contracts_not_signed(utilisateur):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Contrats non signés liés au commercial ===")
    cursor.execute("""
        SELECT c.id, c.client_id, c.total_amount, c.amount_due, c.created_date, cl.full_name
        FROM contract c
        JOIN client cl ON c.client_id = cl.id
        WHERE c.is_signed = 0
          AND c.commercial_id = ?
        ORDER BY c.created_date DESC
    """, (utilisateur['id'],))
    contrats = cursor.fetchall()

    if not contrats:
        print("✅ Aucun contrat non signé lié à vous.")
    else:
        for contrat in contrats:
            print(f"""
Contrat ID: {contrat[0]}
Client ID: {contrat[1]} ({contrat[5]})
Montant total: {contrat[2]}
Montant restant à payer: {contrat[3]}
Date de création: {contrat[4]}
Signé: Non
""")
    conn.close()

def update_contract(utilisateur):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Modification d'un contrat ===")
    contrat_id = input("Numéro du contrat à modifier : ").strip()

    # Vérifier que le contrat existe et appartient au commercial
    cursor.execute("""
        SELECT id, client_id, commercial_id, total_amount, amount_due, created_date, is_signed
        FROM contract
        WHERE id = ? AND commercial_id = ?
    """, (contrat_id, utilisateur['id']))
    contrat = cursor.fetchone()

    if not contrat:
        print("❌ Contrat introuvable ou non lié à vous.")
        conn.close()
        return

    colonnes = ['id', 'client_id', 'commercial_id', 'total_amount', 'amount_due', 'created_date', 'is_signed']
    contrat_data = dict(zip(colonnes, contrat))

    print("\n=== Laisser vide pour ne rien modifier ===")

    # Pour client_id, on peut afficher l'id mais généralement pas modifier ici (car FK)
    # Si tu veux, je peux ajouter la modif client_id aussi, mais souvent on ne change pas ça.
    # Je propose de ne modifier que : total_amount, amount_due, created_date, is_signed

    # total_amount (float)
    while True:
        valeur = input(f"Montant total [{contrat_data['total_amount']}]: ").strip()
        if valeur == '':
            total_amount = contrat_data['total_amount']
            break
        try:
            total_amount = float(valeur)
            break
        except ValueError:
            print("❌ Montant invalide, veuillez entrer un nombre.")

    # amount_due (float)
    while True:
        valeur = input(f"Montant restant à payer [{contrat_data['amount_due']}]: ").strip()
        if valeur == '':
            amount_due = contrat_data['amount_due']
            break
        try:
            amount_due = float(valeur)
            break
        except ValueError:
            print("❌ Montant invalide, veuillez entrer un nombre.")

    # created_date (texte - format AAAA-MM-JJ)
    while True:
        valeur = input(f"Date de création [{contrat_data['created_date']}]: ").strip()
        if valeur == '':
            created_date = contrat_data['created_date']
            break
        # Optionnel : vérifier format date
        import datetime
        try:
            datetime.datetime.strptime(valeur, "%Y-%m-%d")
            created_date = valeur
            break
        except ValueError:
            print("❌ Format date invalide. Utilisez AAAA-MM-JJ.")

    # is_signed (0 ou 1)
    while True:
        valeur = input(f"Contrat signé ? (0 = non, 1 = oui) [{contrat_data['is_signed']}]: ").strip()
        if valeur == '':
            is_signed = contrat_data['is_signed']
            break
        if valeur in ('0', '1'):
            is_signed = int(valeur)
            break
        else:
            print("❌ Veuillez entrer 0 ou 1.")

    # Mise à jour
    try:
        cursor.execute("""
            UPDATE contract
            SET total_amount = ?, amount_due = ?, created_date = ?, is_signed = ?
            WHERE id = ?
        """, (total_amount, amount_due, created_date, is_signed, contrat_id))
        conn.commit()
        print("✅ Contrat modifié avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors de la modification : {e}")

    conn.close()

def create_event(utilisateur):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un nouvel événement ===")

    # Demander l'ID du contrat
    contrat_id = input("Numéro du contrat associé : ").strip()

    # Vérifier que le contrat existe et appartient bien au commercial connecté
    cursor.execute("""
        SELECT id FROM contract WHERE id = ? AND commercial_id = ?
    """, (contrat_id, utilisateur['id']))
    contrat = cursor.fetchone()

    if not contrat:
        print("❌ Contrat introuvable ou non lié à vous.")
        conn.close()
        return

    # support_id : optionnel
    support_id = input("ID du support technique (laisser vide si aucun) : ").strip()
    if support_id == '':
        support_id = None
    else:
        # Vérifier si le support existe
        cursor.execute("SELECT id FROM user WHERE id = ?", (support_id,))
        if not cursor.fetchone():
            print("❌ Support introuvable, champ ignoré.")
            support_id = None

    # start_date
    while True:
        start_date = input("Date de début (AAAA-MM-JJ) : ").strip()
        try:
            import datetime
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
            break
        except ValueError:
            print("❌ Format invalide. Utilisez AAAA-MM-JJ.")

    # end_date
    while True:
        end_date = input("Date de fin (AAAA-MM-JJ) : ").strip()
        try:
            datetime.datetime.strptime(end_date, "%Y-%m-%d")
            break
        except ValueError:
            print("❌ Format invalide. Utilisez AAAA-MM-JJ.")

    # location
    location = input("Lieu de l'événement : ").strip()

    # attendees (nombre de participants)
    while True:
        attendees_input = input("Nombre de participants : ").strip()
        if attendees_input == '':
            attendees = None
            break
        try:
            attendees = int(attendees_input)
            break
        except ValueError:
            print("❌ Veuillez entrer un nombre.")

    # notes
    notes = input("Notes (description, détails...) : ").strip()

    # Insertion
    try:
        cursor.execute("""
            INSERT INTO event (contract_id, support_id, start_date, end_date, location, attendees, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (contrat_id, support_id, start_date, end_date, location, attendees, notes))
        conn.commit()
        print("✅ Événement créé avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors de la création : {e}")

    conn.close()


