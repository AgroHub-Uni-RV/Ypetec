"""
Views de templates para o app Avaliações.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from apps.projetos.models import Projeto, Submissao

from .models import Avaliacao


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para views que requerem admin."""

    def test_func(self):
        return self.request.user.role == 'ADMIN'

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito a administradores.')
        return redirect('home:index')


class AvaliacaoListView(AdminRequiredMixin, ListView):
    """Lista de submissões para avaliação (admin)."""
    model = Submissao
    template_name = 'avaliacoes/lista.html'
    context_object_name = 'submissoes'
    paginate_by = 20

    def get_queryset(self):
        return Submissao.objects.select_related(
            'projeto', 'edital'
        ).order_by('-submetido_em')


class AvaliarSubmissaoView(AdminRequiredMixin, View):
    """View para avaliar uma submissão."""

    def post(self, request, submissao_pk):
        submissao = get_object_or_404(Submissao, pk=submissao_pk)
        resultado = request.POST.get('resultado')
        comentarios = request.POST.get('comentarios', '').strip()

        # Validar resultado
        resultados_validos = ['APROVADO', 'REPROVADO', 'NECESSITA_AJUSTES']
        if resultado not in resultados_validos:
            messages.error(request, 'Selecione um resultado válido.')
            return redirect('avaliacoes:lista')

        # Verificar se submissão pode ser avaliada
        if submissao.status not in [Submissao.Status.ENVIADA, Submissao.Status.EM_AVALIACAO]:
            messages.warning(request, 'Esta submissão já foi avaliada.')
            return redirect('avaliacoes:lista')

        # Criar avaliação
        Avaliacao.objects.create(
            submissao=submissao,
            avaliador=request.user,
            resultado=resultado,
            comentarios=comentarios
        )

        # Atualizar status da submissão e projeto
        projeto = submissao.projeto

        if resultado == 'APROVADO':
            submissao.status = Submissao.Status.APROVADA
            projeto.status = Projeto.Status.APROVADO
            msg = f'Submissão de "{projeto.titulo}" APROVADA!'
        elif resultado == 'REPROVADO':
            submissao.status = Submissao.Status.REPROVADA
            projeto.status = Projeto.Status.REPROVADO
            msg = f'Submissão de "{projeto.titulo}" reprovada.'
        else:  # NECESSITA_AJUSTES
            submissao.status = Submissao.Status.AJUSTES_SOLICITADOS
            projeto.status = Projeto.Status.AJUSTES
            msg = f'Ajustes solicitados para "{projeto.titulo}".'

        submissao.save()
        projeto.save()

        messages.success(request, msg)
        return redirect('avaliacoes:lista')
