from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'preco', 'quantidade_estoque')
    search_fields = ('nome',)
    ordering      = ('nome',)
    list_filter   = ('quantidade_estoque',)
