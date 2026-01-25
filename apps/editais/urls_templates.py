"""
URLs de templates para o app Editais.
"""
from django.urls import path

from . import views_templates

app_name = 'editais'

urlpatterns = [
    path('', views_templates.EditalListView.as_view(), name='lista'),
    path('<int:pk>/', views_templates.EditalDetailView.as_view(), name='detalhe'),
    path('criar/', views_templates.EditalCreateView.as_view(), name='criar'),
]
