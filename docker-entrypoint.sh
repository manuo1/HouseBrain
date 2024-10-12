#!/bin/sh

# Fonction pour vérifier la connexion à PostgreSQL
postgres_ready() {
python << END
import sys
import psycopg2
from os import getenv

try:
    conn = psycopg2.connect(
        dbname=getenv("POSTGRES_DB"),
        user=getenv("POSTGRES_USER"),
        password=getenv("POSTGRES_PASSWORD"),
        host="postgres"
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

# Attendre que PostgreSQL soit prêt
until postgres_ready; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

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
