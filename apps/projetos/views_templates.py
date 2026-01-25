"""
Views de templates para o app Projetos.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from apps.editais.models import Edital

from .models import Projeto, Submissao


class AlunoRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para views que requerem aluno."""

    def test_func(self):
        return self.request.user.role == 'ALUNO'

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito a alunos.')
        return redirect('home:index')


class MeusProjetosView(AlunoRequiredMixin, ListView):
    """Lista de projetos do aluno."""
    model = Projeto
    template_name = 'projetos/meus_projetos.html'
    context_object_name = 'projetos'

    def get_queryset(self):
        return Projeto.objects.filter(
            responsavel=self.request.user
        ).order_by('-created_at')


class ProjetoCreateView(AlunoRequiredMixin, CreateView):
    """Criar projeto."""
    model = Projeto
    template_name = 'projetos/criar.html'
    fields = ['titulo', 'resumo', 'area']
    success_url = reverse_lazy('projetos:meus_projetos')

    def form_valid(self, form):
        form.instance.responsavel = self.request.user
        messages.success(self.request, 'Projeto criado com sucesso!')
        return super().form_valid(form)


class ProjetoDetailView(LoginRequiredMixin, DetailView):
    """Detalhe de um projeto."""
    model = Projeto
    template_name = 'projetos/detalhe.html'
    context_object_name = 'projeto'


class SubmeterProjetoView(AlunoRequiredMixin, View):
    """View para submeter projeto a edital."""
    template_name = 'projetos/submeter.html'

    def get(self, request, projeto_pk):
        projeto = get_object_or_404(Projeto, pk=projeto_pk, responsavel=request.user)

        # Apenas projetos PRE_SUBMISSAO podem ser submetidos
        if projeto.status != Projeto.Status.PRE_SUBMISSAO:
            messages.warning(request, 'Este projeto já foi submetido a um edital.')
            return redirect('projetos:detalhe', pk=projeto_pk)

        # Listar editais abertos
        hoje = timezone.now()
        editais = Edital.objects.filter(
            status=Edital.Status.PUBLICADO,
            inicio__lte=hoje,
            fim__gte=hoje
        )

        return render(request, self.template_name, {
            'projeto': projeto,
            'editais': editais
        })

    def post(self, request, projeto_pk):
        projeto = get_object_or_404(Projeto, pk=projeto_pk, responsavel=request.user)
        edital_pk = request.POST.get('edital')

        # Validações
        if not edital_pk:
            messages.error(request, 'Selecione um edital.')
            return redirect('projetos:submeter', projeto_pk=projeto_pk)

        if projeto.status != Projeto.Status.PRE_SUBMISSAO:
            messages.warning(request, 'Este projeto já foi submetido.')
            return redirect('projetos:detalhe', pk=projeto_pk)

        edital = get_object_or_404(Edital, pk=edital_pk)

        # Verificar se edital está aberto
        hoje = timezone.now()
        if not (edital.status == Edital.Status.PUBLICADO and
                edital.inicio <= hoje <= edital.fim):
            messages.error(request, 'Este edital não está aberto para submissões.')
            return redirect('projetos:submeter', projeto_pk=projeto_pk)

        # Verificar se já existe submissão para este edital
        if Submissao.objects.filter(projeto=projeto, edital=edital).exists():
            messages.warning(request, 'Projeto já submetido a este edital.')
            return redirect('projetos:detalhe', pk=projeto_pk)

        # Criar submissão
        Submissao.objects.create(
            projeto=projeto,
            edital=edital,
            status=Submissao.Status.ENVIADA
        )

        # Atualizar status do projeto
        projeto.status = Projeto.Status.SUBMETIDO
        projeto.save()

        messages.success(request, f'Projeto submetido ao edital "{edital.titulo}" com sucesso!')
        return redirect('projetos:detalhe', pk=projeto_pk)
