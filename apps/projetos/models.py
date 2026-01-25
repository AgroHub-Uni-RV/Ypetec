"""
Modelos de projetos do sistema YpeTec.

Este módulo contém:
- Projeto: projetos criados por alunos
- MembroEquipe: membros da equipe do projeto
- Submissao: submissões de projetos a editais
- RelatorioProgresso: relatórios de acompanhamento
"""
from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Projeto(BaseModel):
    """
    Projeto criado por um aluno.

    Representa uma ideia/startup que pode ser submetida
    a editais para avaliação e incubação.
    """

    class Status(models.TextChoices):
        """Status do projeto no ciclo de vida."""
        PRE_SUBMISSAO = 'PRE_SUBMISSAO', 'Pré-submissão'
        SUBMETIDO = 'SUBMETIDO', 'Submetido'
        APROVADO = 'APROVADO', 'Aprovado'
        REPROVADO = 'REPROVADO', 'Reprovado'
        AJUSTES = 'AJUSTES', 'Ajustes'
        INCUBADO = 'INCUBADO', 'Incubado'
        INATIVO = 'INATIVO', 'Inativo'
        DESLIGADO = 'DESLIGADO', 'Desligado'

    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='projetos',
        verbose_name='responsável',
    )
    titulo = models.CharField(
        'título',
        max_length=160,
    )
    resumo = models.TextField(
        'resumo',
    )
    area = models.CharField(
        'área',
        max_length=80,
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.PRE_SUBMISSAO,
        db_index=True,
    )

    class Meta:
        verbose_name = 'projeto'
        verbose_name_plural = 'projetos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['responsavel', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.titulo

    @property
    def esta_incubado(self):
        """Retorna True se o projeto está incubado."""
        return self.status == self.Status.INCUBADO

    @property
    def pode_submeter(self):
        """Retorna True se o projeto pode ser submetido a um edital."""
        return self.status in [
            self.Status.PRE_SUBMISSAO,
            self.Status.AJUSTES,
        ]


class MembroEquipe(models.Model):
    """
    Membro da equipe de um projeto.

    Nota: O schema MySQL tem user_id FK, mas o código Node.js
    usa nome e email diretamente. Seguindo o código.
    """

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='membros',
        verbose_name='projeto',
    )
    nome = models.CharField(
        'nome',
        max_length=120,
    )
    email = models.EmailField(
        'email',
        blank=True,
        default='',
    )
    funcao = models.CharField(
        'função na equipe',
        max_length=80,
    )
    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'membro da equipe'
        verbose_name_plural = 'membros da equipe'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['projeto']),
        ]

    def __str__(self):
        return f'{self.nome} - {self.funcao}'


class Submissao(models.Model):
    """
    Submissão de um projeto a um edital.

    Representa a participação de um projeto em um processo
    seletivo específico.
    """

    class Status(models.TextChoices):
        """Status da submissão."""
        ENVIADA = 'ENVIADA', 'Enviada'
        EM_AVALIACAO = 'EM_AVALIACAO', 'Em avaliação'
        APROVADA = 'APROVADA', 'Aprovada'
        REPROVADA = 'REPROVADA', 'Reprovada'
        AJUSTES_SOLICITADOS = 'AJUSTES_SOLICITADOS', 'Ajustes solicitados'

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.PROTECT,
        related_name='submissoes',
        verbose_name='projeto',
    )
    edital = models.ForeignKey(
        'editais.Edital',
        on_delete=models.PROTECT,
        related_name='submissoes',
        verbose_name='edital',
    )
    status = models.CharField(
        'status',
        max_length=25,
        choices=Status.choices,
        default=Status.ENVIADA,
        db_index=True,
    )
    submetido_em = models.DateTimeField(
        'submetido em',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'submissão'
        verbose_name_plural = 'submissões'
        ordering = ['-submetido_em']
        # Evitar submissão duplicada do mesmo projeto ao mesmo edital
        constraints = [
            models.UniqueConstraint(
                fields=['projeto', 'edital'],
                name='unique_projeto_edital',
            )
        ]
        indexes = [
            models.Index(fields=['projeto', 'edital']),
            models.Index(fields=['status']),
            models.Index(fields=['edital', 'status']),
        ]

    def __str__(self):
        return f'{self.projeto.titulo} → {self.edital.titulo}'


class RelatorioProgresso(models.Model):
    """
    Relatório de progresso de um projeto incubado.

    Permite acompanhar a evolução dos projetos durante
    o período de incubação.
    """

    class Periodo(models.TextChoices):
        """Periodicidade do relatório."""
        MENSAL = 'MENSAL', 'Mensal'
        TRIMESTRAL = 'TRIMESTRAL', 'Trimestral'

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='relatorios',
        verbose_name='projeto',
    )
    periodo = models.CharField(
        'período',
        max_length=20,
        choices=Periodo.choices,
    )
    conteudo = models.TextField(
        'conteúdo',
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='relatorios_criados',
        verbose_name='autor',
    )
    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'relatório de progresso'
        verbose_name_plural = 'relatórios de progresso'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['projeto', 'created_at']),
        ]

    def __str__(self):
        return f'{self.projeto.titulo} - {self.get_periodo_display()} ({self.created_at.strftime("%m/%Y")})'
