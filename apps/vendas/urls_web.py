from django.urls import path
from .views_web import VendaListView, VendaDetailView, VendaCreateView

urlpatterns = [
    path('',          VendaListView.as_view(),   name='venda_lista'),
    path('nova/',     VendaCreateView.as_view(), name='venda_nova'),
    path('<int:pk>/', VendaDetailView.as_view(), name='venda_detalhe'),
]
