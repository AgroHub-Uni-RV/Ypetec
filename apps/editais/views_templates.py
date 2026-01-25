"""
Views de templates para o app Editais.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Edital


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para views que requerem admin."""

    def test_func(self):
        return self.request.user.role == 'ADMIN'

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito a administradores.')
        return redirect('home:index')


class EditalListView(ListView):
    """Lista de editais."""
    model = Edital
    template_name = 'editais/lista.html'
    context_object_name = 'editais'
    paginate_by = 12

    def get_queryset(self):
        return Edital.objects.filter(
            status=Edital.Status.PUBLICADO
        ).order_by('-inicio')


class EditalDetailView(DetailView):
    """Detalhe de um edital."""
    model = Edital
    template_name = 'editais/detalhe.html'
    context_object_name = 'edital'


class EditalCreateView(AdminRequiredMixin, CreateView):
    """Criar edital (admin)."""
    model = Edital
    template_name = 'editais/form.html'
    fields = ['titulo', 'descricao', 'inicio', 'fim']
    success_url = reverse_lazy('editais:lista')

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        form.instance.status = Edital.Status.PUBLICADO
        messages.success(self.request, 'Edital criado com sucesso!')
        return super().form_valid(form)
