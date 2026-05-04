from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from decimal import Decimal, InvalidOperation

from application.services import ProdutoService
from apps.usuarios.decorators import admin_required
from .models import Produto

_svc = ProdutoService()


@method_decorator(login_required, name='dispatch')
class ProdutoListView(View):
    """RF05 — Consulta de produtos. Disponível para todos os perfis."""
    def get(self, request):
        q = request.GET.get('q', '').strip()
        produtos = Produto.objects.all().order_by('nome')
        if q:
            produtos = produtos.filter(nome__icontains=q)
        return render(request, 'produtos/lista.html', {
            'produtos': produtos,
            'q': q,
            'pode_editar': request.user.is_admin,
        })


@method_decorator([login_required, admin_required], name='dispatch')
class ProdutoCreateView(View):
    """RF03 — Cadastro de produtos. Restrito a ADMIN."""
    def get(self, request):
        return render(request, 'produtos/form.html', {'titulo': 'Novo Produto'})

    def post(self, request):
        try:
            preco = Decimal(request.POST.get('preco', '0').replace(',', '.'))
            _svc.cadastrar(
                nome=request.POST.get('nome', ''),
                descricao=request.POST.get('descricao', ''),
                preco=preco,
                quantidade_estoque=int(request.POST.get('quantidade_estoque', 0)),
            )
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('produto_lista')
        except (ValueError, InvalidOperation) as e:
            messages.error(request, str(e))
            return render(request, 'produtos/form.html',
                          {'titulo': 'Novo Produto', 'dados': request.POST})


@method_decorator([login_required, admin_required], name='dispatch')
class ProdutoEditView(View):
    """RF04 — Atualização de produtos. Restrito a ADMIN."""
    def get(self, request, pk):
        obj = get_object_or_404(Produto, pk=pk)
        return render(request, 'produtos/form.html',
                      {'titulo': 'Editar Produto', 'dados': obj, 'editando': True, 'pk': pk})

    def post(self, request, pk):
        try:
            preco = Decimal(request.POST.get('preco', '0').replace(',', '.'))
            _svc.atualizar(pk,
                nome=request.POST.get('nome', ''),
                descricao=request.POST.get('descricao', ''),
                preco=preco,
                quantidade_estoque=int(request.POST.get('quantidade_estoque', 0)),
            )
            messages.success(request, 'Produto atualizado!')
            return redirect('produto_lista')
        except (ValueError, InvalidOperation) as e:
            obj = get_object_or_404(Produto, pk=pk)
            messages.error(request, str(e))
            return render(request, 'produtos/form.html',
                          {'titulo': 'Editar Produto', 'dados': obj, 'editando': True, 'pk': pk})


@method_decorator([login_required, admin_required], name='dispatch')
class ProdutoDeleteView(View):
    """Exclusão de produtos. Restrito a ADMIN."""
    def post(self, request, pk):
        _svc.remover(pk)
        messages.success(request, 'Produto removido.')
        return redirect('produto_lista')
