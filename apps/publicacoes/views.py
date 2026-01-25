"""
Views para publicações.
"""
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.contas.permissions import IsAdmin

from .models import Publicacao
from .serializers import (
    PublicacaoCreateSerializer,
    PublicacaoListSerializer,
    PublicacaoSerializer,
)


class PublicacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para publicações.

    GET  /api/publications/     - Lista publicações (público)
    POST /api/publications/     - Cria publicação (admin)
    """

    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Retorna publicações ativas por padrão."""
        queryset = Publicacao.objects.select_related('projeto').order_by('-publicado_em')

        # Para listagem pública, apenas ativas
        if self.action == 'list' and not self.request.user.is_authenticated:
            return queryset.filter(ativo=True)

        # Admin pode ver todas
        if self.request.user.is_authenticated and self.request.user.role == 'ADMIN':
            return queryset

        # Usuário comum vê apenas ativas
        return queryset.filter(ativo=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return PublicacaoCreateSerializer
        if self.action == 'list':
            return PublicacaoListSerializer
        return PublicacaoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        publicacao = serializer.save()

        output_serializer = PublicacaoSerializer(publicacao, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
