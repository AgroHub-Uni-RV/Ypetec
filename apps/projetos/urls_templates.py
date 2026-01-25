"""
URLs de templates para o app Projetos.
"""
from django.urls import path

from . import views_templates

app_name = 'projetos'

urlpatterns = [
    path('meus/', views_templates.MeusProjetosView.as_view(), name='meus_projetos'),
    path('criar/', views_templates.ProjetoCreateView.as_view(), name='criar'),
    path('<int:pk>/', views_templates.ProjetoDetailView.as_view(), name='detalhe'),
    path('<int:projeto_pk>/submeter/', views_templates.SubmeterProjetoView.as_view(), name='submeter'),
]
