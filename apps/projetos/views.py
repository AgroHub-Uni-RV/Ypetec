"""
Views para projetos, submissões e relatórios.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.contas.permissions import IsAdmin, IsAluno, IsOwnerOrAdmin

from .models import MembroEquipe, Projeto, RelatorioProgresso, Submissao
from .serializers import (
    MembroEquipeSerializer,
    ProjetoCreateSerializer,
    ProjetoListSerializer,
    ProjetoSerializer,
    RelatorioProgressoSerializer,
    SubmissaoCreateSerializer,
    SubmissaoSerializer,
)


class ProjetoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para projetos.

    POST   /api/projects/                    - Cria projeto (aluno)
    GET    /api/students/me/projects/        - Lista projetos do aluno
    POST   /api/projects/:id/disengage/      - Solicita desligamento
    GET    /api/students/me/incubated-projects/ - Projetos incubados (para mentoria)
    GET    /api/projects/report/             - Relatório completo (admin)
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Projeto.objects.all()
        return Projeto.objects.filter(responsavel=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjetoCreateSerializer
        if self.action in ['list', 'my_projects']:
            return ProjetoListSerializer
        return ProjetoSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsAluno()]
        if self.action == 'report':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='my-projects')
    def my_projects(self, request):
        """
        GET /api/students/me/projects

        Lista projetos do aluno logado com última submissão/avaliação.
        """
        queryset = Projeto.objects.filter(
            responsavel=request.user
        ).prefetch_related(
            'submissoes__edital',
            'submissoes__avaliacoes'
        ).order_by('-created_at')

        serializer = ProjetoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def disengage(self, request, pk=None):
        """
        POST /api/projects/:id/disengage

        Solicita desligamento do projeto (soft delete).
        """
        projeto = self.get_object()

        # Verifica se é o responsável
        if projeto.responsavel != request.user:
            return Response(
                {'detail': 'Você não é responsável por este projeto.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verifica se pode ser desligado
        status_permitidos = [
            Projeto.Status.INCUBADO,
            Projeto.Status.APROVADO,
            Projeto.Status.SUBMETIDO,
            Projeto.Status.PRE_SUBMISSAO,
            Projeto.Status.AJUSTES,
            Projeto.Status.INATIVO,
        ]
        if projeto.status not in status_permitidos:
            return Response(
                {'detail': f'Projeto com status "{projeto.status}" não pode ser desligado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Soft delete
        projeto.status = Projeto.Status.DESLIGADO
        projeto.delete()  # Usa soft delete do BaseModel

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='incubated')
    def incubated(self, request):
        """
        GET /api/students/me/incubated-projects

        Lista projetos incubados do aluno (para dropdown de mentoria).
        """
        queryset = Projeto.objects.filter(
            responsavel=request.user,
            status=Projeto.Status.INCUBADO,
        ).order_by('titulo')

        data = [{'id': p.id, 'title': p.titulo} for p in queryset]
        return Response(data)

    @action(detail=False, methods=['get'])
    def report(self, request):
        """
        GET /api/projects/report

        Relatório completo de projetos (admin).
        """
        queryset = Projeto.objects.select_related(
            'responsavel'
        ).prefetch_related(
            'submissoes__edital',
            'submissoes__avaliacoes__avaliador'
        ).order_by('-id')

        serializer = ProjetoSerializer(queryset, many=True)
        return Response(serializer.data)


class SubmissaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para submissões.

    POST /api/submissions/     - Cria submissão (aluno)
    GET  /api/submissions/     - Lista submissões (admin)
    """

    serializer_class = SubmissaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Submissao.objects.select_related(
            'projeto', 'edital'
        ).prefetch_related(
            'avaliacoes'
        ).filter(
            projeto__status__in=[
                Projeto.Status.SUBMETIDO,
                Projeto.Status.APROVADO,
                Projeto.Status.INCUBADO,
                Projeto.Status.AJUSTES,
            ]
        ).exclude(
            projeto__status=Projeto.Status.DESLIGADO
        ).order_by('-submetido_em')

        # Filtro por status de avaliação
        status_filter = self.request.query_params.get('status')
        if status_filter == 'pending':
            queryset = queryset.filter(avaliacoes__isnull=True)
        elif status_filter == 'evaluated':
            queryset = queryset.filter(avaliacoes__isnull=False).distinct()

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return SubmissaoCreateSerializer
        return SubmissaoSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsAluno()]
        return [IsAuthenticated(), IsAdmin()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submissao = serializer.save()

        # Retorna a submissão criada
        output_serializer = SubmissaoSerializer(submissao)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
