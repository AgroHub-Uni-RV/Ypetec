"""
URLs do app contas.

Endpoints de autenticação e gerenciamento de usuários.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ForgotPasswordView,
    LoginView,
    MeView,
    RegisterView,
    ResetPasswordView,
    UsuarioViewSet,
)

router = DefaultRouter()
router.register('users', UsuarioViewSet, basename='usuario')

urlpatterns = [
    # Auth endpoints (compatíveis com sistema Node.js)
    path('auth/login', LoginView.as_view(), name='auth-login'),
    path('auth/register', RegisterView.as_view(), name='auth-register'),
    path('auth/me', MeView.as_view(), name='auth-me'),
    path('auth/forgot', ForgotPasswordView.as_view(), name='auth-forgot'),
    path('auth/reset', ResetPasswordView.as_view(), name='auth-reset'),

    # Token refresh (JWT)
    path('auth/refresh', TokenRefreshView.as_view(), name='auth-refresh'),

    # Users management (admin)
    path('', include(router.urls)),
]
