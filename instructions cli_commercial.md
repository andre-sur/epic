Parfait ! Voici un résumé clair et structuré des **commandes CLI pour les commerciaux**, suivi d’un exemple d'utilisation pour chaque commande.

---

## ✅ Résumé des commandes – Interface Commercial

### 1. `creer_client`

Crée un nouveau client et l’associe automatiquement au commercial connecté.

**Exemple :**

```bash
python commercial_cli.py creer_client
```

🔹 Vous devrez fournir :

* Nom, email, téléphone
* Entreprise, date de création
* Date du dernier contact

---

### 2. `modifier_client`

Modifie les informations d’un client existant **du commercial connecté uniquement**.

**Exemple :**

```bash
python commercial_cli.py modifier_client
```

🔹 Fournissez l’ID du client puis les nouvelles informations à modifier (ou laisser vide pour ne pas changer).

---

### 3. `afficher_clients`

Affiche la liste complète de vos clients.

**Exemple :**

```bash
python commercial_cli.py afficher_clients
```

🔹 Affiche l’ID, le nom, l’email, l’entreprise, la date de création et le dernier contact.

---

### 4. `creer_contrat`

Crée un contrat pour l’un de vos clients.

**Exemple :**

```bash
python commercial_cli.py creer_contrat
```

🔹 Vous devrez fournir :

* ID du client (qui vous est associé)
* Montant total, montant dû
* Date de création, si le contrat est signé (0 ou 1)

---

### 5. `afficher_contrats`

Affiche tous les contrats que vous avez créés.

**Exemple :**

```bash
python commercial_cli.py afficher_contrats
```

🔹 Affiche ID, client, montants, signature, date.

---

## 🧾 Exemple d'exécution typique :

```bash
> python commercial_cli.py creer_client
Nom complet du client : Jean Dupont
Email : jean@dupont.fr
Téléphone : 0612345678
Nom de l'entreprise : Dupont SARL
Date de création (AAAA-MM-JJ) : 2024-09-15
Date du dernier contact : 2025-01-12
✅ Client 'Jean Dupont' ajouté avec succès !
```

---

