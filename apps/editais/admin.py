"""Configuração do Django Admin para o app editais."""
from django.contrib import admin

from .models import Edital


@admin.register(Edital)
class EditalAdmin(admin.ModelAdmin):
    """Admin para Edital."""

    list_display = [
        'id',
        'titulo',
        'status',
        'inicio',
        'fim',
        'criado_por',
        'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['titulo', 'descricao']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    date_hierarchy = 'inicio'
    ordering = ['-inicio']
    raw_id_fields = ['criado_por']

    fieldsets = (
        (None, {'fields': ('titulo', 'descricao')}),
        ('Período', {'fields': ('inicio', 'fim', 'status')}),
        ('Metadados', {
            'fields': ('criado_por', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',),
        }),
    )
