#!/bin/sh

# Si le fichier .env n'existe pas créer depuis .env.exemple
if [ ! -f ".env" ]; then
    echo ".env file not found. Copying .env.example to .env..."
    cp .env.example .env
    echo "Warning: .env was created from .env.example! Please update the .env file with the correct values."
else
    echo ".env file already exists. No need to create it."
fi

# Démarrer les migrations de la base de données
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collecte des fichiers statiques
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Créer un superutilisateur si nécessaire
echo "Checking for superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created.')
else:
    print('Superuser already exists.')
END

# Lancer le serveur Django
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000