"""
CAMADA DE INFRAESTRUTURA - Repositórios Concretos
==================================================
Cada classe aqui implementa a interface Repository<T> usando o ORM do Django.
A camada de aplicação (services) só conhece a interface — se precisarmos
trocar o banco de dados ou o ORM, apenas este arquivo muda.

Esta separação é o coração do Repository Pattern:
  domínio/aplicação <──── interface ────> implementação (aqui)
"""

from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from .base import Repository
from domain.models import (
    ClienteDomain, ProdutoDomain, ItemVendaDomain, VendaDomain
)


# ══════════════════════════════════════════════════════════════════════
# Helpers de mapeamento (ORM → Domain)
# Convertem os modelos do Django nas entidades puras do domínio.
# ══════════════════════════════════════════════════════════════════════

def _orm_to_cliente(obj) -> ClienteDomain:
    return ClienteDomain(
        id=obj.id, nome=obj.nome, cpf=obj.cpf,
        email=obj.email, telefone=obj.telefone, endereco=obj.endereco
    )

def _orm_to_produto(obj) -> ProdutoDomain:
    return ProdutoDomain(
        id=obj.id, nome=obj.nome, descricao=obj.descricao,
        preco_atual=Decimal(str(obj.preco)),
        quantidade_estoque=obj.quantidade_estoque
    )

def _orm_to_item(obj) -> ItemVendaDomain:
    return ItemVendaDomain(
        id=obj.id,
        produto=_orm_to_produto(obj.produto),
        quantidade=obj.quantidade,
        preco_unitario=Decimal(str(obj.preco_unitario))
    )

def _orm_to_venda(obj) -> VendaDomain:
    return VendaDomain(
        id=obj.id,
        cliente=_orm_to_cliente(obj.cliente),
        usuario_id=obj.usuario_id,
        data=obj.data,
        itens=[_orm_to_item(i) for i in obj.itens.select_related('produto').all()]
    )


# ══════════════════════════════════════════════════════════════════════
# ClienteRepository
# ══════════════════════════════════════════════════════════════════════
class ClienteRepository(Repository[ClienteDomain]):
    """Gerencia a persistência da entidade Cliente."""

    def __init__(self):
        # Importação tardia para evitar circular imports entre camadas
        from apps.clientes.models import Cliente as ClienteORM
        self._model = ClienteORM

    def save(self, entity: ClienteDomain) -> ClienteDomain:
        if entity.id:
            obj = self._model.objects.get(pk=entity.id)
            obj.nome = entity.nome
            obj.cpf = entity.cpf
            obj.email = entity.email
            obj.telefone = entity.telefone
            obj.endereco = entity.endereco
            obj.save()
        else:
            obj = self._model.objects.create(
                nome=entity.nome, cpf=entity.cpf,
                email=entity.email, telefone=entity.telefone,
                endereco=entity.endereco
            )
        return _orm_to_cliente(obj)

    def find_by_id(self, entity_id: int) -> Optional[ClienteDomain]:
        try:
            return _orm_to_cliente(self._model.objects.get(pk=entity_id))
        except self._model.DoesNotExist:
            return None

    def find_all(self) -> List[ClienteDomain]:
        return [_orm_to_cliente(obj) for obj in self._model.objects.all()]

    def delete(self, entity_id: int) -> None:
        self._model.objects.filter(pk=entity_id).delete()

    def find_by_cpf(self, cpf: str) -> Optional[ClienteDomain]:
        try:
            return _orm_to_cliente(self._model.objects.get(cpf=cpf))
        except self._model.DoesNotExist:
            return None

    def has_vendas(self, cliente_id: int) -> bool:
        """RN: Cliente não pode ser removido se possuir vendas."""
        from apps.vendas.models import Venda as VendaORM
        return VendaORM.objects.filter(cliente_id=cliente_id).exists()


