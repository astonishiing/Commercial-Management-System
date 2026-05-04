from django.urls import path
from .views_api import VendaListCreateAPIView, VendaDetailAPIView, VendaPorPeriodoAPIView

urlpatterns = [
    path('',          VendaListCreateAPIView.as_view(), name='api_vendas'),
    path('<int:pk>/', VendaDetailAPIView.as_view(),     name='api_venda_detail'),
    path('periodo/',  VendaPorPeriodoAPIView.as_view(), name='api_venda_periodo'),
]
