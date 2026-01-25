"""Configuração do Django Admin para o app mentorias."""
from django.contrib import admin

from .models import SolicitacaoMentoria


@admin.register(SolicitacaoMentoria)
class SolicitacaoMentoriaAdmin(admin.ModelAdmin):
    """Admin para SolicitacaoMentoria."""

    list_display = [
        'id',
        'projeto',
        'area',
        'status',
        'solicitante',
        'mentor',
        'created_at',
    ]
    list_filter = ['status', 'area', 'created_at']
    search_fields = [
        'projeto__titulo',
        'area',
        'solicitante__name',
        'mentor__name',
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['projeto', 'solicitante', 'mentor']

    fieldsets = (
        (None, {'fields': ('projeto', 'solicitante')}),
        ('Solicitação', {'fields': ('area', 'justificativa')}),
        ('Status', {'fields': ('status', 'mentor')}),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