# ══════════════════════════════════════════════════════════════════════
# ProdutoRepository
# ══════════════════════════════════════════════════════════════════════
class ProdutoRepository(Repository[ProdutoDomain]):
    """Gerencia a persistência da entidade Produto, incluindo controle de estoque."""

    def __init__(self):
        from apps.produtos.models import Produto as ProdutoORM
        self._model = ProdutoORM

    def save(self, entity: ProdutoDomain) -> ProdutoDomain:
        if entity.id:
            obj = self._model.objects.get(pk=entity.id)
            obj.nome = entity.nome
            obj.descricao = entity.descricao
            obj.preco = entity.preco_atual
            obj.quantidade_estoque = entity.quantidade_estoque
            obj.save()
        else:
            obj = self._model.objects.create(
                nome=entity.nome, descricao=entity.descricao,
                preco=entity.preco_atual,
                quantidade_estoque=entity.quantidade_estoque
            )
        return _orm_to_produto(obj)

    def find_by_id(self, entity_id: int) -> Optional[ProdutoDomain]:
        try:
            return _orm_to_produto(self._model.objects.get(pk=entity_id))
        except self._model.DoesNotExist:
            return None

    def find_all(self) -> List[ProdutoDomain]:
        return [_orm_to_produto(obj) for obj in self._model.objects.all()]

    def delete(self, entity_id: int) -> None:
        self._model.objects.filter(pk=entity_id).delete()


# ══════════════════════════════════════════════════════════════════════
# VendaRepository
# ══════════════════════════════════════════════════════════════════════
class VendaRepository(Repository[VendaDomain]):
    """
    Gerencia a persistência do agregado Venda + ItemVenda.
    A criação de uma venda é atômica — todos os itens são salvos
    juntos, e o estoque é atualizado na mesma operação (via service).
    """

    def __init__(self):
        from apps.vendas.models import Venda as VendaORM, ItemVenda as ItemVendaORM
        self._model = VendaORM
        self._item_model = ItemVendaORM

    def save(self, entity: VendaDomain) -> VendaDomain:
        from apps.clientes.models import Cliente as ClienteORM
        from apps.usuarios.models import Usuario

        cliente_orm = ClienteORM.objects.get(pk=entity.cliente.id)
        usuario_orm = Usuario.objects.get(pk=entity.usuario_id)

        obj = self._model.objects.create(
            cliente=cliente_orm,
            usuario=usuario_orm,
            data=entity.data,
            valor_total=entity.calcular_total()
        )
        # Persiste cada item do agregado
        for item in entity.itens:
            from apps.produtos.models import Produto as ProdutoORM
            produto_orm = ProdutoORM.objects.get(pk=item.produto.id)
            self._item_model.objects.create(
                venda=obj,
                produto=produto_orm,
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario,
                subtotal=item.calcular_subtotal()
            )
        return _orm_to_venda(obj)

    def find_by_id(self, entity_id: int) -> Optional[VendaDomain]:
        try:
            return _orm_to_venda(
                self._model.objects.select_related('cliente', 'usuario').get(pk=entity_id)
            )
        except self._model.DoesNotExist:
            return None

    def find_all(self) -> List[VendaDomain]:
        return [
            _orm_to_venda(obj)
            for obj in self._model.objects.select_related('cliente', 'usuario').all()
        ]

    def delete(self, entity_id: int) -> None:
        self._model.objects.filter(pk=entity_id).delete()

    def find_by_cliente(self, cliente_id: int) -> List[VendaDomain]:
        qs = self._model.objects.filter(cliente_id=cliente_id).select_related('cliente', 'usuario')
        return [_orm_to_venda(obj) for obj in qs]

    def find_by_periodo(self, data_inicio: datetime, data_fim: datetime) -> List[VendaDomain]:
        qs = self._model.objects.filter(
            data__date__gte=data_inicio,
            data__date__lte=data_fim
        ).select_related('cliente', 'usuario')
        return [_orm_to_venda(obj) for obj in qs]
