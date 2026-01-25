"""
Views para avaliações.
"""
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.contas.permissions import IsAdmin

from .models import Avaliacao
from .serializers import AvaliacaoCreateSerializer, AvaliacaoSerializer


class AvaliacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para avaliações.

    POST /api/evaluations/              - Cria avaliação (admin)
    GET  /api/evaluations/              - Lista avaliações (admin)
    GET  /api/evaluations/?submission=X - Avaliações de uma submissão
    """

    serializer_class = AvaliacaoSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = Avaliacao.objects.select_related(
            'submissao__projeto',
            'avaliador'
        ).order_by('-avaliado_em')

        # Filtro por submissão
        submission_id = self.request.query_params.get('submission')
        if submission_id:
            queryset = queryset.filter(submissao_id=submission_id)

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return AvaliacaoCreateSerializer
        return AvaliacaoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        avaliacao = serializer.save()

        # Retorna a avaliação criada
        output_serializer = AvaliacaoSerializer(avaliacao)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
