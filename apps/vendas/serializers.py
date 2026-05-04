from rest_framework import serializers
from .models import Venda, ItemVenda


class ItemVendaSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)

    class Meta:
        model  = ItemVenda
        fields = ['id', 'produto', 'produto_nome', 'quantidade', 'preco_unitario', 'subtotal']


class VendaSerializer(serializers.ModelSerializer):
    itens         = ItemVendaSerializer(many=True, read_only=True)
    cliente_nome  = serializers.CharField(source='cliente.nome', read_only=True)
    usuario_nome  = serializers.CharField(source='usuario.username', read_only=True)
    data_formatada = serializers.DateTimeField(source='data', format='%d/%m/%Y %H:%M', read_only=True)

    class Meta:
        model  = Venda
        fields = ['id', 'data', 'data_formatada', 'cliente', 'cliente_nome',
                  'usuario', 'usuario_nome', 'valor_total', 'itens']


class ItemInputSerializer(serializers.Serializer):
    produto_id = serializers.IntegerField()
    quantidade = serializers.IntegerField(min_value=1)


class VendaCreateSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    itens      = ItemInputSerializer(many=True)
