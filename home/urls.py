from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import home

urlpatterns = [
    path("", home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('adicionar-ao-carrinho/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('remover-do-carrinho/<int:item_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('carrinho/', views.visualizar_carrinho, name='carrinho'),
    path('pedidos/', views.visualizar_pedidos, name='pedidos'),
    path('finalizar-pedido/', views.finalizar_pedido, name='finalizar_pedido'),
]