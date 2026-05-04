from django.db import models
from apps.clientes.models import Cliente
from apps.produtos.models import Produto
from apps.usuarios.models import Usuario


class Venda(models.Model):
    data        = models.DateTimeField(auto_now_add=True)
    cliente     = models.ForeignKey(Cliente,  on_delete=models.PROTECT, related_name='vendas')
    usuario     = models.ForeignKey(Usuario,  on_delete=models.PROTECT, related_name='vendas')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'vendas'
        ordering = ['-data']

    def __str__(self):
        return f"Venda #{self.id} — {self.cliente.nome} ({self.data:%d/%m/%Y})"


class ItemVenda(models.Model):
    venda          = models.ForeignKey(Venda,   on_delete=models.CASCADE, related_name='itens')
    produto        = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='itens_venda')
    quantidade     = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal       = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'itens_venda'

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} @ R${self.preco_unitario}"
