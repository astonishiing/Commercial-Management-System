from django.urls import path
from .views_api import RelatorioPorClienteAPIView, RelatorioPorPeriodoAPIView, RelatorioPorProdutoAPIView

urlpatterns = [
    path('cliente/<int:cliente_id>/', RelatorioPorClienteAPIView.as_view(), name='api_rel_cliente'),
    path('periodo/',                  RelatorioPorPeriodoAPIView.as_view(), name='api_rel_periodo'),
    path('produto/',                  RelatorioPorProdutoAPIView.as_view(), name='api_rel_produto'),
]
