"""
URLs de templates para o app Publicações.
"""
from django.urls import path

from . import views_templates

app_name = 'publicacoes'

urlpatterns = [
    path('', views_templates.VitrineView.as_view(), name='vitrine'),
]
