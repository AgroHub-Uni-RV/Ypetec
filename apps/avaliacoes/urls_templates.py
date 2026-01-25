"""
URLs de templates para o app Avaliações.
"""
from django.urls import path

from . import views_templates

app_name = 'avaliacoes'

urlpatterns = [
    path('', views_templates.AvaliacaoListView.as_view(), name='lista'),
    path('<int:submissao_pk>/avaliar/', views_templates.AvaliarSubmissaoView.as_view(), name='avaliar'),
]
