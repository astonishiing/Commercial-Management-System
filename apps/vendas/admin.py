from django.contrib import admin
from .models import Venda, ItemVenda

class ItemVendaInline(admin.TabularInline):
    model  = ItemVenda
    extra  = 0
    fields = ('produto', 'quantidade', 'preco_unitario', 'subtotal')
    readonly_fields = ('subtotal',)

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display  = ('id', 'cliente', 'usuario', 'data', 'valor_total')
    list_filter   = ('data', 'usuario')
    search_fields = ('cliente__nome',)
    inlines       = [ItemVendaInline]
    readonly_fields = ('valor_total', 'data')
