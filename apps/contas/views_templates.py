"""
Views de templates para o app Contas (autenticação).
"""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView

from .models import Usuario


class TemplateLoginView(View):
    """View de login para templates."""
    template_name = 'auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home:index')
        return render(request, self.template_name)

    def post(self, request):
        cpf = request.POST.get('cpf', '').replace('.', '').replace('-', '')
        password = request.POST.get('password', '')

        try:
            user = Usuario.objects.get(cpf=cpf)
            if user.check_password(password):
                if user.status == Usuario.Status.ATIVO:
                    login(request, user)
                    next_url = request.GET.get('next', '/')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Usuário inativo. Entre em contato com o administrador.')
            else:
                messages.error(request, 'CPF ou senha inválidos.')
        except Usuario.DoesNotExist:
            messages.error(request, 'CPF ou senha inválidos.')

        return render(request, self.template_name)


def template_logout_view(request):
    """View de logout para templates."""
    logout(request)
    messages.success(request, 'Você saiu com sucesso.')
    return redirect('home:index')


class TemplateRegisterView(View):
    """View de registro para templates."""
    template_name = 'auth/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home:index')
        return render(request, self.template_name)

    def post(self, request):
        cpf = request.POST.get('cpf', '').replace('.', '').replace('-', '')
        email = request.POST.get('email', '').strip()
        name = request.POST.get('name', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        # Validações
        if not all([cpf, email, name, password]):
            messages.error(request, 'Preencha todos os campos.')
            return render(request, self.template_name)

        if password != password2:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, self.template_name)

        if len(password) < 6:
            messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            return render(request, self.template_name)

        if Usuario.objects.filter(cpf=cpf).exists():
            messages.error(request, 'CPF já cadastrado.')
            return render(request, self.template_name)

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Email já cadastrado.')
            return render(request, self.template_name)

        # Criar usuário
        user = Usuario.objects.create_user(
            cpf=cpf,
            email=email,
            name=name,
            password=password,
            role=Usuario.Role.ALUNO
        )

        messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
        return redirect('contas:login')


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para views que requerem admin."""

    def test_func(self):
        return self.request.user.role == 'ADMIN'

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito a administradores.')
        return redirect('home:index')


class UsuarioListView(AdminRequiredMixin, ListView):
    """Lista de usuários para admin."""
    model = Usuario
    template_name = 'usuarios/gerenciar.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        qs = Usuario.objects.all().order_by('-created_at')
        role = self.request.GET.get('role')
        if role:
            qs = qs.filter(role=role)
        return qs
