from django.contrib import admin
from .models import Produtos, ItemCarrinho, Carrinho

# Register your models here.

admin.site.register(Produtos)
admin.site.register(ItemCarrinho)
admin.site.register(Carrinho)
