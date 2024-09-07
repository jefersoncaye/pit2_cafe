from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Produtos(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.IntegerField()
    imagem = models.ImageField(upload_to='produtos/')

    class Meta:
        db_table = 'produtos'

    def __str__(self):
        return self.nome

class Carrinho(models.Model):
    cliente_id = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'carrinho'

class ItemCarrinho(models.Model):
    carrinho_id = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto_id = models.ForeignKey(Produtos, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField()
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'carrinho_produtos'

class Pedido(models.Model):
    cliente_id = models.ForeignKey(User, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pendente')


    class Meta:
        db_table = 'pedido'

class ItemPedido(models.Model):
    pedido_id = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto_id = models.ForeignKey(Produtos, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField()
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'pedido_produtos'
