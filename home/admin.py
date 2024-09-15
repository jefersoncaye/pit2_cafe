from django.contrib import admin
from .models import Produtos, ItemCarrinho, Carrinho, Pedido, ItemPedido

# Register your models here.

admin.site.register(Produtos)
admin.site.register(ItemCarrinho)
admin.site.register(Carrinho)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
