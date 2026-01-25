"""
Modelos de publicações do sistema YpeTec.

Este módulo contém:
- Publicacao: vitrine pública de projetos aprovados
"""
from django.conf import settings
from django.db import models


class Publicacao(models.Model):
    """
    Publicação de um projeto na vitrine pública.

    Representa um projeto aprovado que foi publicado
    para exibição pública no site.
    """

    projeto = models.OneToOneField(
        'projetos.Projeto',
        on_delete=models.CASCADE,
        related_name='publicacao',
        verbose_name='projeto',
    )
    logo = models.ImageField(
        'logo',
        upload_to='publicacoes/',
    )
    descricao = models.TextField(
        'descrição pública',
    )
    publicado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='publicacoes_realizadas',
        verbose_name='publicado por',
    )
    publicado_em = models.DateTimeField(
        'publicado em',
        auto_now_add=True,
    )
    destaque = models.BooleanField(
        'destaque',
        default=False,
        help_text='Exibir em destaque na página inicial.',
    )
    ativo = models.BooleanField(
        'ativo',
        default=True,
        help_text='Se desmarcado, não aparece na vitrine.',
    )

    class Meta:
        verbose_name = 'publicação'
        verbose_name_plural = 'publicações'
        ordering = ['-publicado_em']
        indexes = [
            models.Index(fields=['ativo', 'destaque']),
            models.Index(fields=['publicado_em']),
        ]

    def __str__(self):
        return f'{self.projeto.titulo}'

    @property
    def logo_url(self):
        """Retorna a URL completa do logo."""
        if self.logo:
            return self.logo.url
        return None

    @classmethod
    def vitrine(cls):
        """Retorna publicações ativas para a vitrine."""
        return cls.objects.filter(ativo=True).select_related('projeto')

    @classmethod
    def destaques(cls):
        """Retorna publicações em destaque."""
        return cls.objects.filter(ativo=True, destaque=True).select_related('projeto')
