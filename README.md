**Projet en cours de développement **

House brain est un projet domotique Python/Django basé sur un Raspberry qui sera dans un premier temps chargé de la gestion du chauffage.
Le raspberry est connecté à des sondes de températures, aux commandes des radiateurs et à la télé information EDF.
L'interface utilisateur est une application Django
Celery est en charge des taches périodiques (relevé des températures et de la télé information, surveillance de la puissance utilisée)


Framework Web : Django
Base de données : PostgreSQL
Serveur Web : Nginx
Serveur d'application WSGI : Gunicron
Système de contrôle de processus : Supervisor
Planificateur de tâches périodiques : Django Celery beat
Broker Celery : Redis

27/09/2021:

  **Interface utilisateur**:
  app housebrain | Basic permet uniquement le login, l'accès à la console django admin et l'affichage des températures actuelles

  **Système d'authentification** :
  app authentication | fonctionnel depuis la console d'admin django

  **Chauffages** :
  app heaters | La liaison entre l'état du chauffage dans la base de données et l’état réel est opérationnelle, lorsque l'état du chauffage change dans la base de données l'état du chauffage change réellement.

  **Sondes de températures** :
  app sensors | Une tâche périodique celery effectue toute les 5 minutes un mesure des températures ainsi que leur mise à jour en base de données. Un historique des mesures de température est sauvegardé toutes les 30 minutes

  **Teleinformation** :
  app teleinformation | Une tâche périodique celery effectue toute les 15 secondes une lecture de la télé-information, elle contrôle la puissance disponible, enregistre en base les puissances trop faibles et déclenche si besoin l'arrêt de tous les radiateurs.
  Un historique des lectures de télé-information est sauvegardé toutes les 30 minutes


  **Suite**:
  Les tâches périodiques sont stables et efficaces le suivi est constant, pas d’erreur de mesures de températures ni de lecture de teleinfo. Même en cas de redémarrage système les tâches s'exécutent normalement au re-démarrage
  La prochaine étape de développement  est la planification des périodes de chauffage depuis un planning.
