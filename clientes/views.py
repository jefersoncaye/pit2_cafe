from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from .models import Clientes
from home.views import home
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login


# Create your views here.
@csrf_exempt
def cadastro_cliente(request):
    return render(request, 'cadastro_cliente.html')


@csrf_exempt
def cadastrar_cliente(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        endereco = request.POST.get('endereco')

        # Cria o usuário usando o modelo User do Django
        user = User.objects.create_user(username=nome, email=email, password=senha)

        # Cria o cliente associado ao usuário
        Clientes.objects.create(user=user, endereco=endereco)

        # Loga o usuário automaticamente após o cadastro
        auth_login(request, user)

        # Redireciona para a página inicial com a query string ?sucesso=True
        return HttpResponseRedirect(reverse('home') + '?sucesso=True')

    # Se não for POST, renderiza o formulário de cadastro
    return render(request, 'cadastro_cliente.html')


@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST.get('name')
        senha = request.POST.get('password')  # O nome do campo no HTML é 'password'

        # Autentica o usuário usando o sistema padrão de autenticação do Django
        user = authenticate(request, username=email, password=senha)

        if user is not None:
            # Usuário autenticado com sucesso
            auth_login(request, user)
            return redirect('home')
        else:
            # Credenciais inválidas
            messages.error(request, 'Email ou senha incorretos. Tente novamente.')
            return redirect('login')

    # Se não for POST, renderiza o formulário de login
    return render(request, 'login.html')
