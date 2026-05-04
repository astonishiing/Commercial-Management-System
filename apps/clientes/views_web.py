from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View

from application.services import ClienteService
from apps.usuarios.decorators import admin_required
from .models import Cliente

_svc = ClienteService()


@method_decorator(login_required, name='dispatch')
class ClienteListView(View):
    """RF02 — Consulta de clientes. Disponível para todos os perfis."""
    def get(self, request):
        q = request.GET.get('q', '').strip()
        clientes = Cliente.objects.all().order_by('nome')
        if q:
            clientes = clientes.filter(nome__icontains=q) | clientes.filter(cpf__icontains=q)
        return render(request, 'clientes/lista.html', {
            'clientes': clientes,
            'q': q,
            'pode_editar': request.user.is_admin,
        })


@method_decorator([login_required, admin_required], name='dispatch')
class ClienteCreateView(View):
    """RF01 — Cadastro de clientes. Restrito a ADMIN."""
    def get(self, request):
        return render(request, 'clientes/form.html', {'titulo': 'Novo Cliente', 'acao': 'cadastrar'})

    def post(self, request):
        try:
            _svc.cadastrar(
                nome=request.POST.get('nome', ''),
                cpf=request.POST.get('cpf', ''),
                email=request.POST.get('email', ''),
                telefone=request.POST.get('telefone', ''),
                endereco=request.POST.get('endereco', ''),
            )
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('cliente_lista')
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'clientes/form.html',
                          {'titulo': 'Novo Cliente', 'acao': 'cadastrar', 'dados': request.POST})


@method_decorator([login_required, admin_required], name='dispatch')
class ClienteEditView(View):
    """Edição de clientes. Restrito a ADMIN."""
    def get(self, request, pk):
        obj = get_object_or_404(Cliente, pk=pk)
        return render(request, 'clientes/form.html',
                      {'titulo': 'Editar Cliente', 'acao': 'editar', 'dados': obj})

    def post(self, request, pk):
        try:
            _svc.atualizar(pk, **{
                k: request.POST[k]
                for k in ['nome', 'cpf', 'email', 'telefone', 'endereco']
                if k in request.POST
            })
            messages.success(request, 'Cliente atualizado!')
            return redirect('cliente_lista')
        except ValueError as e:
            obj = get_object_or_404(Cliente, pk=pk)
            messages.error(request, str(e))
            return render(request, 'clientes/form.html',
                          {'titulo': 'Editar Cliente', 'acao': 'editar', 'dados': obj})


@method_decorator([login_required, admin_required], name='dispatch')
class ClienteDeleteView(View):
    """Exclusão de clientes. Restrito a ADMIN."""
    def post(self, request, pk):
        try:
            _svc.remover(pk)
            messages.success(request, 'Cliente removido.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('cliente_lista')
