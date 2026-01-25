"""
Modelos de usuários e autenticação do sistema YpeTec.

Este módulo contém:
- Usuario: modelo customizado de usuário (extends AbstractUser)
- Managers customizados para soft delete
"""
import re

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def validar_cpf(value):
    """
    Valida um CPF (apenas dígitos, 11 caracteres).

    Não valida o dígito verificador, apenas formato.
    A validação completa deve ser feita no frontend.
    """
    cpf_limpo = re.sub(r'\D', '', value)
    if len(cpf_limpo) != 11:
        raise ValidationError('CPF deve conter exatamente 11 dígitos.')
    if not cpf_limpo.isdigit():
        raise ValidationError('CPF deve conter apenas números.')
    return cpf_limpo


class UsuarioManager(UserManager):
    """Manager customizado para Usuario com suporte a soft delete."""

    def get_queryset(self):
        """Retorna apenas usuários não deletados."""
        return super().get_queryset().filter(deleted_at__isnull=True)

    def with_deleted(self):
        """Retorna todos os usuários, incluindo deletados."""
        return super().get_queryset()

    def only_deleted(self):
        """Retorna apenas usuários deletados."""
        return super().get_queryset().filter(deleted_at__isnull=False)

    def _create_user(self, cpf, email, password, **extra_fields):
        """Cria e salva um usuário com CPF, email e senha."""
        if not cpf:
            raise ValueError('O CPF é obrigatório.')
        if not email:
            raise ValueError('O email é obrigatório.')

        email = self.normalize_email(email)
        cpf = validar_cpf(cpf)

        user = self.model(cpf=cpf, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, cpf, email, password=None, **extra_fields):
        """Cria um usuário comum (ALUNO)."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', Usuario.Role.ALUNO)
        return self._create_user(cpf, email, password, **extra_fields)

    def create_superuser(self, cpf, email, password=None, **extra_fields):
        """Cria um superusuário (ADMIN)."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Usuario.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self._create_user(cpf, email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Modelo customizado de usuário para o sistema YpeTec.

    Usa CPF como identificador único para login (em vez de username).
    Mantém compatibilidade com o sistema Node.js existente.

    Atributos:
        cpf: CPF do usuário (11 dígitos, único)
        email: Email do usuário (único)
        name: Nome completo do usuário
        role: Papel no sistema (ADMIN, ALUNO, MENTOR, INVESTIDOR)
        status: Status da conta (ATIVO, INATIVO)
        deleted_at: Soft delete timestamp
    """

    class Role(models.TextChoices):
        """Papéis disponíveis no sistema."""
        ADMIN = 'ADMIN', 'Administrador'
        ALUNO = 'ALUNO', 'Aluno'
        MENTOR = 'MENTOR', 'Mentor'
        INVESTIDOR = 'INVESTIDOR', 'Investidor'

    class Status(models.TextChoices):
        """Status da conta do usuário."""
        ATIVO = 'ATIVO', 'Ativo'
        INATIVO = 'INATIVO', 'Inativo'

    # Remover username, usar CPF como identificador
    username = None

    cpf = models.CharField(
        'CPF',
        max_length=11,
        unique=True,
        validators=[validar_cpf],
        help_text='CPF do usuário (apenas números).',
    )
    email = models.EmailField(
        'email',
        unique=True,
    )
    name = models.CharField(
        'nome completo',
        max_length=120,
    )
    role = models.CharField(
        'papel',
        max_length=20,
        choices=Role.choices,
        default=Role.ALUNO,
        db_index=True,
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.ATIVO,
    )

    # Soft delete
    deleted_at = models.DateTimeField(
        'deletado em',
        null=True,
        blank=True,
        db_index=True,
    )

    # Timestamps (sobrescreve AbstractUser para consistência)
    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        'atualizado em',
        auto_now=True,
    )

    # Configuração de autenticação
    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['email', 'name']

    objects = UsuarioManager()

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'status']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f'{self.name} ({self.cpf})'

    def delete(self, using=None, keep_parents=False):
        """Soft delete: marca deleted_at em vez de remover."""
        self.deleted_at = timezone.now()
        self.status = self.Status.INATIVO
        self.save(update_fields=['deleted_at', 'status', 'updated_at'])

    def hard_delete(self, using=None, keep_parents=False):
        """Delete real do banco de dados."""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restaura um usuário soft-deleted."""
        self.deleted_at = None
        self.status = self.Status.ATIVO
        self.save(update_fields=['deleted_at', 'status', 'updated_at'])

    @property
    def is_deleted(self):
        """Retorna True se o usuário foi soft-deleted."""
        return self.deleted_at is not None

    @property
    def is_admin(self):
        """Retorna True se o usuário é administrador."""
        return self.role == self.Role.ADMIN

    @property
    def is_aluno(self):
        """Retorna True se o usuário é aluno."""
        return self.role == self.Role.ALUNO

    @property
    def is_mentor(self):
        """Retorna True se o usuário é mentor."""
        return self.role == self.Role.MENTOR

    def get_full_name(self):
        """Retorna o nome completo do usuário."""
        return self.name

    def get_short_name(self):
        """Retorna o primeiro nome do usuário."""
        return self.name.split()[0] if self.name else ''

    def save(self, *args, **kwargs):
        """Limpa o CPF antes de salvar."""
        if self.cpf:
            self.cpf = re.sub(r'\D', '', self.cpf)
        super().save(*args, **kwargs)
