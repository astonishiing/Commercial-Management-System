"""
CAMADA DE DOMÍNIO - Domain Model Pattern
=========================================
As entidades aqui são classes Python puras que encapsulam os dados
e as REGRAS DE NEGÓCIO do sistema. Esta camada NÃO conhece Django,
banco de dados nem HTTP — ela representa apenas o domínio do problema.

Referência: Fowler, M. Patterns of Enterprise Application Architecture.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


# ══════════════════════════════════════════════════════════════════════
# ENTIDADE: Cliente
# ══════════════════════════════════════════════════════════════════════
@dataclass
class ClienteDomain:
    """
    Representa o consumidor responsável por realizar compras no sistema.
    Armazena dados de identificação e contato.
    """
    id: Optional[int]
    nome: str
    cpf: str
    email: str
    telefone: str
    endereco: str

    def validar(self) -> List[str]:
        """Retorna lista de erros de validação. Lista vazia = válido."""
        erros = []
        if not self.nome or not self.nome.strip():
            erros.append("Nome do cliente é obrigatório.")
        cpf_limpo = self.cpf.replace('.', '').replace('-', '')
        if not cpf_limpo.isdigit() or len(cpf_limpo) != 11:
            erros.append("CPF inválido. Use o formato 000.000.000-00.")
        if self.email and '@' not in self.email:
            erros.append("E-mail inválido.")
        return erros


# ══════════════════════════════════════════════════════════════════════
# ENTIDADE: Produto
# ══════════════════════════════════════════════════════════════════════
@dataclass
class ProdutoDomain:
    """
    Representa um item disponível para comercialização.
    Controla preço e quantidade em estoque.
    """
    id: Optional[int]
    nome: str
    descricao: str
    preco_atual: Decimal
    quantidade_estoque: int

    def tem_estoque_suficiente(self, quantidade_solicitada: int) -> bool:
        """RN04: Verifica se há estoque disponível para a quantidade pedida."""
        return self.quantidade_estoque >= quantidade_solicitada

    def reduzir_estoque(self, quantidade: int) -> None:
        """RN05: Reduz o estoque após uma venda. Lança erro se insuficiente."""
        if not self.tem_estoque_suficiente(quantidade):
            raise ValueError(
                f"Estoque insuficiente para '{self.nome}'. "
                f"Disponível: {self.quantidade_estoque}, solicitado: {quantidade}."
            )
        self.quantidade_estoque -= quantidade

    def validar(self) -> List[str]:
        erros = []
        if not self.nome or not self.nome.strip():
            erros.append("Nome do produto é obrigatório.")
        if self.preco_atual < Decimal('0'):
            erros.append("Preço não pode ser negativo.")
        if self.quantidade_estoque < 0:
            erros.append("Quantidade em estoque não pode ser negativa.")
        return erros


# ══════════════════════════════════════════════════════════════════════
# ENTIDADE: ItemVenda
# ══════════════════════════════════════════════════════════════════════
@dataclass
class ItemVendaDomain:
    """
    Representa um produto específico incluído em uma venda.
    A relação entre Venda e Produto é uma COMPOSIÇÃO: o item
    não existe independentemente de sua venda.
    """
    id: Optional[int]
    produto: ProdutoDomain
    quantidade: int
    preco_unitario: Decimal

    def calcular_subtotal(self) -> Decimal:
        """RN06: Calcula o valor parcial deste item (quantidade × preço unitário)."""
        return Decimal(str(self.quantidade)) * self.preco_unitario

    def validar(self) -> List[str]:
        """RN03: A quantidade deve ser maior que zero."""
        erros = []
        if self.quantidade <= 0:
            erros.append("A quantidade do item deve ser maior que zero.")
        if self.preco_unitario < Decimal('0'):
            erros.append("Preço unitário não pode ser negativo.")
        return erros


# ══════════════════════════════════════════════════════════════════════
# ENTIDADE: Venda  (raiz do agregado)
# ══════════════════════════════════════════════════════════════════════
@dataclass
class VendaDomain:
    """
    Representa uma transação comercial realizada por um cliente.
    É a raiz do agregado Venda + ItemVenda: todos os itens
    pertencem exclusivamente a esta venda.

    Regras de negócio encapsuladas aqui:
      - RN01: deve ter um cliente associado
      - RN02: deve ter ao menos um item
      - RN06: valor total calculado a partir dos subtotais
    """
    id: Optional[int]
    cliente: ClienteDomain
    usuario_id: int
    data: datetime
    itens: List[ItemVendaDomain] = field(default_factory=list)

    def calcular_total(self) -> Decimal:
        """RN06: Soma os subtotais de todos os itens da venda."""
        return sum(item.calcular_subtotal() for item in self.itens)

    def adicionar_item(self, item: ItemVendaDomain) -> None:
        """Adiciona um item à venda, validando-o antes."""
        erros = item.validar()
        if erros:
            raise ValueError('; '.join(erros))
        self.itens.append(item)

    def validar(self) -> List[str]:
        erros = []
        if not self.cliente:
            erros.append("A venda deve estar associada a um cliente.")
        if not self.itens:  # RN02
            erros.append("A venda deve possuir ao menos um item.")
        for item in self.itens:
            erros.extend(item.validar())
        return erros
