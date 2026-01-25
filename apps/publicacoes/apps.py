"""Configuração do app publicacoes."""
from django.apps import AppConfig


class PublicacoesConfig(AppConfig):
    """Configuração do app publicacoes - vitrine pública."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.publicacoes'
    verbose_name = 'Publicações'
