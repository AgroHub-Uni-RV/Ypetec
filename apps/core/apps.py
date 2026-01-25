"""Configuração do app core."""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuração do app core - utilitários e modelos base."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Núcleo'
