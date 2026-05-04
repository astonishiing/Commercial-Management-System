"""
Testes de Integração — API REST
=================================
Testam os endpoints da API com banco de dados real (SQLite em memória).
Verificam os fluxos de criação, leitura, atualização e exclusão,
além das regras de negócio nas rotas de venda.

Execute com:  python manage.py test tests.test_api
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.usuarios.models import Usuario
from apps.clientes.models import Cliente
from apps.produtos.models import Produto
from apps.vendas.models import Venda, ItemVenda


class BaseAPITest(TestCase):
    """Setup comum: cria usuários ADMIN e FUNCIONARIO e autentica o client."""

    def setUp(self):
        self.client = APIClient()

        # Usuário ADMIN
        self.admin = Usuario.objects.create_user(
            username='admin_test', password='senha123', perfil='ADMIN'
        )
        # Usuário FUNCIONARIO
        self.funcionario = Usuario.objects.create_user(
            username='func_test', password='senha123', perfil='FUNCIONARIO'
        )

        # Por padrão, testa como admin
        self.client.force_authenticate(user=self.admin)

    def _criar_cliente(self, nome='Cliente Teste', cpf='111.222.333-44'):
        return Cliente.objects.create(
            nome=nome, cpf=cpf,
            email='teste@email.com', telefone='(62) 99999-0000', endereco='Rua X'
        )

    def _criar_produto(self, nome='Produto Teste', preco='100.00', estoque=10):
        return Produto.objects.create(
            nome=nome, descricao='Descrição', preco=Decimal(preco),
            quantidade_estoque=estoque
        )


# ══════════════════════════════════════════════════════════════════════
# Testes de Clientes
# ══════════════════════════════════════════════════════════════════════
class ClienteAPITest(BaseAPITest):

    def test_listar_clientes(self):
        """GET /api/clientes/ deve retornar 200 e lista vazia inicialmente."""
        res = self.client.get('/api/clientes/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)

    def test_criar_cliente_admin(self):
        """POST /api/clientes/ como ADMIN deve criar o cliente."""
        dados = {
            'nome': 'João da Silva', 'cpf': '123.456.789-09',
            'email': 'joao@email.com', 'telefone': '(62) 9 9999-0000',
            'endereco': 'Rua A, 10'
        }
        res = self.client.post('/api/clientes/', dados, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Cliente.objects.filter(cpf='123.456.789-09').exists())

    def test_criar_cliente_cpf_duplicado(self):
        """POST com CPF já cadastrado deve retornar 400."""
        self._criar_cliente(cpf='000.000.000-00')
        res = self.client.post('/api/clientes/', {
            'nome': 'Outro', 'cpf': '000.000.000-00',
            'email': '', 'telefone': '', 'endereco': ''
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_atualizar_cliente(self):
        """PUT /api/clientes/{id}/ deve atualizar o nome do cliente."""
        c = self._criar_cliente()
        res = self.client.put(f'/api/clientes/{c.id}/', {'nome': 'Nome Atualizado'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        c.refresh_from_db()
        self.assertEqual(c.nome, 'Nome Atualizado')

    def test_excluir_cliente_sem_vendas(self):
        """DELETE deve remover cliente que não tem vendas."""
        c = self._criar_cliente()
        res = self.client.delete(f'/api/clientes/{c.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(Cliente.objects.filter(pk=c.id).exists())

    def test_excluir_cliente_com_vendas_bloqueado(self):
        """RN: Não deve permitir excluir cliente com vendas registradas."""
        c = self._criar_cliente()
        p = self._criar_produto()
        Venda.objects.create(cliente=c, usuario=self.admin, valor_total=Decimal('100'))
        res = self.client.delete(f'/api/clientes/{c.id}/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


# ══════════════════════════════════════════════════════════════════════
# Testes de Produtos
# ══════════════════════════════════════════════════════════════════════
class ProdutoAPITest(BaseAPITest):

    def test_listar_produtos(self):
        res = self.client.get('/api/produtos/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_criar_produto_admin(self):
        res = self.client.post('/api/produtos/', {
            'nome': 'Monitor 24"', 'descricao': 'Full HD',
            'preco': '899.90', 'quantidade_estoque': 5
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_criar_produto_preco_negativo(self):
        """Preço negativo deve ser rejeitado."""
        res = self.client.post('/api/produtos/', {
            'nome': 'Produto X', 'descricao': '',
            'preco': '-10.00', 'quantidade_estoque': 5
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_atualizar_produto(self):
        p = self._criar_produto()
        res = self.client.put(f'/api/produtos/{p.id}/', {
            'nome': 'Produto Atualizado', 'preco': '150.00', 'quantidade_estoque': 8
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


# ══════════════════════════════════════════════════════════════════════
# Testes de Vendas
# ══════════════════════════════════════════════════════════════════════
class VendaAPITest(BaseAPITest):

    def test_registrar_venda_valida(self):
        """POST /api/vendas/ deve registrar a venda e reduzir o estoque."""
        c = self._criar_cliente()
        p = self._criar_produto(estoque=10)

        res = self.client.post('/api/vendas/', {
            'cliente_id': c.id,
            'itens': [{'produto_id': p.id, 'quantidade': 3}]
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Verifica que o estoque foi reduzido (RN05)
        p.refresh_from_db()
        self.assertEqual(p.quantidade_estoque, 7)

    def test_registrar_venda_sem_itens(self):
        """RN02: Venda sem itens deve retornar 400."""
        c = self._criar_cliente()
        res = self.client.post('/api/vendas/', {
            'cliente_id': c.id, 'itens': []
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registrar_venda_estoque_insuficiente(self):
        """RN04: Venda com quantidade maior que o estoque deve retornar 400."""
        c = self._criar_cliente()
        p = self._criar_produto(estoque=2)

        res = self.client.post('/api/vendas/', {
            'cliente_id': c.id,
            'itens': [{'produto_id': p.id, 'quantidade': 10}]
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Estoque não deve ter sido alterado
        p.refresh_from_db()
        self.assertEqual(p.quantidade_estoque, 2)

    def test_registrar_venda_cliente_invalido(self):
        """Venda com cliente inexistente deve retornar 400."""
        p = self._criar_produto()
        res = self.client.post('/api/vendas/', {
            'cliente_id': 9999,
            'itens': [{'produto_id': p.id, 'quantidade': 1}]
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listar_vendas(self):
        res = self.client.get('/api/vendas/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detalhar_venda(self):
        c = self._criar_cliente()
        p = self._criar_produto()
        venda = Venda.objects.create(
            cliente=c, usuario=self.admin, valor_total=Decimal('100')
        )
        ItemVenda.objects.create(
            venda=venda, produto=p, quantidade=1,
            preco_unitario=Decimal('100'), subtotal=Decimal('100')
        )
        res = self.client.get(f'/api/vendas/{venda.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], venda.id)

    def test_calculo_total_venda(self):
        """RN06: O total retornado deve corresponder a quantidade × preço."""
        c = self._criar_cliente()
        p = self._criar_produto(preco='50.00', estoque=20)

        res = self.client.post('/api/vendas/', {
            'cliente_id': c.id,
            'itens': [{'produto_id': p.id, 'quantidade': 4}]
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertAlmostEqual(float(res.data['total']), 200.0)


# ══════════════════════════════════════════════════════════════════════
# Testes de Autenticação
# ══════════════════════════════════════════════════════════════════════
class AutenticacaoAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create_user(
            username='user_auth', password='senha456'
        )

    def test_login_valido(self):
        """POST /api/auth/login/ com credenciais válidas deve retornar tokens."""
        res = self.client.post('/api/auth/login/', {
            'username': 'user_auth', 'password': 'senha456'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_login_invalido(self):
        """Credenciais erradas devem retornar 401."""
        res = self.client.post('/api/auth/login/', {
            'username': 'user_auth', 'password': 'senhaerrada'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_acesso_sem_autenticacao(self):
        """Rotas protegidas sem token devem retornar 403."""
        res = self.client.get('/api/clientes/')
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
