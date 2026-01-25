"""Configuração do app projetos."""
from django.apps import AppConfig


class ProjetosConfig(AppConfig):
    """Configuração do app projetos - projetos, equipe e submissões."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.projetos'
    verbose_name = 'Projetos'
