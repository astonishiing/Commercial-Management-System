import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View

from application.services import VendaService
from apps.clientes.models import Cliente
from apps.produtos.models import Produto
from .models import Venda

_svc = VendaService()


@method_decorator(login_required, name='dispatch')
class VendaListView(View):
    def get(self, request):
        vendas = Venda.objects.select_related('cliente', 'usuario').all()
        return render(request, 'vendas/lista.html', {'vendas': vendas})


@method_decorator(login_required, name='dispatch')
class VendaDetailView(View):
    def get(self, request, pk):
        venda = get_object_or_404(
            Venda.objects.select_related('cliente', 'usuario').prefetch_related('itens__produto'),
            pk=pk
        )
        return render(request, 'vendas/detalhe.html', {'venda': venda})


@method_decorator(login_required, name='dispatch')
class VendaCreateView(View):
    def get(self, request):
        clientes = Cliente.objects.all().order_by('nome')
        produtos = Produto.objects.filter(quantidade_estoque__gt=0).order_by('nome')
        return render(request, 'vendas/form.html', {
            'clientes': clientes,
            'produtos': produtos,
            'produtos_json': json.dumps([
                {'id': p.id, 'nome': p.nome,
                 'preco': float(p.preco),
                 'estoque': p.quantidade_estoque}
                for p in produtos
            ])
        })

    def post(self, request):
        try:
            # Coleta os itens do formulário dinâmico
            # O form envia: produto_id[], quantidade[]
            produto_ids  = request.POST.getlist('produto_id[]')
            quantidades  = request.POST.getlist('quantidade[]')

            if not produto_ids:
                raise ValueError("Adicione ao menos um produto à venda.")

            itens_data = [
                {'produto_id': int(pid), 'quantidade': int(qty)}
                for pid, qty in zip(produto_ids, quantidades)
                if pid and qty
            ]

            venda = _svc.registrar(
                cliente_id=int(request.POST.get('cliente_id')),
                usuario_id=request.user.id,
                itens_data=itens_data,
            )
            messages.success(request, f'Venda #{venda.id} registrada! Total: R$ {venda.calcular_total():.2f}')
            return redirect('venda_detalhe', pk=venda.id)
        except (ValueError, TypeError) as e:
            messages.error(request, str(e))
            clientes = Cliente.objects.all().order_by('nome')
            produtos = Produto.objects.filter(quantidade_estoque__gt=0).order_by('nome')
            return render(request, 'vendas/form.html', {
                'clientes': clientes,
                'produtos': produtos,
                'produtos_json': json.dumps([
                    {'id': p.id, 'nome': p.nome,
                     'preco': float(p.preco),
                     'estoque': p.quantidade_estoque}
                    for p in produtos
                ])
            })
