from django.db import models


class Cliente(models.Model):
    nome      = models.CharField(max_length=100)
    cpf       = models.CharField(max_length=14, unique=True)
    email     = models.EmailField(max_length=100, blank=True)
    telefone  = models.CharField(max_length=20, blank=True)
    endereco  = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'clientes'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.cpf})"
