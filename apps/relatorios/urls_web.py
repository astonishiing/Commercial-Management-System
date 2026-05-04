from django.urls import path
from .views_web import RelatorioIndexView, RelatorioPorClienteView, RelatorioPorPeriodoView, RelatorioPorProdutoView

urlpatterns = [
    path('',         RelatorioIndexView.as_view(),      name='relatorio_index'),
    path('cliente/', RelatorioPorClienteView.as_view(), name='relatorio_cliente'),
    path('periodo/', RelatorioPorPeriodoView.as_view(), name='relatorio_periodo'),
    path('produto/', RelatorioPorProdutoView.as_view(), name='relatorio_produto'),
]
