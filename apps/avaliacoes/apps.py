"""Configuração do app avaliacoes."""
from django.apps import AppConfig


class AvaliacoesConfig(AppConfig):
    """Configuração do app avaliacoes - avaliação de submissões."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.avaliacoes'
    verbose_name = 'Avaliações'
