FROM python:3.11-slim

# Prévenir le buffering et l'écriture des fichiers .pyc
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Créer et utiliser le répertoire de travail /app
WORKDIR /app

# Installer les dépendances nécessaires pour psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copier et installer les dépendances Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application dans le conteneur
COPY . /app/

# Ajouter le script d'initialisation
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Exposer le port 8000 pour l'application Django
EXPOSE 8000

# Utiliser le script d'initialisation comme point d'entrée
ENTRYPOINT ["docker-entrypoint.sh"]

# Commande par défaut pour démarrer le serveur Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
