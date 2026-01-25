"""
Views de templates para o app Mentorias.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView

from apps.projetos.models import Projeto

from .models import SolicitacaoMentoria


class AlunoRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para views que requerem aluno."""

    def test_func(self):
        return self.request.user.role == 'ALUNO'

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito a alunos.')
        return redirect('home:index')


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para views que requerem admin."""

    def test_func(self):
        return self.request.user.role == 'ADMIN'

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito a administradores.')
        return redirect('home:index')


class SolicitarMentoriaView(AlunoRequiredMixin, View):
    """View para solicitar mentoria."""
    template_name = 'mentorias/solicitar.html'

    def get(self, request):
        # Listar apenas projetos INCUBADOS do aluno
        projetos = Projeto.objects.filter(
            responsavel=request.user,
            status=Projeto.Status.INCUBADO
        )
        return render(request, self.template_name, {'projetos': projetos})

    def post(self, request):
        projeto_pk = request.POST.get('projeto')
        area = request.POST.get('area', '').strip()
        justificativa = request.POST.get('justificativa', '').strip()

        # Validações
        if not all([projeto_pk, area, justificativa]):
            messages.error(request, 'Preencha todos os campos.')
            return redirect('mentorias:solicitar')

        # Verificar se projeto pertence ao usuário e está incubado
        projeto = get_object_or_404(
            Projeto,
            pk=projeto_pk,
            responsavel=request.user,
            status=Projeto.Status.INCUBADO
        )

        # Verificar se já existe solicitação pendente para este projeto
        if SolicitacaoMentoria.objects.filter(
            projeto=projeto,
            status=SolicitacaoMentoria.Status.SOLICITADA
        ).exists():
            messages.warning(request, 'Já existe uma solicitação pendente para este projeto.')
            return redirect('mentorias:solicitar')

        # Criar solicitação
        SolicitacaoMentoria.objects.create(
            projeto=projeto,
            area=area,
            justificativa=justificativa,
            solicitante=request.user
        )

        messages.success(request, 'Solicitação de mentoria enviada com sucesso!')
        return redirect('projetos:meus_projetos')


class GerenciarMentoriasView(AdminRequiredMixin, ListView):
    """Lista de solicitações de mentoria para admin."""
    model = SolicitacaoMentoria
    template_name = 'mentorias/gerenciar.html'
    context_object_name = 'solicitacoes'
    paginate_by = 20

    def get_queryset(self):
        return SolicitacaoMentoria.objects.select_related(
            'projeto', 'solicitante'
        ).order_by('-created_at')


class AtualizarMentoriaView(AdminRequiredMixin, View):
    """View para aprovar/negar/concluir mentoria."""

    def post(self, request, pk):
        solicitacao = get_object_or_404(SolicitacaoMentoria, pk=pk)
        acao = request.POST.get('acao')

        if acao == 'aprovar':
            solicitacao.status = SolicitacaoMentoria.Status.EM_ANDAMENTO
            messages.success(request, f'Mentoria para "{solicitacao.projeto.titulo}" aprovada!')
        elif acao == 'negar':
            solicitacao.status = SolicitacaoMentoria.Status.NEGADA
            messages.warning(request, f'Mentoria para "{solicitacao.projeto.titulo}" negada.')
        elif acao == 'concluir':
            solicitacao.status = SolicitacaoMentoria.Status.CONCLUIDA
            messages.success(request, f'Mentoria para "{solicitacao.projeto.titulo}" concluída!')
        else:
            messages.error(request, 'Ação inválida.')
            return redirect('mentorias:gerenciar')

        solicitacao.save()
        return redirect('mentorias:gerenciar')
