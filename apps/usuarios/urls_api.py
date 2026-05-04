# urls_api.py — rotas da API REST de autenticação
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views_api import LoginView, RegistroView, MeuPerfilView

urlpatterns = [
    path('login/',    LoginView.as_view(),    name='api_login'),
    path('refresh/',  TokenRefreshView.as_view(), name='api_token_refresh'),
    path('register/', RegistroView.as_view(), name='api_register'),
    path('me/',       MeuPerfilView.as_view(), name='api_me'),
]
