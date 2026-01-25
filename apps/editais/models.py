"""
Modelos de editais do sistema YpeTec.

Este módulo contém:
- Edital: períodos de submissão de projetos
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel


class Edital(BaseModel):
    """
    Edital (call) para submissão de projetos.

    Representa um período durante o qual alunos podem submeter
    projetos para avaliação e possível incubação.
    """

    class Status(models.TextChoices):
        """Status do edital."""
        RASCUNHO = 'RASCUNHO', 'Rascunho'
        PUBLICADO = 'PUBLICADO', 'Publicado'
        ENCERRADO = 'ENCERRADO', 'Encerrado'

    titulo = models.CharField(
        'título',
        max_length=160,
    )
    descricao = models.TextField(
        'descrição',
    )
    inicio = models.DateTimeField(
        'data de início',
        db_index=True,
    )
    fim = models.DateTimeField(
        'data de encerramento',
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.RASCUNHO,
        db_index=True,
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='editais_criados',
        verbose_name='criado por',
    )

    class Meta:
        verbose_name = 'edital'
        verbose_name_plural = 'editais'
        ordering = ['-inicio']
        indexes = [
            models.Index(fields=['status', 'inicio']),
            models.Index(fields=['criado_por']),
        ]

    def __str__(self):
        return self.titulo

    @property
    def esta_aberto(self):
        """Retorna True se o edital está aberto para submissões."""
        agora = timezone.now()
        return (
            self.status == self.Status.PUBLICADO
            and self.inicio <= agora <= self.fim
        )

    @property
    def esta_encerrado(self):
        """Retorna True se o edital já encerrou."""
        return self.fim < timezone.now() or self.status == self.Status.ENCERRADO

    @property
    def esta_futuro(self):
        """Retorna True se o edital ainda não começou."""
        return self.inicio > timezone.now()

    @classmethod
    def abertos(cls):
        """Retorna editais atualmente abertos."""
        agora = timezone.now()
        return cls.objects.filter(
            status=cls.Status.PUBLICADO,
            inicio__lte=agora,
            fim__gte=agora,
        )

    @classmethod
    def futuros(cls):
        """Retorna editais que ainda não começaram."""
        agora = timezone.now()
        return cls.objects.filter(inicio__gt=agora)

    @classmethod
    def encerrados(cls):
        """Retorna editais já encerrados."""
        agora = timezone.now()
        return cls.objects.filter(fim__lt=agora)
