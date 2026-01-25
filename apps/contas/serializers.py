"""
Serializers para autenticação e usuários.

Este módulo contém:
- UsuarioSerializer: serialização de usuários
- UsuarioCreateSerializer: criação de usuários (registro)
- TokenObtainSerializer: login com JWT customizado
- PasswordResetRequestSerializer: solicitação de reset de senha
- PasswordResetConfirmSerializer: confirmação de reset de senha
"""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario, validar_cpf


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para leitura de usuários."""

    class Meta:
        model = Usuario
        fields = [
            'id',
            'cpf',
            'email',
            'name',
            'role',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de usuários (registro público).

    Cria usuários com role ALUNO por padrão.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
    )

    class Meta:
        model = Usuario
        fields = ['cpf', 'email', 'name', 'password']

    def validate_cpf(self, value):
        """Valida e limpa o CPF."""
        return validar_cpf(value)

    def validate_email(self, value):
        """Valida unicidade do email (case-insensitive)."""
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Este email já está em uso.')
        return value.lower()

    def create(self, validated_data):
        """Cria usuário com senha hasheada."""
        return Usuario.objects.create_user(
            cpf=validated_data['cpf'],
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
        )


class UsuarioAdminCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de usuários pelo admin.

    Permite definir role e status.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
    )

    class Meta:
        model = Usuario
        fields = ['id', 'cpf', 'email', 'name', 'password', 'role']
        read_only_fields = ['id']

    def validate_cpf(self, value):
        """Valida e limpa o CPF."""
        return validar_cpf(value)

    def validate_email(self, value):
        """Valida unicidade do email (case-insensitive)."""
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Este email já está em uso.')
        return value.lower()

    def create(self, validated_data):
        """Cria usuário com senha hasheada."""
        return Usuario.objects.create_user(
            cpf=validated_data['cpf'],
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data.get('role', Usuario.Role.ALUNO),
        )


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de usuários."""

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        required=False,
        style={'input_type': 'password'},
    )

    class Meta:
        model = Usuario
        fields = ['name', 'cpf', 'email', 'role', 'password']
        extra_kwargs = {
            'name': {'required': False},
            'cpf': {'required': False},
            'email': {'required': False},
            'role': {'required': False},
        }

    def validate_cpf(self, value):
        """Valida e limpa o CPF."""
        cpf_limpo = validar_cpf(value)
        # Verifica unicidade excluindo o usuário atual
        if Usuario.objects.filter(cpf=cpf_limpo).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError('Este CPF já está em uso.')
        return cpf_limpo

    def validate_email(self, value):
        """Valida unicidade do email excluindo o usuário atual."""
        if Usuario.objects.filter(email__iexact=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError('Este email já está em uso.')
        return value.lower()

    def update(self, instance, validated_data):
        """Atualiza usuário, tratando senha separadamente."""
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class TokenObtainSerializer(serializers.Serializer):
    """
    Serializer customizado para login.

    Retorna token JWT com payload compatível com sistema Node.js:
    { id, role, name, iat, exp }
    """

    cpf = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_cpf(self, value):
        """Limpa o CPF (remove pontuação)."""
        import re
        return re.sub(r'\D', '', value)

    def validate(self, attrs):
        """Autentica o usuário e gera tokens."""
        cpf = attrs.get('cpf')
        password = attrs.get('password')

        # Busca usuário pelo CPF
        try:
            user = Usuario.objects.get(cpf=cpf)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({
                'detail': 'CPF ou senha inválidos.'
            })

        # Verifica se está ativo
        if user.status != Usuario.Status.ATIVO:
            raise serializers.ValidationError({
                'detail': 'Conta inativa. Entre em contato com o administrador.'
            })

        # Verifica senha
        if not user.check_password(password):
            raise serializers.ValidationError({
                'detail': 'CPF ou senha inválidos.'
            })

        # Gera tokens
        refresh = RefreshToken.for_user(user)

        # Adiciona claims customizados ao access token
        refresh['id'] = user.id
        refresh['role'] = user.role
        refresh['name'] = user.name

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'cpf': user.cpf,
                'email': user.email,
                'name': user.name,
                'role': user.role,
            }
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer para solicitação de reset de senha."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Normaliza email para lowercase."""
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer para confirmação de reset de senha."""

    token = serializers.CharField()
    password = serializers.CharField(
        min_length=6,
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate_password(self, value):
        """Valida força da senha."""
        # Pode adicionar validações customizadas aqui
        return value
