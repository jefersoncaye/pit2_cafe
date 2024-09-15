from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Produtos, Carrinho, ItemCarrinho, Pedido, ItemPedido
from django.http import JsonResponse
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

def home(request):
    produtos = Produtos.objects.all()
    return render(request, 'index.html', {'produtos': produtos})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Produtos, Carrinho, ItemCarrinho

def adicionar_ao_carrinho(request):
    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        quantidade = int(request.POST.get('quantidade', 1))

        # Obtém o produto selecionado
        produto = get_object_or_404(Produtos, id=produto_id)
        preco = produto.preco

        # Verifica se o usuário está logado
        if request.user.is_authenticated:
            # Se o usuário está logado, utiliza o carrinho associado ao usuário
            usuario = request.user
            carrinho, criado = Carrinho.objects.get_or_create(cliente_id=usuario)
        else:
            # Se o usuário não está logado, utiliza a sessão para armazenar o carrinho
            carrinho = request.session.get('carrinho', {})

            # Verifica se o produto já está no carrinho
            if str(produto_id) in carrinho:
                carrinho[str(produto_id)]['quantidade'] += quantidade
                carrinho[str(produto_id)]['preco_total'] = carrinho[str(produto_id)]['preco'] * carrinho[str(produto_id)]['quantidade']
            else:
                carrinho[str(produto_id)] = {
                    'produto_id': produto_id,
                    'nome': produto.nome,
                    'preco': float(preco),  # Convertendo para float para serializar o JSON
                    'quantidade': quantidade,
                    'preco_total': float(preco * quantidade)
                }

            # Armazena o carrinho atualizado na sessão
            request.session['carrinho'] = carrinho

        # Caso o usuário esteja logado, salva os itens no banco de dados
        if request.user.is_authenticated:
            # Verifica se o item já está no carrinho do usuário
            item, criado = ItemCarrinho.objects.get_or_create(
                carrinho_id=carrinho,
                produto_id=produto,
                defaults={'quantidade': quantidade, 'preco': preco, 'preco_total': float(preco * quantidade)},
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
        carrinho, criado = Carrinho.objects.get_or_create(cliente_id=request.user)

        # Filtra os itens do carrinho usando a instância do carrinho
        itens_carrinho = ItemCarrinho.objects.filter(carrinho_id=carrinho.id)

        # Calcula o total dos itens no carrinho
        total = sum(item.preco * item.quantidade for item in itens_carrinho)

    else:
        # Obtém o carrinho da sessão
        carrinho_sessao = request.session.get('carrinho', {})

        # Converte os itens da sessão em uma lista para exibir no template
        itens_carrinho = [{
            'produto_id': item_info['produto_id'],
            'nome': item_info['nome'],
            'preco': item_info['preco'],
            'quantidade': item_info['quantidade'],
            'preco_total': item_info['preco_total']
        } for item_info in carrinho_sessao.values()]

        # Calcula o total dos itens no carrinho da sessão
        total = sum(item['preco_total'] for item in itens_carrinho)

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
        messages.error(request, "Carrinho não encontrado! É necessario logar no sistema")
        return redirect('login')


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

@receiver(user_logged_in)
def transferir_carrinho_sessao(sender, request, user, **kwargs):
    carrinho_sessao = request.session.get('carrinho', {})

    if carrinho_sessao:
        carrinho, _ = Carrinho.objects.get_or_create(cliente_id=user)

        for produto_id, detalhes in carrinho_sessao.items():
            produto = get_object_or_404(Produtos, id=produto_id)
            item, criado = ItemCarrinho.objects.get_or_create(
                carrinho_id=carrinho,
                produto_id=produto,
                defaults={'quantidade': detalhes['quantidade'], 'preco': detalhes['preco']}
            )

            if not criado:
                item.quantidade += detalhes['quantidade']
                item.preco_total = item.preco * item.quantidade
                item.save()

        # Limpa o carrinho da sessão
        request.session['carrinho'] = {}