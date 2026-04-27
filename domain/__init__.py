# Camada de Domínio - Domain Model Pattern
# Entidades puras do negócio, sem dependência de frameworks externos.
from .models import ClienteDomain, ProdutoDomain, ItemVendaDomain, VendaDomain

__all__ = ['ClienteDomain', 'ProdutoDomain', 'ItemVendaDomain', 'VendaDomain']
