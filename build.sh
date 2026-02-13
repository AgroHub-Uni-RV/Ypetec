#!/usr/bin/env bash
set -o errexit

# Mantido apenas para compatibilidade local.
# Não executar migrations/collectstatic em build para evitar dependência de segredos em build-time.
pip install -r requirements.txt
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic --no-input
