#!/bin/sh

# Si le fichier .env n'existe pas créer depuis .env.exemple
if [ ! -f ".env" ]; then
    echo ".env file not found. Copying .env.example to .env..."
    cp .env.example .env
    echo "Warning: .env was created from .env.exemple ! Please update the .env file with the correct values. !"
fi

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
