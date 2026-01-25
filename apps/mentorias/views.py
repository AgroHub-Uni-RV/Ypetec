"""
Views para mentorias.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.contas.permissions import IsAdmin, IsAluno

from .models import SolicitacaoMentoria
from .serializers import (
    SolicitacaoMentoriaCreateSerializer,
    SolicitacaoMentoriaSerializer,
    SolicitacaoMentoriaUpdateSerializer,
)


class SolicitacaoMentoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para solicitações de mentoria.

    POST  /api/mentorship-requests/           - Cria solicitação (aluno)
    GET   /api/mentorship-requests/mine       - Minhas solicitações (aluno)
    GET   /api/mentorship-requests/           - Lista todas (admin)
    PATCH /api/mentorship-requests/:id/status - Atualiza status (admin)
    """

    serializer_class = SolicitacaoMentoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = SolicitacaoMentoria.objects.select_related(
            'projeto', 'solicitante', 'mentor'
        ).order_by('-created_at')

        # Aluno vê apenas suas solicitações
        if user.role == 'ALUNO':
            return queryset.filter(solicitante=user)

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return SolicitacaoMentoriaCreateSerializer
        if self.action in ['update', 'partial_update', 'update_status']:
            return SolicitacaoMentoriaUpdateSerializer
        return SolicitacaoMentoriaSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsAluno()]
        if self.action in ['mine']:
            return [IsAuthenticated()]
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'update_status']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def mine(self, request):
        """
        GET /api/mentorship-requests/mine

        Lista solicitações de mentoria do aluno logado.
        """
        queryset = SolicitacaoMentoria.objects.filter(
            solicitante=request.user
        ).select_related('projeto').order_by('-created_at')

        serializer = SolicitacaoMentoriaSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """
        PATCH /api/mentorship-requests/:id/status

        Atualiza status da solicitação de mentoria (admin).
        """
        instance = self.get_object()
        serializer = SolicitacaoMentoriaUpdateSerializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(SolicitacaoMentoriaSerializer(instance).data)
