import click
import sqlite3
from rich.console import Console
from rich.table import Table

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

@click.group()
def client():
    """Commandes pour gérer les clients (réservé aux commerciaux)"""
    pass

@client.command()
@click.option('--user-id', required=True, type=int, help='ID du commercial connecté')
def display(user_id):
    """Afficher vos clients"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, email, company_name FROM client WHERE commercial_id = ?", (user_id,))
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

@client.command()
@click.option('--user-id', required=True, type=int, help='ID du commercial connecté')
@click.option('--client-id', prompt='ID du client à modifier', type=int)
def update(user_id, client_id):
    """Modifier un client (réservé au commercial propriétaire)"""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, user_id))
    client = cursor.fetchone()

    if not client:
        console.print("[red]❌ Client introuvable ou non lié à vous.[/red]")
        conn.close()
        return

    colonnes = [desc[0] for desc in cursor.description]
    client_data = dict(zip(colonnes, client))

    console.print("[bold green]=== Modifier le client ===[/bold green]")
    console.print("Laisser vide pour ne rien changer.")

    champs_modifiables = ['full_name', 'email', 'phone', 'company_name', 'created_date', 'last_contact_date']
    nouvelles_valeurs = {}

    for champ in champs_modifiables:
        valeur_actuelle = client_data.get(champ, '') or ''
        nouvelle_valeur = click.prompt(f"{champ.replace('_', ' ').capitalize()} [{valeur_actuelle}]", default='', show_default=False)
        if nouvelle_valeur != '':
            nouvelles_valeurs[champ] = nouvelle_valeur

    if nouvelles_valeurs:
        set_clause = ", ".join([f"{champ} = ?" for champ in nouvelles_valeurs])
        valeurs = list(nouvelles_valeurs.values()) + [client_id]
        cursor.execute(f"UPDATE client SET {set_clause} WHERE id = ?", valeurs)
        conn.commit()
        console.print("[green]✅ Client modifié avec succès.[/green]")
    else:
        console.print("[yellow]Aucune modification effectuée.[/yellow]")

    conn.close()
@client.command()
@click.option('--user-id', required=True, type=int, help='ID du commercial connecté')
@click.option('--client-id', prompt='ID du client à supprimer', type=int)
def delete(user_id, client_id):
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Suppression d'un client ===")

    # même requête que dans update
    cursor.execute(
        "SELECT id, full_name, email FROM client WHERE id = ? AND commercial_id = ?",
        (client_id, user_id)
    )
    client = cursor.fetchone()

    if not client:
        print("❌ Ce client n'existe pas ou ne vous appartient pas.")
        conn.close()
        return

    # affichage du nom et email comme dans update
    print(f"Prénom : {client[1]}")
    print(f"Email : {client[2]}")

    confirmation = input("⚠️ Êtes-vous sûr de vouloir supprimer ce client ? (o/N): ").strip().lower()

    if confirmation == 'o':
        cursor.execute("DELETE FROM client WHERE id = ?", (client_id,))
        conn.commit()
        print("✅ Client supprimé avec succès.")
    else:
        print("❌ Suppression annulée.")

    conn.close()
