"""
Decorators de controle de acesso por perfil para views web.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Redireciona FUNCIONARIO para o dashboard com mensagem de erro."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not getattr(request.user, 'is_admin', False):
            messages.error(request, 'Acesso restrito a administradores.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
