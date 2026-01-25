"""Configuração do Django Admin para o app core."""
from django.contrib import admin

from .models import LogAuditoria


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    """Admin para LogAuditoria."""

    list_display = [
        'id',
        'usuario',
        'acao',
        'entidade',
        'entidade_id',
        'created_at',
    ]
    list_filter = ['acao', 'entidade', 'created_at']
    search_fields = ['usuario__name', 'usuario__cpf', 'entidade']
    readonly_fields = [
        'usuario',
        'acao',
        'entidade',
        'entidade_id',
        'dados_anteriores',
        'dados_novos',
        'ip_address',
        'user_agent',
        'created_at',
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    def has_add_permission(self, request):
        """Logs são criados programaticamente, não pelo admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Logs são imutáveis."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Logs não podem ser deletados pelo admin."""
        return False
