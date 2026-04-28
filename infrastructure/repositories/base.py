"""
CAMADA DE INFRAESTRUTURA - Repository Pattern
==============================================
Define a interface genérica Repository<T> que todas as implementações
concretas devem respeitar. Isso garante que a camada de aplicação
nunca dependa diretamente do banco de dados — ela só conhece este contrato.

Referência: Fowler, M. Patterns of Enterprise Application Architecture, p. 322.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')


class Repository(ABC, Generic[T]):
    """
    Interface genérica de repositório.
    Declara as operações fundamentais de persistência para qualquer entidade.
    O uso de Generics (TypeVar) permite reutilizar esta interface para
    Cliente, Produto, Venda etc. sem repetir código.
    """

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persiste a entidade. Cria se não tiver id, atualiza se tiver."""
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Recupera uma entidade pelo identificador. Retorna None se não existir."""
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> List[T]:
        """Lista todas as entidades persistidas."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        """Remove o registro pelo identificador."""
        raise NotImplementedError
