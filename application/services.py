"""
CAMADA DE APLICAÇÃO - Services
================================
Os services orquestram os casos de uso do sistema. Eles conhecem:
  - o domínio (entidades e suas regras de negócio),
  - os repositórios (como persistir/recuperar dados),
  - as factories e strategies (como gerar relatórios).

O que eles NÃO fazem: não sabem nada sobre HTTP, templates Django,
nem detalhes de banco de dados. Isso garante que a lógica de negócio
possa ser testada de forma independente.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any

from domain.models import ClienteDomain, ProdutoDomain, ItemVendaDomain, VendaDomain
from infrastructure.repositories import ClienteRepository, ProdutoRepository, VendaRepository
from .factories import RelatorioFactory


# ══════════════════════════════════════════════════════════════════════
# ClienteService
# ══════════════════════════════════════════════════════════════════════
class ClienteService:

    def __init__(self):
        self._repo = ClienteRepository()

    def cadastrar(self, nome: str, cpf: str, email: str,
                  telefone: str, endereco: str) -> ClienteDomain:
        """RF01: Cadastra um novo cliente após validar seus dados."""
        cliente = ClienteDomain(
            id=None, nome=nome, cpf=cpf,
            email=email, telefone=telefone, endereco=endereco
        )
        erros = cliente.validar()
        if erros:
            raise ValueError('; '.join(erros))
        # Garante unicidade do CPF
        if self._repo.find_by_cpf(cpf):
            raise ValueError("Já existe um cliente cadastrado com este CPF.")
        return self._repo.save(cliente)

    def atualizar(self, cliente_id: int, **dados) -> ClienteDomain:
        """RF02 (parte de atualização): Atualiza os dados de um cliente."""
        cliente = self._repo.find_by_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")
        for campo, valor in dados.items():
            setattr(cliente, campo, valor)
        erros = cliente.validar()
        if erros:
            raise ValueError('; '.join(erros))
        return self._repo.save(cliente)

    def buscar(self, cliente_id: int) -> Optional[ClienteDomain]:
        """RF02: Consulta um cliente pelo id."""
        return self._repo.find_by_id(cliente_id)

    def listar(self) -> List[ClienteDomain]:
        """RF02: Lista todos os clientes cadastrados."""
        return self._repo.find_all()

    def remover(self, cliente_id: int) -> None:
        """Remove um cliente, mas impede a remoção se ele tiver vendas registradas."""
        if self._repo.has_vendas(cliente_id):
            raise ValueError(
                "Este cliente possui vendas registradas e não pode ser removido."
            )
        self._repo.delete(cliente_id)


# ══════════════════════════════════════════════════════════════════════
# ProdutoService
# ══════════════════════════════════════════════════════════════════════
class ProdutoService:

    def __init__(self):
        self._repo = ProdutoRepository()

    def cadastrar(self, nome: str, descricao: str,
                  preco: Decimal, quantidade_estoque: int) -> ProdutoDomain:
        """RF03: Cadastra um novo produto."""
        produto = ProdutoDomain(
            id=None, nome=nome, descricao=descricao,
            preco_atual=Decimal(str(preco)),
            quantidade_estoque=quantidade_estoque
        )
        erros = produto.validar()
        if erros:
            raise ValueError('; '.join(erros))
        return self._repo.save(produto)

    def atualizar(self, produto_id: int, **dados) -> ProdutoDomain:
        """RF04: Atualiza as informações de um produto cadastrado."""
        produto = self._repo.find_by_id(produto_id)
        if not produto:
            raise ValueError(f"Produto {produto_id} não encontrado.")
        if 'preco' in dados:
            dados['preco_atual'] = Decimal(str(dados.pop('preco')))
        for campo, valor in dados.items():
            setattr(produto, campo, valor)
        erros = produto.validar()
        if erros:
            raise ValueError('; '.join(erros))
        return self._repo.save(produto)

    def buscar(self, produto_id: int) -> Optional[ProdutoDomain]:
        """RF05: Consulta um produto pelo id."""
        return self._repo.find_by_id(produto_id)

    def listar(self) -> List[ProdutoDomain]:
        """RF05: Lista todos os produtos cadastrados."""
        return self._repo.find_all()

    def remover(self, produto_id: int) -> None:
        self._repo.delete(produto_id)


# ══════════════════════════════════════════════════════════════════════
# VendaService
# ══════════════════════════════════════════════════════════════════════
class VendaService:
    """
    Orquestra o caso de uso mais complexo do sistema: o registro de uma venda.
    Este service coordena: validação do domínio → verificação de estoque →
    persistência da venda → atualização do estoque dos produtos.
    """

    def __init__(self):
        self._venda_repo = VendaRepository()
        self._cliente_repo = ClienteRepository()
        self._produto_repo = ProdutoRepository()

    def registrar(self, cliente_id: int, usuario_id: int,
                  itens_data: List[Dict]) -> VendaDomain:
        """
        RF06, RF07, RF08, RF09: Registra uma nova venda completa.

        itens_data: lista de dicts com {'produto_id': int, 'quantidade': int}
        """
        # 1. Valida e carrega o cliente (RN01)
        cliente = self._cliente_repo.find_by_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente não encontrado.")

        # 2. Constrói a entidade de domínio Venda
        venda = VendaDomain(
            id=None,
            cliente=cliente,
            usuario_id=usuario_id,
            data=datetime.now(),
            itens=[]
        )

        # 3. Valida cada item e verifica estoque (RN02, RN03, RN04)
        if not itens_data:
            raise ValueError("A venda deve conter ao menos um item.")

        produtos_para_atualizar = []
        for item_data in itens_data:
            produto = self._produto_repo.find_by_id(item_data['produto_id'])
            if not produto:
                raise ValueError(f"Produto id={item_data['produto_id']} não encontrado.")

            quantidade = int(item_data['quantidade'])

            # RN04: verifica disponibilidade de estoque no domínio
            if not produto.tem_estoque_suficiente(quantidade):
                raise ValueError(
                    f"Estoque insuficiente para '{produto.nome}'. "
                    f"Disponível: {produto.quantidade_estoque}."
                )

            item = ItemVendaDomain(
                id=None,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=produto.preco_atual
            )
            venda.adicionar_item(item)  # valida o item pelo domínio
            produtos_para_atualizar.append((produto, quantidade))

        # 4. Valida a venda completa pelas regras de domínio
        erros = venda.validar()
        if erros:
            raise ValueError('; '.join(erros))

        # 5. Persiste a venda
        venda_salva = self._venda_repo.save(venda)

        # 6. RN05: Atualiza o estoque de cada produto envolvido
        for produto, quantidade in produtos_para_atualizar:
            produto.reduzir_estoque(quantidade)
            self._produto_repo.save(produto)

        return venda_salva

    def buscar(self, venda_id: int) -> Optional[VendaDomain]:
        return self._venda_repo.find_by_id(venda_id)

    def listar(self) -> List[VendaDomain]:
        return self._venda_repo.find_all()


# ══════════════════════════════════════════════════════════════════════
# RelatorioService
# ══════════════════════════════════════════════════════════════════════
class RelatorioService:
    """
    Demonstra o uso combinado de Factory + Strategy.
    O service pede à Factory a estratégia correta e depois delega
    a geração do relatório para ela — sem nenhum if/elif aqui.
    """

    def gerar(self, tipo: str, **kwargs) -> Dict[str, Any]:
        """RF10, RF11, RF12: Gera um relatório usando a estratégia adequada."""
        # Factory cria a estratégia correta com base no tipo
        estrategia = RelatorioFactory.criar(tipo)
        # Strategy executa a lógica de geração
        return estrategia.gerar(**kwargs)

    def tipos_disponiveis(self) -> list:
        return RelatorioFactory.tipos_disponiveis()
