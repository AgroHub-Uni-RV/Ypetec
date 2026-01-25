"""Configuração do Django Admin para o app publicacoes."""
from django.contrib import admin

from .models import Publicacao


@admin.register(Publicacao)
class PublicacaoAdmin(admin.ModelAdmin):
    """Admin para Publicacao."""

    list_display = [
        'id',
        'projeto',
        'ativo',
        'destaque',
        'publicado_por',
        'publicado_em',
    ]
    list_filter = ['ativo', 'destaque', 'publicado_em']
    search_fields = ['projeto__titulo', 'descricao']
    readonly_fields = ['publicado_em']
    date_hierarchy = 'publicado_em'
    raw_id_fields = ['projeto', 'publicado_por']

    fieldsets = (
        (None, {'fields': ('projeto', 'logo', 'descricao')}),
        ('Exibição', {'fields': ('ativo', 'destaque')}),
        ('Metadados', {
            'fields': ('publicado_por', 'publicado_em'),
            'classes': ('collapse',),
        }),
    )
