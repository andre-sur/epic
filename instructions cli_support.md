Parfait ! Voici maintenant le résumé complet des **commandes CLI pour le rôle Support**, avec explications et exemples concrets :

---

## 🛠️ Résumé des commandes – Interface Support

Le rôle "support" permet de consulter les événements assignés ou non, et de les mettre à jour.

---

### 1. `afficher_evenements`

Affiche tous les événements **assignés au support connecté**.

**Exemple :**

```bash
python support_cli.py afficher_evenements
```

🔹 Affiche :

* ID de l’événement, client concerné
* Dates de début et fin
* Lieu, nombre de participants

---

### 2. `afficher_evenements_non_assignes`

Liste les événements **sans support technique assigné**.

**Exemple :**

```bash
python support_cli.py afficher_evenements_non_assignes
```

🔹 Utile pour les gestionnaires ou le support voulant se proposer.

---

### 3. `modifier_evenement`

Permet de **mettre à jour** certaines informations de l’événement **assigné au support connecté**, comme les dates, le lieu, ou le nombre de participants.

**Exemple :**

```bash
python support_cli.py modifier_evenement
```

🔹 Saisir l’ID de l’événement, puis renseigner :

* Nouvelle date de début / fin
* Nouveau lieu ou nombre de participants

---

## 🔄 Exemple d'utilisation typique :

```bash
> python support_cli.py afficher_evenements
=== Vos événements assignés ===
ID: 12, Client: Total Energy, Début: 2025-07-01, Fin: 2025-07-02, Lieu: Paris, Participants: 45
```

```bash
> python support_cli.py modifier_evenement
ID de l'événement à modifier : 12
Nouvelle date de début (AAAA-MM-JJ, vide = inchangé) : 2025-07-03
Nouvelle date de fin (AAAA-MM-JJ, vide = inchangé) :
Nouveau lieu (vide = inchangé) :
Nouveau nombre de participants (vide = inchangé) : 50
✅ Événement modifié avec succès !
```


