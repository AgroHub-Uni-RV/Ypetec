"""Configuração do Django Admin para o app avaliacoes."""
from django.contrib import admin

from .models import Avaliacao


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    """Admin para Avaliacao."""

    list_display = [
        'id',
        'submissao',
        'resultado',
        'avaliador',
        'avaliado_em',
    ]
    list_filter = ['resultado', 'avaliado_em']
    search_fields = [
        'submissao__projeto__titulo',
        'avaliador__name',
        'comentarios',
    ]
    readonly_fields = ['avaliado_em']
    date_hierarchy = 'avaliado_em'
    raw_id_fields = ['submissao', 'avaliador']

    fieldsets = (
        (None, {'fields': ('submissao', 'avaliador')}),
        ('Avaliação', {'fields': ('resultado', 'comentarios')}),
        ('Metadados', {
            'fields': ('avaliado_em',),
            'classes': ('collapse',),
        }),
    )
