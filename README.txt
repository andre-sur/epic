Utilisation du CRM


Fonctionnement 
- modèles en classes python
- structure du menu dans json (commands.json) : autorisation, intitulé
- choix CRUD : interface utilisateur (generic_prompt) : create, delete, update, display_all et display avec filtre paramétrable
- fonction CRUD : conversion données de classes vers SQL (generic_dao)
- équivalence champs de table et intitulé pour l'interface : fields.py

Voir requirements.txt pour les dépendances

LANCER LE CRM
Sur le terminal > python GEN_MENU.python

il existe un compte : 
admin@admin.fr
mot de passe : admin
(role de gestion)
(pour utiliser le CRM directement)

> si aucun administrateur n'existe : il faut le créer. Terminal > python add_admin_initialisation.py

> pas de session ouverte en cours, le programme demande email et mot de passe.

> une session est déjà ouverte (tilisateur connecté et token enregistré) : un menu s'affiche 
dont le contenu dépend du rôle de l'utilisateur connecté (selon les autorisations affectées à chaque rôle)