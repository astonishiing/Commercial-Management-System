"""
CAMADA DE APLICAÇÃO - Factory Pattern
========================================
A RelatorioFactory centraliza a criação das estratégias de relatório.

Por que Factory + Strategy juntos?
  - Strategy resolve "qual algoritmo usar em tempo de execução".
  - Factory resolve "quem é responsável por criar o objeto certo".
  Juntos, eles garantem que nenhuma parte do sistema precise escrever
  `if tipo == 'cliente': return RelatorioPorCliente()` espalhado pelo código.
  Essa lógica fica aqui, num único lugar.

Referência: Gamma et al. Design Patterns, p. 107 (Factory Method).
"""

from .strategies import (
    RelatorioStrategy,
    RelatorioPorCliente,
    RelatorioPorPeriodo,
    RelatorioPorProduto,
)

# Mapeamento de identificadores para classes — facilita extensão futura.
# Para adicionar um novo relatório, basta incluir mais uma entrada aqui.
_ESTRATEGIAS = {
    'cliente':  RelatorioPorCliente,
    'periodo':  RelatorioPorPeriodo,
    'produto':  RelatorioPorProduto,
}


class RelatorioFactory:
    """
    Fábrica responsável por instanciar a estratégia de relatório correta
    com base no tipo solicitado.

    O chamador só precisa dizer QUAL tipo quer — a Factory cuida
    de COMO criar o objeto correspondente.
    """

    @staticmethod
    def criar(tipo: str) -> RelatorioStrategy:
        """
        Recebe um identificador de tipo (string) e retorna a estratégia
        correspondente já instanciada.

        Args:
            tipo: 'cliente', 'periodo' ou 'produto'.

        Returns:
            Instância de RelatorioStrategy pronta para uso.

        Raises:
            ValueError: se o tipo não for reconhecido.
        """
        estrategia_cls = _ESTRATEGIAS.get(tipo)
        if not estrategia_cls:
            tipos_validos = ', '.join(_ESTRATEGIAS.keys())
            raise ValueError(
                f"Tipo de relatório '{tipo}' inválido. "
                f"Tipos disponíveis: {tipos_validos}."
            )
        return estrategia_cls()

    @staticmethod
    def tipos_disponiveis() -> list:
        """Retorna os identificadores de todos os tipos de relatório disponíveis."""
        return list(_ESTRATEGIAS.keys())
