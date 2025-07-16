
Voir requirements.txt pour les dépendances

LANCER LE CRM
Sur le terminal > python GEN_MENU.python

il existe un compte : 
admin@admin.fr
mot de passe : admin
(pour utiliser le CRM directement)

>aucun administrateur n'existe : il faut le créer. Terminal > python add_admin_initialisation.py

> pas de session ouverte en cours, le programme demande email et mot de passe.

> une session est déjà ouverte (tilisateur connecté et token enregistré) : un menu s'affiche 
dont le contenu dépend du rôle de l'utilisateur connecté (selon les autorisations affectées à chaque rôle)