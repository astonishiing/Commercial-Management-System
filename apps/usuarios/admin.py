from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ('username', 'email', 'perfil', 'is_active', 'is_staff')
    list_filter   = ('perfil', 'is_active')

    # Campos exibidos na tela de EDIÇÃO de um usuário existente
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('email',)}),
        ('Perfil', {'fields': ('perfil',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    # Campos exibidos na tela de CRIAÇÃO de um novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'perfil'),
        }),
    )

    search_fields = ('username', 'email')
    ordering      = ('username',)
