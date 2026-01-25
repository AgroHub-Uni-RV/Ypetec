"""Configuração do Django Admin para o app projetos."""
from django.contrib import admin

from .models import MembroEquipe, Projeto, RelatorioProgresso, Submissao


class MembroEquipeInline(admin.TabularInline):
    """Inline para membros da equipe."""

    model = MembroEquipe
    extra = 0


class SubmissaoInline(admin.TabularInline):
    """Inline para submissões do projeto."""

    model = Submissao
    extra = 0
    readonly_fields = ['submetido_em']
    raw_id_fields = ['edital']


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    """Admin para Projeto."""

    list_display = [
        'id',
        'titulo',
        'area',
        'status',
        'responsavel',
        'created_at',
    ]
    list_filter = ['status', 'area', 'created_at']
    search_fields = ['titulo', 'resumo', 'responsavel__name']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    raw_id_fields = ['responsavel']
    inlines = [MembroEquipeInline, SubmissaoInline]

    fieldsets = (
        (None, {'fields': ('titulo', 'resumo', 'area')}),
        ('Status', {'fields': ('status', 'responsavel')}),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """Inclui projetos soft-deleted no admin."""
        return Projeto.all_objects.all()


@admin.register(MembroEquipe)
class MembroEquipeAdmin(admin.ModelAdmin):
    """Admin para MembroEquipe."""

    list_display = ['id', 'nome', 'email', 'funcao', 'projeto', 'created_at']
    list_filter = ['created_at']
    search_fields = ['nome', 'email', 'projeto__titulo']
    raw_id_fields = ['projeto']


@admin.register(Submissao)
class SubmissaoAdmin(admin.ModelAdmin):
    """Admin para Submissao."""

    list_display = [
        'id',
        'projeto',
        'edital',
        'status',
        'submetido_em',
    ]
    list_filter = ['status', 'submetido_em', 'edital']
    search_fields = ['projeto__titulo', 'edital__titulo']
    readonly_fields = ['submetido_em']
    date_hierarchy = 'submetido_em'
    raw_id_fields = ['projeto', 'edital']


@admin.register(RelatorioProgresso)
class RelatorioProgressoAdmin(admin.ModelAdmin):
    """Admin para RelatorioProgresso."""

    list_display = ['id', 'projeto', 'periodo', 'autor', 'created_at']
    list_filter = ['periodo', 'created_at']
    search_fields = ['projeto__titulo', 'conteudo']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['projeto', 'autor']
