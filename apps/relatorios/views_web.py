import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from application.services import RelatorioService
from apps.clientes.models import Cliente

_svc = RelatorioService()


@method_decorator(login_required, name='dispatch')
class RelatorioIndexView(View):
    def get(self, request):
        clientes = Cliente.objects.all().order_by('nome')
        return render(request, 'relatorios/index.html', {'clientes': clientes})


@method_decorator(login_required, name='dispatch')
class RelatorioPorClienteView(View):
    def get(self, request):
        cliente_id = request.GET.get('cliente_id')
        clientes   = Cliente.objects.all().order_by('nome')
        dados      = None
        if cliente_id:
            try:
                dados = _svc.gerar('cliente', cliente_id=int(cliente_id))
            except ValueError as e:
                dados = {'erro': str(e)}
        return render(request, 'relatorios/por_cliente.html', {
            'clientes': clientes,
            'cliente_id': cliente_id,
            'dados': dados,
        })


@method_decorator(login_required, name='dispatch')
class RelatorioPorPeriodoView(View):
    def get(self, request):
        data_inicio = request.GET.get('inicio', '')
        data_fim    = request.GET.get('fim', '')
        dados       = None
        grafico_labels = '[]'
        grafico_values = '[]'

        if data_inicio and data_fim:
            try:
                dados = _svc.gerar('periodo', data_inicio=data_inicio, data_fim=data_fim)
                # Prepara dados para o gráfico Chart.js
                por_dia = dados.get('por_dia', {})
                grafico_labels = json.dumps(list(por_dia.keys()))
                grafico_values = json.dumps(list(por_dia.values()))
            except ValueError as e:
                dados = {'erro': str(e)}

        return render(request, 'relatorios/por_periodo.html', {
            'dados': dados,
            'data_inicio': data_inicio,
            'data_fim':    data_fim,
            'grafico_labels': grafico_labels,
            'grafico_values': grafico_values,
        })


@method_decorator(login_required, name='dispatch')
class RelatorioPorProdutoView(View):
    def get(self, request):
        dados = _svc.gerar('produto')
        # Prepara dados para o gráfico de barras
        nomes   = json.dumps([p['nome']          for p in dados['produtos'][:10]])
        receitas = json.dumps([p['receita_total'] for p in dados['produtos'][:10]])
        return render(request, 'relatorios/por_produto.html', {
            'dados': dados,
            'grafico_nomes':   nomes,
            'grafico_receitas': receitas,
        })
