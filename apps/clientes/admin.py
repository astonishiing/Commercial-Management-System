from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'cpf', 'email', 'telefone')
    search_fields = ('nome', 'cpf', 'email')
    ordering      = ('nome',)
