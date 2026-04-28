# Repository Pattern - implementações concretas usando Django ORM
from .base import Repository
from .concrete import ClienteRepository, ProdutoRepository, VendaRepository

__all__ = ['Repository', 'ClienteRepository', 'ProdutoRepository', 'VendaRepository']
