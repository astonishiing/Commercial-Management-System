from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ('username', 'perfil', 'is_active', 'is_staff')
    list_filter   = ('perfil', 'is_active')
    fieldsets     = (
        (None, {'fields': ('username', 'password')}),
        ('Perfil', {'fields': ('perfil',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'password1', 'password2', 'perfil')}),
    )
    search_fields = ('username',)
    ordering      = ('username',)
