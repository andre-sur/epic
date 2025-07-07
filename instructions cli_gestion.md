Voici un **résumé clair et pratique** de chaque commande disponible dans l’interface CLI de gestion, avec des **exemples concrets** d’utilisation :

---

## ✅ Résumé des commandes – Interface Gestion

### 1. `creer_collaborateur`

Permet de créer un nouvel utilisateur dans le système avec un rôle spécifique.

**Exemple :**

```bash
python gestion_cli.py creer_collaborateur
```

🔹 Le système vous demandera :

* Nom complet
* Email
* Mot de passe (avec confirmation)
* Rôle (gestion, commercial, support)

---

### 2. `modifier_collaborateur`

Permet de modifier les informations d’un utilisateur existant (nom, email, mot de passe, rôle).

**Exemple :**

```bash
python gestion_cli.py modifier_collaborateur
```

🔹 Vous devez entrer l’ID du collaborateur, puis modifier les champs désirés (ou les laisser vides pour ne pas les changer).

---

### 3. `supprimer_collaborateur`

Supprime un utilisateur du système après confirmation.

**Exemple :**

```bash
python gestion_cli.py supprimer_collaborateur
```

🔹 Entrez l’ID du collaborateur à supprimer, puis confirmez.

---

### 4. `creer_contrat`

Crée un nouveau contrat pour un client et l’associe à un commercial.

**Exemple :**

```bash
python gestion_cli.py creer_contrat
```

🔹 Vous devrez fournir :

* ID du client
* ID du commercial
* Montant total et montant dû
* Date de création
* Indiquer si le contrat est signé (0 ou 1)

---

### 5. `modifier_contrat`

Modifie les informations d’un contrat existant (montants, statut signé).

**Exemple :**

```bash
python gestion_cli.py modifier_contrat
```

🔹 Fournissez l’ID du contrat, puis saisissez les nouvelles valeurs (ou laissez vide).

---

### 6. `afficher_evenements_non_assignes`

Affiche tous les événements qui n’ont pas encore de support attribué.

**Exemple :**

```bash
python gestion_cli.py afficher_evenements_non_assignes
```

🔹 Liste les événements sans technicien support.

---

### 7. `modifier_evenement`

Attribue un collaborateur support à un événement existant.

**Exemple :**

```bash
python gestion_cli.py modifier_evenement
```

🔹 Vous devrez indiquer :

* ID de l’événement
* ID du support (doit être un utilisateur avec le rôle `support`)

---

## 🧾 Exemple d'exécution typique :

```bash
> python gestion_cli.py creer_collaborateur
Nom complet du collaborateur : Jeanne Martin
Email : jeanne@epic.com
Mot de passe : ******
Confirmation : ******
Rôle (gestion, commercial, support) : support
✅ Collaborateur 'Jeanne Martin' créé avec succès !
```


