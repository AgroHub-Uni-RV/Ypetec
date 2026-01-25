"""Configuração do app mentorias."""
from django.apps import AppConfig


class MentoriasConfig(AppConfig):
    """Configuração do app mentorias - solicitações e acompanhamento."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mentorias'
    verbose_name = 'Mentorias'
