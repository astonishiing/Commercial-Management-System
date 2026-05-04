# Camada de Aplicação - Services, Factories e Strategies
from .services import ClienteService, ProdutoService, VendaService, RelatorioService
from .factories import RelatorioFactory
from .strategies import RelatorioStrategy, RelatorioPorCliente, RelatorioPorPeriodo, RelatorioPorProduto

__all__ = [
    'ClienteService', 'ProdutoService', 'VendaService', 'RelatorioService',
    'RelatorioFactory',
    'RelatorioStrategy', 'RelatorioPorCliente', 'RelatorioPorPeriodo', 'RelatorioPorProduto',
]
