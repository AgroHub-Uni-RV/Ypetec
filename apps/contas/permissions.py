"""
Permissões customizadas para o sistema YpeTec.

Este módulo contém:
- IsAdmin: permite apenas administradores
- IsAluno: permite apenas alunos
- IsAdminOrReadOnly: admin pode tudo, outros apenas leitura
- IsOwner: permite apenas o dono do recurso
"""
from rest_framework import permissions

from .models import Usuario


class IsAdmin(permissions.BasePermission):
    """
    Permite acesso apenas para usuários com role ADMIN.
    """

    message = 'Acesso restrito a administradores.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Usuario.Role.ADMIN
        )


class IsAluno(permissions.BasePermission):
    """
    Permite acesso apenas para usuários com role ALUNO.
    """

    message = 'Acesso restrito a alunos.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Usuario.Role.ALUNO
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin pode fazer qualquer coisa.
    Outros usuários autenticados podem apenas ler.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Usuario.Role.ADMIN
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite acesso ao dono do recurso ou a administradores.

    Requer que o objeto tenha um campo que referencia o usuário.
    O campo padrão é 'responsavel', mas pode ser customizado na view
    definindo owner_field.
    """

    message = 'Você não tem permissão para acessar este recurso.'

    def has_object_permission(self, request, view, obj):
        # Admin pode tudo
        if request.user.role == Usuario.Role.ADMIN:
            return True

        # Busca o campo que indica o dono
        owner_field = getattr(view, 'owner_field', 'responsavel')

        # Verifica se o usuário é o dono
        owner = getattr(obj, owner_field, None)
        if owner is None:
            return False

        # Se owner é um objeto Usuario, compara com request.user
        if hasattr(owner, 'pk'):
            return owner.pk == request.user.pk

        # Se owner é um ID, compara diretamente
        return owner == request.user.pk


class IsProjectOwner(permissions.BasePermission):
    """
    Permite acesso apenas ao responsável pelo projeto.

    Usado para ações que apenas o dono do projeto pode fazer,
    como submeter a editais ou solicitar mentoria.
    """

    message = 'Você não é responsável por este projeto.'

    def has_object_permission(self, request, view, obj):
        # Para projetos diretamente
        if hasattr(obj, 'responsavel'):
            return obj.responsavel == request.user

        # Para submissões, mentorias, etc (que têm projeto como FK)
        if hasattr(obj, 'projeto'):
            return obj.projeto.responsavel == request.user

        return False
