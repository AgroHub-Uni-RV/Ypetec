"""
URLs de templates para o app Contas (autenticação).
"""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views_templates

app_name = 'contas'

urlpatterns = [
    # Login
    path('login/', views_templates.TemplateLoginView.as_view(), name='login'),

    # Logout
    path('logout/', views_templates.template_logout_view, name='logout'),

    # Registro
    path('register/', views_templates.TemplateRegisterView.as_view(), name='register'),

    # Lista de usuários (admin)
    path('usuarios/', views_templates.UsuarioListView.as_view(), name='lista_usuarios'),
]
