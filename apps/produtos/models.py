from django.db import models


class Produto(models.Model):
    nome               = models.CharField(max_length=100)
    descricao          = models.TextField(blank=True)
    preco              = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.IntegerField(default=0)

    class Meta:
        db_table = 'produtos'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} (R$ {self.preco})"
