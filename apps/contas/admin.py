"""Configuração do Django Admin para o app contas."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Admin customizado para Usuario."""

    # Campos exibidos na listagem
    list_display = [
        'cpf',
        'name',
        'email',
        'role',
        'status',
        'is_active',
        'created_at',
    ]
    list_filter = ['role', 'status', 'is_active', 'is_staff', 'created_at']
    search_fields = ['cpf', 'name', 'email']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    # Fieldsets para edição
    fieldsets = (
        (None, {'fields': ('cpf', 'password')}),
        ('Informações Pessoais', {'fields': ('name', 'email')}),
        ('Permissões do Sistema', {'fields': ('role', 'status')}),
        ('Permissões Django', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Datas', {
            'fields': ('last_login', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',),
        }),
    )

    # Fieldsets para criação
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('cpf', 'email', 'name', 'password1', 'password2', 'role'),
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'deleted_at', 'last_login']

    def get_queryset(self, request):
        """Inclui usuários soft-deleted no admin."""
        return Usuario.objects.with_deleted()
