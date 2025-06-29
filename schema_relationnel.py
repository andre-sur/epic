import matplotlib.pyplot as plt
import networkx as nx

# Initialisation du graphe orienté
G = nx.DiGraph()

# Dictionnaire des tables avec leurs champs et relations
tables = {
    "user": [
        "id (PK)", "name", "email", "password", "role [gestion|commercial|support]"
    ],
    "client": [
        "id (PK)", "full_name", "email", "phone", "company_name",
        "created_date", "last_contact_date", "commercial_id (FK → user.id)"
    ],
    "contract": [
        "id (PK)", "client_id (FK → client.id)", "commercial_id (FK → user.id)",
        "total_amount", "amount_due", "created_date", "is_signed [0|1]"
    ],
    "event": [
        "id (PK)", "contract_id (FK → contract.id)", "support_id (FK → user.id)",
        "start_date", "end_date", "location", "attendees", "notes"
    ]
}

# Ajout des nœuds
for table, fields in tables.items():
    label = f"{table}\n" + "\n".join(fields)
    G.add_node(table, label=label)

# Définition des relations (arêtes)
relations = [
    ("client", "user"),           # client.commercial_id → user.id
    ("contract", "client"),       # contract.client_id → client.id
    ("contract", "user"),         # contract.commercial_id → user.id
    ("event", "contract"),        # event.contract_id → contract.id
    ("event", "user")             # event.support_id → user.id
]

# Ajout des arêtes au graphe
G.add_edges_from(relations)

# Positionnement automatique des nœuds
pos = nx.spring_layout(G, seed=42)

# Dessin du graphe
plt.figure(figsize=(13, 9))
nx.draw_networkx_edges(G, pos, edge_color='gray', arrowstyle='-|>', arrowsize=20)
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=4500)
nx.draw_networkx_labels(G, pos, labels={t: t for t in tables}, font_weight='bold', font_size=11)

# Ajout des détails des tables sous forme de boîtes de texte
for table, (x, y) in pos.items():
    label = G.nodes[table]["label"]
    plt.text(x, y - 0.08, label, fontsize=9, ha='center', va='top',
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5', alpha=0.85))

plt.title("Modèle relationnel EPIC CRM", fontsize=15, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.show()
