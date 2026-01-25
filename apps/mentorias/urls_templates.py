"""
URLs de templates para o app Mentorias.
"""
from django.urls import path

from . import views_templates

app_name = 'mentorias'

urlpatterns = [
    path('solicitar/', views_templates.SolicitarMentoriaView.as_view(), name='solicitar'),
    path('gerenciar/', views_templates.GerenciarMentoriasView.as_view(), name='gerenciar'),
    path('<int:pk>/atualizar/', views_templates.AtualizarMentoriaView.as_view(), name='atualizar'),
]
