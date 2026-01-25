"""Configuração do app contas."""
from django.apps import AppConfig


class ContasConfig(AppConfig):
    """Configuração do app contas - usuários e autenticação."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contas'
    verbose_name = 'Contas'
