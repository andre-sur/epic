import matplotlib.pyplot as plt
import networkx as nx

# Initialisation du graphe orienté
G = nx.DiGraph()

# Tables et colonnes
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

# Ajout des nœuds avec labels
for table, fields in tables.items():
    label = f"{table}\n" + "\n".join(fields)
    G.add_node(table, label=label)

# Relations entre les tables
relations = [
    ("client", "user"),
    ("contract", "client"),
    ("contract", "user"),
    ("event", "contract"),
    ("event", "user")
]
G.add_edges_from(relations)

# Utilise une disposition circulaire compacte
pos = nx.shell_layout(G)

# Dessiner les arêtes et les nœuds
plt.figure(figsize=(10, 7))
nx.draw_networkx_edges(G, pos, edge_color='gray', arrowstyle='-|>', arrowsize=18)
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=3000)
nx.draw_networkx_labels(G, pos, labels={t: t for t in tables}, font_size=9, font_weight='bold')

# Ajouter les détails des tables
for table, (x, y) in pos.items():
    label = G.nodes[table]["label"]
    plt.text(x, y - 0.08, label, fontsize=8, ha='center', va='top',
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3', alpha=0.9))

plt.title("Modèle relationnel EPIC CRM (compact)", fontsize=13, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.show()
