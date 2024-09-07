from django.urls import path

from .views import cadastro_cliente, login, cadastrar_cliente

urlpatterns = [
    path("", cadastro_cliente, name='clientes'),
    path("login/", login, name='login'),
    path("cadastrar_cliente/", cadastrar_cliente, name='cadastrar_cliente'),
]