#!/usr/bin/env bash
set -o errexit

# Em deploy, garantir uso das configurações de produção também nos comandos do manage.py.
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings.production}

python manage.py collectstatic --no-input
python manage.py migrate --no-input
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --access-logfile - --error-logfile -
