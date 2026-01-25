"""Configuração do app editais."""
from django.apps import AppConfig


class EditaisConfig(AppConfig):
    """Configuração do app editais - gerenciamento de editais."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.editais'
    verbose_name = 'Editais'
