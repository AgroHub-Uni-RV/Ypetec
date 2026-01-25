"""
Views para editais.
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.contas.permissions import IsAdmin

from .models import Edital
from .serializers import EditalCreateSerializer, EditalListSerializer, EditalSerializer


class EditalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para editais.

    GET    /api/calls/          - Lista editais (público)
    GET    /api/calls/:id/      - Detalhe do edital (público)
    POST   /api/calls/          - Cria edital (admin)
    PUT    /api/calls/:id/      - Atualiza edital (admin)
    DELETE /api/calls/:id/      - Remove edital (admin)

    Query params:
        status: open | upcoming | closed | all (default: open)
    """

    def get_queryset(self):
        """Filtra editais por status."""
        status_filter = self.request.query_params.get('status', 'open')

        if status_filter == 'open':
            return Edital.abertos()
        elif status_filter == 'upcoming':
            return Edital.futuros()
        elif status_filter == 'closed':
            return Edital.encerrados()
        else:  # all
            return Edital.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return EditalCreateSerializer
        if self.action == 'list':
            return EditalListSerializer
        return EditalSerializer

    def get_permissions(self):
        """
        Leitura é pública, escrita requer admin.
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]
