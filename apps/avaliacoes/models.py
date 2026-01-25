"""
Modelos de avaliações do sistema YpeTec.

Este módulo contém:
- Avaliacao: avaliações de submissões por administradores
"""
from django.conf import settings
from django.db import models


class Avaliacao(models.Model):
    """
    Avaliação de uma submissão.

    Registra o parecer de um avaliador sobre uma submissão
    de projeto a um edital.
    """

    class Resultado(models.TextChoices):
        """Resultado da avaliação."""
        APROVADO = 'APROVADO', 'Aprovado'
        REPROVADO = 'REPROVADO', 'Reprovado'
        NECESSITA_AJUSTES = 'NECESSITA_AJUSTES', 'Necessita ajustes'

    submissao = models.ForeignKey(
        'projetos.Submissao',
        on_delete=models.CASCADE,
        related_name='avaliacoes',
        verbose_name='submissão',
    )
    avaliador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='avaliacoes_realizadas',
        verbose_name='avaliador',
    )
    resultado = models.CharField(
        'resultado',
        max_length=20,
        choices=Resultado.choices,
        db_index=True,
    )
    comentarios = models.TextField(
        'comentários',
    )
    avaliado_em = models.DateTimeField(
        'avaliado em',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'avaliação'
        verbose_name_plural = 'avaliações'
        ordering = ['-avaliado_em']
        indexes = [
            models.Index(fields=['submissao', 'avaliado_em']),
            models.Index(fields=['avaliador']),
            models.Index(fields=['resultado']),
        ]

    def __str__(self):
        return f'{self.submissao} - {self.get_resultado_display()}'

    @property
    def foi_aprovado(self):
        """Retorna True se a avaliação aprovou a submissão."""
        return self.resultado == self.Resultado.APROVADO

    @property
    def foi_reprovado(self):
        """Retorna True se a avaliação reprovou a submissão."""
        return self.resultado == self.Resultado.REPROVADO

    @property
    def precisa_ajustes(self):
        """Retorna True se a avaliação solicitou ajustes."""
        return self.resultado == self.Resultado.NECESSITA_AJUSTES
