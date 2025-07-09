import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import os
import bcrypt

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

def display_menu_users(utilisateur):
    if utilisateur['role'] != 'gestion':
        console.print("[red]❌ Accès refusé. Seuls les utilisateurs avec le rôle 'gestion' peuvent gérer les utilisateurs.[/red]")
        console.input("Appuyez sur Entrée pour continuer...")
        return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.rule("[bold cyan]Menu Gestion des utilisateurs[/bold cyan]")

        table = Table(show_header=False, show_edge=False)
        table.add_row("1.", "Créer un utilisateur")
        table.add_row("2.", "Modifier un utilisateur")
        table.add_row("3.", "Supprimer un utilisateur")
        table.add_row("4.", "Afficher les utilisateurs")
        table.add_row("5.", "Quitter le menu utilisateurs")
        console.print(table)

        choix = Prompt.ask("Choisissez une option", choices=["1", "2", "3", "4", "5"])

        if choix == '1':
            create_user()
        elif choix == '2':
            update_user()
        elif choix == '3':
            delete_user()
        elif choix == '4':
            display_users()
        elif choix == '5':
            break

def create_user():
    console.print("[bold green]=== Création d'un utilisateur ===[/bold green]")
    name = Prompt.ask("Nom")
    email = Prompt.ask("Email")
    password = Prompt.ask("Mot de passe")
    role = Prompt.ask("Rôle", choices=['gestion', 'commercial', 'support'])

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO user (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (name, email, password, role))
        conn.commit()
        console.print("[green]✅ Utilisateur créé avec succès ![/green]")
    except sqlite3.IntegrityError as e:
        console.print(f"[red]❌ Erreur lors de la création : {e}[/red]")
    finally:
        conn.close()
    console.input("Appuyez sur Entrée pour continuer...")

def update_user():
    console.print("[bold yellow]=== Modification d'un utilisateur ===[/bold yellow]")
    user_id = Prompt.ask("ID de l'utilisateur à modifier")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role FROM user WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        console.print("[red]❌ Utilisateur introuvable.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    colonnes = ['id', 'name', 'email', 'role']
    user_data = dict(zip(colonnes, user))

    console.print("Laisser vide pour conserver la valeur actuelle :")
    new_name = Prompt.ask(f"Nom [{user_data['name']}]", default=user_data['name'])
    new_email = Prompt.ask(f"Email [{user_data['email']}]", default=user_data['email'])
    new_role = Prompt.ask(f"Rôle [{user_data['role']}]", choices=['gestion', 'commercial', 'support'], default=user_data['role'])

    # Demander un nouveau mot de passe deux fois si l'utilisateur veut le changer
    new_password = Prompt.ask("Nouveau mot de passe (laisser vide si inchangé)", default=None, password=True)
    hashed_password = None

    if new_password:
        confirm_password = Prompt.ask("Confirmez le nouveau mot de passe", password=True)
        if new_password != confirm_password:
            console.print("[red]❌ Les mots de passe ne correspondent pas.[/red]")
            conn.close()
            console.input("Appuyez sur Entrée pour continuer...")
            return
        # Hasher le mot de passe avec bcrypt
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    try:
        if hashed_password:
            cursor.execute("""
                UPDATE user SET name=?, email=?, password=?, role=? WHERE id=?
            """, (new_name, new_email, hashed_password.decode('utf-8'), new_role, user_id))
        else:
            cursor.execute("""
                UPDATE user SET name=?, email=?, role=? WHERE id=?
            """, (new_name, new_email, new_role, user_id))
        conn.commit()
        console.print("[green]✅ Utilisateur modifié avec succès.[/green]")
    except sqlite3.IntegrityError as e:
        console.print(f"[red]❌ Erreur lors de la modification : {e}[/red]")
    finally:
        conn.close()
    console.input("Appuyez sur Entrée pour continuer...")


def delete_user():
    console.print("[bold red]=== Suppression d'un utilisateur ===[/bold red]")
    user_id = Prompt.ask("ID de l'utilisateur à supprimer")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM user WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        console.print("[red]❌ Utilisateur introuvable.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    confirm = Prompt.ask(f"Confirmer la suppression de l'utilisateur '{user[1]}' ? (o/n)", choices=['o', 'n'])
    if confirm == 'o':
        cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
        conn.commit()
        console.print("[green]✅ Utilisateur supprimé avec succès.[/green]")
    else:
        console.print("[yellow]Suppression annulée.[/yellow]")

    conn.close()
    console.input("Appuyez sur Entrée pour continuer...")

def display_users():
    console.print("[bold cyan]=== Liste des utilisateurs ===[/bold cyan]")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role FROM user")
    users = cursor.fetchall()
    conn.close()

    if not users:
        console.print("[yellow]Aucun utilisateur trouvé.[/yellow]")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Nom")
        table.add_column("Email")
        table.add_column("Rôle")
        for u in users:
            table.add_row(str(u[0]), u[1], u[2], u[3])
        console.print(table)
    console.input("Appuyez sur Entrée pour continuer...")

# Exemple d'appel (à adapter selon votre système d'authentification)
if __name__ == "__main__":
    utilisateur_exemple = {"id": 1, "name": "Admin", "role": "gestion"}
    afficher_menu_users(utilisateur_exemple)
