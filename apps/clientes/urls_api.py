# urls_api.py
from django.urls import path
from .views_api import ClienteListCreateAPIView, ClienteDetailAPIView

urlpatterns = [
    path('',      ClienteListCreateAPIView.as_view(), name='api_clientes'),
    path('<int:pk>/', ClienteDetailAPIView.as_view(), name='api_cliente_detail'),
]
