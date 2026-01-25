"""
Views de templates para o app Publicações.
"""
from django.views.generic import ListView

from .models import Publicacao


class VitrineView(ListView):
    """Vitrine de projetos aprovados (público)."""
    model = Publicacao
    template_name = 'publicacoes/vitrine.html'
    context_object_name = 'publicacoes'
    paginate_by = 12

    def get_queryset(self):
        return Publicacao.objects.filter(
            ativo=True
        ).select_related('projeto').order_by('-destaque', '-publicado_em')
