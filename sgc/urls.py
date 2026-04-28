"""
Roteamento principal do SGC.
Organiza as URLs por camada: API REST e Interface Web.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Interface Web (camada de apresentação) ──────────────────────────
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('auth/', include('apps.usuarios.urls_web')),
    path('dashboard/', include('apps.usuarios.urls_dashboard')),
    path('clientes/', include('apps.clientes.urls_web')),
    path('produtos/', include('apps.produtos.urls_web')),
    path('vendas/', include('apps.vendas.urls_web')),
    path('relatorios/', include('apps.relatorios.urls_web')),

    # ── API REST (JWT protegida) ────────────────────────────────────────
    path('api/', include([
        path('auth/', include('apps.usuarios.urls_api')),
        path('clientes/', include('apps.clientes.urls_api')),
        path('produtos/', include('apps.produtos.urls_api')),
        path('vendas/', include('apps.vendas.urls_api')),
        path('relatorios/', include('apps.relatorios.urls_api')),
    ])),
]
