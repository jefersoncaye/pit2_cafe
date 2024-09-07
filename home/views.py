from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Produtos, Carrinho, ItemCarrinho, Pedido, ItemPedido
from django.http import JsonResponse
from django.utils import timezone


def home(request):
    produtos = Produtos.objects.all()
    return render(request, 'index.html', {'produtos': produtos})


def adicionar_ao_carrinho(request):
    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        quantidade = int(request.POST.get('quantidade', 1))

        # Obtém o produto selecionado
        produto = get_object_or_404(Produtos, id=produto_id)
        preco = produto.preco
        usuario = request.user

        # Obtém ou cria um carrinho para o usuário
        carrinho, criado = Carrinho.objects.get_or_create(cliente_id=usuario)
        # Verifica se o item já está no carrinho
        item, criado = ItemCarrinho.objects.get_or_create(
            carrinho_id=carrinho,
            produto_id=produto,
            defaults={'quantidade': quantidade, 'preco': preco},
            preco_total = preco * quantidade
        )

        if not criado:
            # Se o item já existia, atualiza a quantidade
            item.quantidade += quantidade
            item.preco_total = item.preco * item.quantidade
            item.save()

        # Retorna uma resposta JSON
        return JsonResponse({'status': 'success', 'message': f'Produto "{produto.nome}" adicionado ao carrinho com sucesso!'})

    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


def visualizar_carrinho(request):
    if request.user.is_authenticated:
        # Obtenha ou crie o carrinho para o usuário autenticado
        carrinho, criado = Carrinho.objects.get_or_create(cliente_id=request.user.id)

        # Filtra os itens do carrinho usando a instância do carrinho
        itens_carrinho = ItemCarrinho.objects.filter(carrinho_id=carrinho.id)

        # Calcula o total dos itens no carrinho
        total = sum(item.preco * item.quantidade for item in itens_carrinho)
    else:
        itens_carrinho = []
        total = 0

    return render(request, 'carrinho.html', {
        'itens_carrinho': itens_carrinho,
        'total': total
    })


def finalizar_pedido(request):
    try:
        # Obtém ou cria o carrinho para o usuário
        carrinho = Carrinho.objects.get(cliente_id=request.user.id)
        itens_carrinho = ItemCarrinho.objects.filter(carrinho_id=carrinho.id)

        if not itens_carrinho.exists():
            messages.error(request, "Seu carrinho está vazio!")
            return redirect('home')  # Redireciona para a página inicial ou onde desejar

        # Calcula o valor total do pedido
        total = sum(item.preco_total for item in itens_carrinho)

        # Cria um novo pedido
        pedido = Pedido.objects.create(
            cliente_id=request.user,
            total=total,
            status='Pendente'
        )

        # Transfere itens do carrinho para o pedido
        for item in itens_carrinho:
            ItemPedido.objects.create(
                pedido_id=pedido,
                produto_id=item.produto_id,
                preco=item.preco,
                quantidade=item.quantidade,
                preco_total=item.preco_total
            )

        # Limpa o carrinho
        itens_carrinho.delete()

        messages.success(request, "Pedido realizado com sucesso!")
        return redirect('pedidos')  # Redireciona para uma página de confirmação de pedido

    except Carrinho.DoesNotExist:
        messages.error(request, "Carrinho não encontrado!")
        return redirect('home')


def visualizar_pedidos(request):
    # Obtém todos os pedidos do usuário
    pedidos = Pedido.objects.filter(cliente_id=request.user).order_by('-data_pedido')

    # Cria um dicionário para armazenar os itens dos pedidos
    pedidos_info = []
    for pedido in pedidos:
        itens = ItemPedido.objects.filter(pedido_id=pedido.id)
        pedidos_info.append({
            'pedido': pedido,
            'itens': itens
        })

    return render(request, 'pedidos.html', {'pedidos_info': pedidos_info})