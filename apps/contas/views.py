"""
Views de autenticação e gerenciamento de usuários.

Este módulo contém:
- AuthViewSet: login, register, me, forgot, reset
- UsuarioViewSet: CRUD de usuários (admin)
"""
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario
from .permissions import IsAdmin
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    TokenObtainSerializer,
    UsuarioAdminCreateSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,
    UsuarioUpdateSerializer,
)


class LoginView(APIView):
    """
    POST /api/auth/login

    Autentica usuário com CPF e senha.
    Retorna tokens JWT compatíveis com sistema Node.js.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    POST /api/auth/register

    Registro público de novos usuários (sempre como ALUNO).
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UsuarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Gera tokens para login automático
        refresh = RefreshToken.for_user(user)
        refresh['id'] = user.id
        refresh['role'] = user.role
        refresh['name'] = user.name

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UsuarioSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class MeView(APIView):
    """
    GET /api/auth/me

    Retorna dados do usuário autenticado.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot

    Solicita reset de senha. Envia email com token.
    Retorna sempre sucesso para não revelar se email existe.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = Usuario.objects.get(email__iexact=email)

            # Gera token único
            token = secrets.token_hex(32)

            # Armazena token no cache (30 minutos)
            cache_key = f'password_reset_{token}'
            cache.set(cache_key, user.id, timeout=30 * 60)

            # TODO: Enviar email com link de reset
            # O link deve ser: {APP_URL}/reset-password?token={token}
            # Por enquanto, apenas log para debug
            reset_url = f"{settings.APP_URL if hasattr(settings, 'APP_URL') else 'http://localhost:3000'}/reset-password?token={token}"
            print(f"[DEBUG] Password reset URL for {email}: {reset_url}")

            # Em produção, usar Resend ou outro serviço de email
            # from apps.core.email import send_password_reset_email
            # send_password_reset_email(user.email, user.name, reset_url)

        except Usuario.DoesNotExist:
            # Não revela se o email existe
            pass

        # Sempre retorna sucesso
        return Response({
            'message': 'Se o email estiver cadastrado, você receberá instruções para redefinir sua senha.'
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    POST /api/auth/reset

    Reseta senha usando token recebido por email.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        password = serializer.validated_data['password']

        # Busca user_id no cache
        cache_key = f'password_reset_{token}'
        user_id = cache.get(cache_key)

        if not user_id:
            return Response({
                'detail': 'Token inválido ou expirado.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Usuario.objects.get(id=user_id)
            user.set_password(password)
            user.save()

            # Invalida o token
            cache.delete(cache_key)

            return Response({
                'message': 'Senha alterada com sucesso.'
            }, status=status.HTTP_200_OK)

        except Usuario.DoesNotExist:
            return Response({
                'detail': 'Usuário não encontrado.'
            }, status=status.HTTP_400_BAD_REQUEST)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de usuários (admin).

    GET    /api/users/          - Lista usuários
    GET    /api/users/:id/      - Detalhe do usuário
    POST   /api/users/          - Cria usuário
    PUT    /api/users/:id/      - Atualiza usuário
    DELETE /api/users/:id/      - Remove usuário (soft delete)
    GET    /api/users/report.csv - Exporta relatório CSV
    """

    queryset = Usuario.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioAdminCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        return UsuarioSerializer

    def get_queryset(self):
        """Filtra por role se especificado."""
        queryset = Usuario.objects.all()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role.upper())
        return queryset.order_by('-id')

    def destroy(self, request, *args, **kwargs):
        """Soft delete do usuário."""
        instance = self.get_object()
        instance.delete()  # Usa soft delete do modelo
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='report.csv')
    def report_csv(self, request):
        """
        GET /api/users/report.csv

        Exporta lista de usuários em CSV.
        """
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Nome', 'CPF', 'Email', 'Role', 'Criado em'])

        role = request.query_params.get('role')
        queryset = Usuario.objects.all()
        if role:
            queryset = queryset.filter(role=role.upper())

        for user in queryset.order_by('role', 'name'):
            writer.writerow([
                user.id,
                user.name,
                user.cpf,
                user.email,
                user.role,
                user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return response
