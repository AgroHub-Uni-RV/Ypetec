"""
Views da página inicial (Home).
"""
from django.shortcuts import render
from django.utils import timezone

from apps.editais.models import Edital
from apps.publicacoes.models import Publicacao


def index(request):
    """Página inicial com editais abertos e projetos aprovados."""
    hoje = timezone.now()

    # Editais abertos (dentro do período)
    editais_abertos = Edital.objects.filter(
        status=Edital.Status.PUBLICADO,
        inicio__lte=hoje,
        fim__gte=hoje
    ).order_by('fim')[:6]

    # Editais futuros
    editais_futuros = Edital.objects.filter(
        status=Edital.Status.PUBLICADO,
        inicio__gt=hoje
    ).order_by('inicio')[:3]

    # Publicações ativas (projetos aprovados)
    publicacoes = Publicacao.objects.filter(
        ativo=True
    ).select_related('projeto').order_by('-destaque', '-publicado_em')[:6]

    context = {
        'editais_abertos': editais_abertos,
        'editais_futuros': editais_futuros,
        'publicacoes': publicacoes,
    }

    return render(request, 'home/index.html', context)
