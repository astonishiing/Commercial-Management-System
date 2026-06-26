# SGC — Sistema de Gestão Comercial
### Entrega 2 — Backend + API REST + Interface Web

<img width="1517" height="775" alt="image" src="https://github.com/user-attachments/assets/fbec03af-3de6-4cd3-9cb7-70884746a02e" />


> Wagner Samuel Cardoso · Eduardo Manzur · Gabriel Becker · Guilherme Rocha de Barros
> Repositório: https://github.com/astonishiing/Commercial-Management-System.git

---

## O que está implementado nesta entrega

| Critério | Status |
|---|---|
| Registro de vendas com atualização de estoque | ✅ |
| CRUD completo de Clientes | ✅ |
| CRUD completo de Produtos | ✅ |
| Relatórios de vendas (cliente, período, produto) | ✅ |
| Banco de dados integrado (SQLite) | ✅ |
| API REST com endpoints JSON | ✅ |
| Interface web Django (login, dashboard, listagens) | ✅ |
| Controle de perfil ADMIN / FUNCIONARIO | ✅ |
| Testes básicos (unitários + integração) | ✅ |
| README atualizado | ✅ |

> **Entrega 3** adicionará: JWT obrigatório em todas as rotas, recuperação de senha por e-mail e documentação final.

<img width="1518" height="768" alt="image" src="https://github.com/user-attachments/assets/3e43b770-cb0e-44c5-b0b4-62de2799b4ef" />

---

## Como executar

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Aplicar migrações (cria o db.sqlite3)
python manage.py migrate

# 4. Criar superusuário administrador
python manage.py createsuperuser

# 5. Iniciar o servidor
python manage.py runserver
```

Acesse: **http://127.0.0.1:8000**

---

## Rodar os testes

```bash
# Todos os testes
python manage.py test tests

# Apenas testes de domínio (sem banco)
python manage.py test tests.test_domain

# Apenas testes de API
python manage.py test tests.test_api
```

---

## Endpoints da API REST

> Autenticação: faça login pela interface web ou via `POST /api/auth/login/`.
> A sessão do navegador é aceita automaticamente nas chamadas da interface.

### Autenticação
| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/auth/login/` | Login — retorna access + refresh token |
| POST | `/api/auth/refresh/` | Renova o access token |
| GET | `/api/auth/me/` | Dados do usuário logado |

### Clientes
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/clientes/` | Listar clientes |
| POST | `/api/clientes/` | Criar cliente *(ADMIN)* |
| GET | `/api/clientes/{id}/` | Detalhe |
| PUT | `/api/clientes/{id}/` | Atualizar *(ADMIN)* |
| DELETE | `/api/clientes/{id}/` | Remover *(ADMIN)* |

### Produtos
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/produtos/` | Listar produtos |
| POST | `/api/produtos/` | Criar produto *(ADMIN)* |
| GET | `/api/produtos/{id}/` | Detalhe |
| PUT | `/api/produtos/{id}/` | Atualizar *(ADMIN)* |
| DELETE | `/api/produtos/{id}/` | Remover *(ADMIN)* |

### Vendas
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/vendas/` | Listar vendas |
| POST | `/api/vendas/` | Registrar venda |
| GET | `/api/vendas/{id}/` | Detalhe |
| POST | `/api/vendas/periodo/` | Filtrar por período |

### Relatórios
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/relatorios/cliente/{id}/` | Por cliente |
| GET | `/api/relatorios/periodo/?inicio=YYYY-MM-DD&fim=YYYY-MM-DD` | Por período |
| GET | `/api/relatorios/produto/` | Por produto |

---

## Exemplo rápido com curl

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"sua_senha"}'

# Registrar venda
curl -X POST http://localhost:8000/api/vendas/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cliente_id":1,"itens":[{"produto_id":1,"quantidade":2}]}'
```

---

## Arquitetura

```
domain/          → Entidades puras com regras de negócio (Domain Model)
infrastructure/  → Repositórios com acesso ao banco (Repository Pattern)
application/     → Services, Factory e Strategies (Strategy + Factory)
apps/            → Views, Serializers, URLs (Camada de Apresentação Django)
templates/       → Interface HTML Bootstrap 5
tests/           → Testes unitários e de integração
```
