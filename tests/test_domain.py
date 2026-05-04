"""
Testes Unitários — Camada de Domínio
======================================
Testam as regras de negócio encapsuladas nas entidades puras.
Não precisam de banco de dados nem do Django — são Python puro.

Execute com:  python manage.py test tests.test_domain
"""

from decimal import Decimal
from datetime import datetime
from django.test import TestCase

from domain.models import ClienteDomain, ProdutoDomain, ItemVendaDomain, VendaDomain


class ClienteDomainTest(TestCase):
    """Testa as regras de validação da entidade Cliente."""

    def _cliente(self, **kwargs):
        defaults = dict(
            id=None, nome='João Silva', cpf='123.456.789-09',
            email='joao@email.com', telefone='(62) 99999-0000',
            endereco='Rua A, 1'
        )
        defaults.update(kwargs)
        return ClienteDomain(**defaults)

    def test_cliente_valido(self):
        erros = self._cliente().validar()
        self.assertEqual(erros, [])

    def test_nome_obrigatorio(self):
        erros = self._cliente(nome='').validar()
        self.assertTrue(any('Nome' in e for e in erros))

    def test_cpf_invalido_letras(self):
        erros = self._cliente(cpf='abc.def.ghi-jk').validar()
        self.assertTrue(any('CPF' in e for e in erros))

    def test_cpf_invalido_tamanho(self):
        erros = self._cliente(cpf='123.456.789').validar()
        self.assertTrue(any('CPF' in e for e in erros))

    def test_email_invalido(self):
        erros = self._cliente(email='nao-e-email').validar()
        self.assertTrue(any('mail' in e.lower() for e in erros))

    def test_email_vazio_permitido(self):
        """E-mail é opcional."""
        erros = self._cliente(email='').validar()
        self.assertEqual(erros, [])


class ProdutoDomainTest(TestCase):
    """Testa as regras de negócio da entidade Produto (estoque e preço)."""

    def _produto(self, **kwargs):
        defaults = dict(
            id=None, nome='Teclado Mecânico', descricao='Teclado RGB',
            preco_atual=Decimal('299.90'), quantidade_estoque=10
        )
        defaults.update(kwargs)
        return ProdutoDomain(**defaults)

    def test_produto_valido(self):
        self.assertEqual(self._produto().validar(), [])

    def test_preco_negativo_invalido(self):
        erros = self._produto(preco_atual=Decimal('-1')).validar()
        self.assertTrue(any('Preço' in e for e in erros))

    def test_estoque_suficiente(self):
        """RN04: tem_estoque_suficiente deve retornar True quando há estoque."""
        p = self._produto(quantidade_estoque=5)
        self.assertTrue(p.tem_estoque_suficiente(5))
        self.assertTrue(p.tem_estoque_suficiente(3))

    def test_estoque_insuficiente(self):
        """RN04: tem_estoque_suficiente deve retornar False quando não há estoque."""
        p = self._produto(quantidade_estoque=5)
        self.assertFalse(p.tem_estoque_suficiente(6))

    def test_reduzir_estoque(self):
        """RN05: reduzir_estoque deve diminuir a quantidade corretamente."""
        p = self._produto(quantidade_estoque=10)
        p.reduzir_estoque(4)
        self.assertEqual(p.quantidade_estoque, 6)

    def test_reduzir_estoque_insuficiente_lanca_erro(self):
        """RN05: reduzir_estoque deve lançar ValueError se não houver estoque."""
        p = self._produto(quantidade_estoque=2)
        with self.assertRaises(ValueError):
            p.reduzir_estoque(5)


class ItemVendaDomainTest(TestCase):
    """Testa o cálculo de subtotal e validação de quantidade."""

    def _produto(self):
        return ProdutoDomain(
            id=1, nome='Mouse', descricao='Mouse sem fio',
            preco_atual=Decimal('89.90'), quantidade_estoque=20
        )

    def test_calcular_subtotal(self):
        """RN06: subtotal = quantidade × preço unitário."""
        item = ItemVendaDomain(
            id=None, produto=self._produto(),
            quantidade=3, preco_unitario=Decimal('89.90')
        )
        self.assertEqual(item.calcular_subtotal(), Decimal('269.70'))

    def test_quantidade_zero_invalida(self):
        """RN03: quantidade deve ser maior que zero."""
        item = ItemVendaDomain(
            id=None, produto=self._produto(),
            quantidade=0, preco_unitario=Decimal('89.90')
        )
        erros = item.validar()
        self.assertTrue(any('quantidade' in e.lower() for e in erros))

    def test_quantidade_negativa_invalida(self):
        item = ItemVendaDomain(
            id=None, produto=self._produto(),
            quantidade=-1, preco_unitario=Decimal('89.90')
        )
        self.assertTrue(len(item.validar()) > 0)


class VendaDomainTest(TestCase):
    """Testa as regras de negócio da entidade Venda."""

    def _cliente(self):
        return ClienteDomain(
            id=1, nome='Maria', cpf='111.222.333-44',
            email='maria@email.com', telefone='', endereco=''
        )

    def _produto(self):
        return ProdutoDomain(
            id=1, nome='Notebook', descricao='',
            preco_atual=Decimal('3500.00'), quantidade_estoque=5
        )

    def _item(self, qtd=1):
        return ItemVendaDomain(
            id=None, produto=self._produto(),
            quantidade=qtd, preco_unitario=Decimal('3500.00')
        )

    def test_calcular_total(self):
        """RN06: total da venda = soma dos subtotais dos itens."""
        venda = VendaDomain(
            id=None, cliente=self._cliente(),
            usuario_id=1, data=datetime.now(),
            itens=[self._item(2), self._item(1)]
        )
        # 2 × 3500 + 1 × 3500 = 10500
        self.assertEqual(venda.calcular_total(), Decimal('10500.00'))

    def test_venda_sem_itens_invalida(self):
        """RN02: venda deve ter ao menos um item."""
        venda = VendaDomain(
            id=None, cliente=self._cliente(),
            usuario_id=1, data=datetime.now(), itens=[]
        )
        erros = venda.validar()
        self.assertTrue(any('item' in e.lower() for e in erros))

    def test_adicionar_item_valido(self):
        venda = VendaDomain(
            id=None, cliente=self._cliente(),
            usuario_id=1, data=datetime.now(), itens=[]
        )
        venda.adicionar_item(self._item(1))
        self.assertEqual(len(venda.itens), 1)

    def test_adicionar_item_invalido_lanca_erro(self):
        """Item com quantidade 0 não pode ser adicionado."""
        venda = VendaDomain(
            id=None, cliente=self._cliente(),
            usuario_id=1, data=datetime.now(), itens=[]
        )
        with self.assertRaises(ValueError):
            venda.adicionar_item(self._item(0))
