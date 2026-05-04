"""
Views Web da autenticação e dashboard.
"""
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View


class LoginWebView(View):
    template_name = 'auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        messages.error(request, 'Usuário ou senha inválidos.')
        return render(request, self.template_name, {'username': username})


class LogoutWebView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class DashboardView(View):
    template_name = 'base/dashboard.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')

        from apps.clientes.models import Cliente
        from apps.produtos.models import Produto
        from apps.vendas.models import Venda
        from django.db.models import Sum, FloatField
        from django.db.models.functions import TruncMonth
        from decimal import Decimal
        from datetime import date

        total_clientes = Cliente.objects.count()
        total_produtos = Produto.objects.count()
        total_vendas   = Venda.objects.count()
        receita_total  = Venda.objects.aggregate(t=Sum('valor_total'))['t'] or Decimal('0')

        # Últimas 5 vendas
        ultimas_vendas = Venda.objects.select_related('cliente').order_by('-data')[:5]

        # ── Gráfico anual: receita agrupada por mês (ano corrente) ──────────
        ano_atual = date.today().year
        vendas_mensais = (
            Venda.objects
            .filter(data__year=ano_atual)
            .annotate(mes=TruncMonth('data'))
            .values('mes')
            .annotate(total=Sum('valor_total'))
            .order_by('mes')
        )

        # Preenche todos os 12 meses (mesmo os sem vendas ficam zerados)
        meses_nomes = ['Jan','Fev','Mar','Abr','Mai','Jun',
                       'Jul','Ago','Set','Out','Nov','Dez']
        receitas_por_mes = {i: 0.0 for i in range(1, 13)}
        for v in vendas_mensais:
            receitas_por_mes[v['mes'].month] = float(v['total'] or 0)

        grafico_labels  = json.dumps(meses_nomes)
        grafico_valores = json.dumps([receitas_por_mes[m] for m in range(1, 13)])

        # Produtos com estoque crítico (≤ 5 unidades)
        estoque_critico = Produto.objects.filter(quantidade_estoque__lte=5).order_by('quantidade_estoque')[:5]

        context = {
            'total_clientes':  total_clientes,
            'total_produtos':  total_produtos,
            'total_vendas':    total_vendas,
            'receita_total':   receita_total,
            'ultimas_vendas':  ultimas_vendas,
            'grafico_labels':  grafico_labels,
            'grafico_valores': grafico_valores,
            'ano_atual':       ano_atual,
            'estoque_critico': estoque_critico,
        }
        return render(request, self.template_name, context)
