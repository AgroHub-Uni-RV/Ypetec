"""
Modelos de mentorias do sistema YpeTec.

Este módulo contém:
- SolicitacaoMentoria: solicitações de mentoria para projetos incubados
"""
from django.conf import settings
from django.db import models


class SolicitacaoMentoria(models.Model):
    """
    Solicitação de mentoria para um projeto.

    Permite que alunos solicitem acompanhamento especializado
    para seus projetos incubados.
    """

    class Status(models.TextChoices):
        """Status da solicitação."""
        SOLICITADA = 'SOLICITADA', 'Solicitada'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em andamento'
        CONCLUIDA = 'CONCLUIDA', 'Concluída'
        NEGADA = 'NEGADA', 'Negada'

    projeto = models.ForeignKey(
        'projetos.Projeto',
        on_delete=models.CASCADE,
        related_name='solicitacoes_mentoria',
        verbose_name='projeto',
    )
    area = models.CharField(
        'área de mentoria',
        max_length=80,
    )
    justificativa = models.TextField(
        'justificativa',
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.SOLICITADA,
        db_index=True,
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='solicitacoes_mentoria',
        verbose_name='solicitante',
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentorias',
        verbose_name='mentor',
    )
    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        'atualizado em',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'solicitação de mentoria'
        verbose_name_plural = 'solicitações de mentoria'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['projeto']),
            models.Index(fields=['solicitante']),
            models.Index(fields=['status']),
            models.Index(fields=['mentor']),
        ]

    def __str__(self):
        return f'{self.projeto.titulo} - {self.area}'

    @property
    def esta_em_andamento(self):
        """Retorna True se a mentoria está em andamento."""
        return self.status == self.Status.EM_ANDAMENTO

    @property
    def esta_concluida(self):
        """Retorna True se a mentoria foi concluída."""
        return self.status == self.Status.CONCLUIDA

    @property
    def foi_negada(self):
        """Retorna True se a solicitação foi negada."""
        return self.status == self.Status.NEGADA
