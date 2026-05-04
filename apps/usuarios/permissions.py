"""
Permissões customizadas de controle de acesso por perfil.
Usadas nas views da API REST para restringir ações a ADMIN.

Conforme requisito de segurança:
  - FUNCIONARIO: pode visualizar e registrar vendas
  - ADMIN: acesso total (criar/editar/excluir clientes, produtos, usuários)
"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Permite acesso apenas a usuários com perfil ADMIN."""
    message = 'Apenas administradores podem realizar esta ação.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'perfil', None) == 'ADMIN'
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Leitura (GET, HEAD, OPTIONS) permitida para qualquer autenticado.
    Escrita (POST, PUT, DELETE) restrita a ADMIN.
    """
    message = 'Apenas administradores podem modificar este recurso.'

    SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in self.SAFE_METHODS:
            return True
        return getattr(request.user, 'perfil', None) == 'ADMIN'
