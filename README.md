
(Projet en cours d’améliorations)

**House brain** est un projet domotique Python/Django basé sur un Raspberry qui sera dans un premier temps chargé de la gestion du chauffage.

Le raspberry est connecté à des sondes de températures, aux commandes des radiateurs et à la téléinformation EDF. Il joue également le rôle de serveur.

L'interface utilisateur est une application Django

Celery est en charge des tâches périodiques (relevé des températures, de la télé information, et surveillance de la puissance utilisée pour le délestage)


Framework Web : Django

Base de données : PostgreSQL

Serveur Web : Nginx

Serveur d'application WSGI : Gunicron

Système de contrôle de processus : Supervisor

Planificateur de tâches périodiques : Django Celery beat

Broker Celery : Redis

15/11/2021:

Accès de démo ici : <http://housebrain.ddns.net>
