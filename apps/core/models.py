"""
Modelos base e utilitários do sistema YpeTec.

Este módulo contém:
- BaseModel: modelo abstrato com soft delete e timestamps
- SoftDeleteManager: manager para filtrar registros deletados
- LogAuditoria: modelo para auditoria de ações
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet customizado para soft delete."""

    def delete(self):
        """Soft delete em batch."""
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        """Delete real em batch."""
        return super().delete()

    def alive(self):
        """Retorna apenas registros não deletados."""
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        """Retorna apenas registros deletados."""
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    """Manager que filtra registros soft-deleted por padrão."""

    def get_queryset(self):
        """Retorna apenas registros não deletados."""
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def with_deleted(self):
        """Retorna todos os registros, incluindo deletados."""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def only_deleted(self):
        """Retorna apenas registros deletados."""
        return SoftDeleteQuerySet(self.model, using=self._db).dead()


class AllObjectsManager(models.Manager):
    """Manager que retorna todos os registros, incluindo deletados."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class BaseModel(models.Model):
    """
    Modelo base abstrato com soft delete e timestamps.

    Todos os modelos principais do sistema devem herdar desta classe.

    Atributos:
        created_at: Data/hora de criação (auto)
        updated_at: Data/hora da última atualização (auto)
        deleted_at: Data/hora do soft delete (null = não deletado)

    Managers:
        objects: Retorna apenas registros não deletados (padrão)
        all_objects: Retorna todos os registros, incluindo deletados
    """

    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        'atualizado em',
        auto_now=True,
    )
    deleted_at = models.DateTimeField(
        'deletado em',
        null=True,
        blank=True,
        db_index=True,
    )

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def delete(self, using=None, keep_parents=False):
        """Soft delete: marca deleted_at em vez de remover."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])

    def hard_delete(self, using=None, keep_parents=False):
        """Delete real do banco de dados."""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restaura um registro soft-deleted."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at', 'updated_at'])

    @property
    def is_deleted(self):
        """Retorna True se o registro foi soft-deleted."""
        return self.deleted_at is not None


class LogAuditoria(models.Model):
    """
    Log de auditoria para rastrear ações no sistema.

    Registra quem fez o quê, quando e em qual entidade.
    """

    class Acao(models.TextChoices):
        """Tipos de ação para auditoria."""
        CRIAR = 'CRIAR', 'Criar'
        ATUALIZAR = 'ATUALIZAR', 'Atualizar'
        DELETAR = 'DELETAR', 'Deletar'
        RESTAURAR = 'RESTAURAR', 'Restaurar'
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
        AVALIAR = 'AVALIAR', 'Avaliar'
        SUBMETER = 'SUBMETER', 'Submeter'
        PUBLICAR = 'PUBLICAR', 'Publicar'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_auditoria',
        verbose_name='usuário',
    )
    acao = models.CharField(
        'ação',
        max_length=80,
        db_index=True,
    )
    entidade = models.CharField(
        'entidade',
        max_length=80,
        db_index=True,
    )
    entidade_id = models.BigIntegerField(
        'ID da entidade',
    )
    dados_anteriores = models.JSONField(
        'dados anteriores',
        null=True,
        blank=True,
    )
    dados_novos = models.JSONField(
        'dados novos',
        null=True,
        blank=True,
    )
    ip_address = models.GenericIPAddressField(
        'endereço IP',
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        'user agent',
        blank=True,
        default='',
    )
    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'log de auditoria'
        verbose_name_plural = 'logs de auditoria'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entidade', 'entidade_id']),
            models.Index(fields=['usuario', 'created_at']),
        ]

    def __str__(self):
        usuario_str = self.usuario.name if self.usuario else 'Sistema'
        return f'{usuario_str} - {self.acao} {self.entidade}#{self.entidade_id}'

    @classmethod
    def registrar(cls, usuario, acao, entidade, entidade_id, **kwargs):
        """
        Método de conveniência para registrar um log.

        Args:
            usuario: Usuário que realizou a ação (pode ser None)
            acao: Tipo de ação (usar LogAuditoria.Acao)
            entidade: Nome da entidade (ex: 'Projeto', 'Usuario')
            entidade_id: ID da entidade afetada
            **kwargs: Campos opcionais (dados_anteriores, dados_novos, ip_address, user_agent)

        Returns:
            LogAuditoria: Instância criada
        """
        return cls.objects.create(
            usuario=usuario,
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            **kwargs
        )
