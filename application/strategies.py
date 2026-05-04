"""
CAMADA DE APLICAÇÃO - Strategy Pattern
========================================
Define a interface RelatorioStrategy e todas as implementações concretas.

O Strategy Pattern resolve um problema clássico: como oferecer diferentes
"sabores" de um comportamento (aqui, geração de relatório) sem encher o
código de if/elif? A resposta é encapsular cada variação em sua própria
classe, todas seguindo a mesma interface. Quem chama não precisa saber
qual estratégia está usando — só chama `gerar()`.

Referência: Gamma et al. Design Patterns, p. 315.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any


# ══════════════════════════════════════════════════════════════════════
# Interface comum (o "contrato" que todas as estratégias assinam)
# ══════════════════════════════════════════════════════════════════════
class RelatorioStrategy(ABC):
    """
    Interface que define o contrato de geração de relatório.
    Toda estratégia concreta DEVE implementar o método `gerar`.
    """

    @abstractmethod
    def gerar(self, **kwargs) -> Dict[str, Any]:
        """
        Gera e retorna os dados do relatório como um dicionário.
        O tipo exato dos kwargs depende de cada estratégia concreta.
        """
        raise NotImplementedError


# ══════════════════════════════════════════════════════════════════════
# Estratégia 1: Relatório por Cliente
# ══════════════════════════════════════════════════════════════════════
class RelatorioPorCliente(RelatorioStrategy):
    """
    Gera um relatório com todas as vendas de um cliente específico,
    calculando o total gasto e listando cada transação.
    """

    def gerar(self, **kwargs) -> Dict[str, Any]:
        """
        kwargs esperados:
          - cliente_id (int): identificador do cliente
        """
        from infrastructure.repositories import ClienteRepository, VendaRepository

        cliente_id = kwargs.get('cliente_id')
        if not cliente_id:
            raise ValueError("É necessário informar o cliente_id para este relatório.")

        cliente_repo = ClienteRepository()
        venda_repo = VendaRepository()

        cliente = cliente_repo.find_by_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente com id={cliente_id} não encontrado.")

        vendas = venda_repo.find_by_cliente(cliente_id)

        linhas = []
        total_geral = Decimal('0')
        for venda in vendas:
            total = venda.calcular_total()
            total_geral += total
            linhas.append({
                'id': venda.id,
                'data': venda.data.strftime('%d/%m/%Y %H:%M'),
                'itens': len(venda.itens),
                'total': float(total),
            })

        return {
            'tipo': 'por_cliente',
            'titulo': f'Relatório de Vendas — {cliente.nome}',
            'cliente': {'id': cliente.id, 'nome': cliente.nome, 'cpf': cliente.cpf},
            'vendas': linhas,
            'total_vendas': len(vendas),
            'total_geral': float(total_geral),
        }


# ══════════════════════════════════════════════════════════════════════
# Estratégia 2: Relatório por Período
# ══════════════════════════════════════════════════════════════════════
class RelatorioPorPeriodo(RelatorioStrategy):
    """
    Gera um relatório com todas as vendas dentro de um intervalo de datas,
    agrupando os dados por dia para facilitar análises temporais.
    """

    def gerar(self, **kwargs) -> Dict[str, Any]:
        """
        kwargs esperados:
          - data_inicio (str ou date): início do período (YYYY-MM-DD)
          - data_fim (str ou date): fim do período (YYYY-MM-DD)
        """
        from infrastructure.repositories import VendaRepository

        data_inicio = kwargs.get('data_inicio')
        data_fim = kwargs.get('data_fim')

        if not data_inicio or not data_fim:
            raise ValueError("É necessário informar data_inicio e data_fim.")

        # Aceita tanto string quanto objeto date/datetime
        if isinstance(data_inicio, str):
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        if isinstance(data_fim, str):
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()

        venda_repo = VendaRepository()
        vendas = venda_repo.find_by_periodo(data_inicio, data_fim)

        # Agrupamento por dia para o gráfico
        por_dia: Dict[str, float] = {}
        linhas = []
        total_geral = Decimal('0')

        for venda in vendas:
            total = venda.calcular_total()
            total_geral += total
            dia = venda.data.strftime('%d/%m/%Y')
            por_dia[dia] = por_dia.get(dia, 0.0) + float(total)
            linhas.append({
                'id': venda.id,
                'data': venda.data.strftime('%d/%m/%Y %H:%M'),
                'cliente': venda.cliente.nome,
                'itens': len(venda.itens),
                'total': float(total),
            })

        return {
            'tipo': 'por_periodo',
            'titulo': f'Relatório de Vendas: {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}',
            'periodo': {
                'inicio': data_inicio.strftime('%d/%m/%Y'),
                'fim': data_fim.strftime('%d/%m/%Y'),
            },
            'vendas': linhas,
            'por_dia': por_dia,        # usado para construir o gráfico
            'total_vendas': len(vendas),
            'total_geral': float(total_geral),
        }


# ══════════════════════════════════════════════════════════════════════
# Estratégia 3: Relatório por Produto
# ══════════════════════════════════════════════════════════════════════
class RelatorioPorProduto(RelatorioStrategy):
    """
    Gera um relatório de quanto cada produto foi vendido (quantidade e receita),
    útil para análise de mix de produtos.
    """

    def gerar(self, **kwargs) -> Dict[str, Any]:
        from infrastructure.repositories import VendaRepository, ProdutoRepository

        venda_repo = VendaRepository()
        produto_repo = ProdutoRepository()
        vendas = venda_repo.find_all()

        # Agrega por produto
        agregado: Dict[int, Dict] = {}
        for venda in vendas:
            for item in venda.itens:
                pid = item.produto.id
                if pid not in agregado:
                    agregado[pid] = {
                        'id': pid,
                        'nome': item.produto.nome,
                        'quantidade_total': 0,
                        'receita_total': 0.0,
                    }
                agregado[pid]['quantidade_total'] += item.quantidade
                agregado[pid]['receita_total'] += float(item.calcular_subtotal())

        produtos_lista = sorted(
            agregado.values(),
            key=lambda x: x['receita_total'],
            reverse=True
        )

        return {
            'tipo': 'por_produto',
            'titulo': 'Relatório de Vendas por Produto',
            'produtos': produtos_lista,
            'total_produtos': len(produtos_lista),
        }
