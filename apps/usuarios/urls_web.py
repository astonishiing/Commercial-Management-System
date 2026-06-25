# urls_web.py — Entrega 2: login/logout apenas
# Recuperação de senha via e-mail será implementada na Entrega 3
from django.urls import path
from .views_web import LoginWebView, LogoutWebView

urlpatterns = [
    path('login/',  LoginWebView.as_view(),  name='login'),
    path('logout/', LogoutWebView.as_view(), name='logout'),
]
