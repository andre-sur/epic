# users_crud.py
import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import bcrypt

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

def create_user():
    console.print("[bold green]=== Création d'un utilisateur ===[/bold green]")
    name = Prompt.ask("Nom")
    email = Prompt.ask("Email")
    password = Prompt.ask("Mot de passe", password=True)
    role = Prompt.ask("Rôle", choices=['gestion', 'commercial', 'support'])

    # Hash du mot de passe
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO user (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (name, email, hashed_password.decode('utf-8'), role))
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

    new_password = Prompt.ask("Nouveau mot de passe (laisser vide si inchangé)", default=None, password=True)
    hashed_password = None

    if new_password:
        confirm_password = Prompt.ask("Confirmez le nouveau mot de passe", password=True)
        if new_password != confirm_password:
            console.print("[red]❌ Les mots de passe ne correspondent pas.[/red]")
            conn.close()
            console.input("Appuyez sur Entrée pour continuer...")
            return
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
