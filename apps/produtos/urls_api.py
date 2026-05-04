from django.urls import path
from .views_api import ProdutoListCreateAPIView, ProdutoDetailAPIView

urlpatterns = [
    path('',          ProdutoListCreateAPIView.as_view(), name='api_produtos'),
    path('<int:pk>/', ProdutoDetailAPIView.as_view(),     name='api_produto_detail'),
]
