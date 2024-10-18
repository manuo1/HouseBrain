#!/bin/sh

# Si le fichier .env n'existe pas créer depuis .env.exemple
if [ ! -f ".env" ]; then
    echo ".env file not found. Copying .env.example to .env..."
    cp .env.example .env
    echo "!!! [WARNING]: .env was created from .env.example! Please update the .env file with the correct secure values."
else
    echo ".env file already exists. No need to create it."
fi

#!/bin/bash

# Vérifier si le service est Django ou autre
if [ "$1" = "django" ]; then
    echo "Applying database migrations..."
    python manage.py migrate --noinput

    echo "Collecting static files..."
    python manage.py collectstatic --noinput

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

elif [ "$1" = "celery" ]; then
    # Pour Celery, ne faire que lancer le worker
    echo "Starting Celery worker..."
    exec celery -A core worker --loglevel=info
else
    # Pour d'autres services éventuels, démarrer sans migrations ni autres étapes Django spécifiques
    exec "$@"
fi
