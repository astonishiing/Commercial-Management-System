-- ================================================================
-- SGC — Sistema de Gestão Comercial
-- Script de criação do banco de dados (MySQL/MariaDB)
-- Para uso com SQLite no Django, basta rodar: python manage.py migrate
-- ================================================================

CREATE DATABASE IF NOT EXISTS sgc CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sgc;

-- ── USUÁRIOS ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50)  NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,         -- hash Django (bcrypt/PBKDF2)
    perfil   ENUM('ADMIN','FUNCIONARIO') NOT NULL DEFAULT 'FUNCIONARIO',
    is_active   TINYINT(1) NOT NULL DEFAULT 1,
    is_staff    TINYINT(1) NOT NULL DEFAULT 0,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    last_login  DATETIME NULL
);

-- ── CLIENTES ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clientes (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nome     VARCHAR(100) NOT NULL,
    cpf      VARCHAR(14)  NOT NULL UNIQUE,
    email    VARCHAR(100),
    telefone VARCHAR(20),
    endereco VARCHAR(200)
);

-- ── PRODUTOS ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS produtos (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    nome               VARCHAR(100)    NOT NULL,
    descricao          TEXT,
    preco              DECIMAL(10,2)   NOT NULL,
    quantidade_estoque INT             NOT NULL DEFAULT 0,
    CONSTRAINT chk_preco_positivo CHECK (preco >= 0),
    CONSTRAINT chk_estoque_positivo CHECK (quantidade_estoque >= 0)
);

-- ── VENDAS ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vendas (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    data        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cliente_id  INT           NOT NULL,
    usuario_id  INT           NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);

-- ── ITENS DE VENDA ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS itens_venda (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    venda_id       INT           NOT NULL,
    produto_id     INT           NOT NULL,
    quantidade     INT           NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    subtotal       DECIMAL(10,2) NOT NULL,
    CONSTRAINT chk_quantidade_positiva CHECK (quantidade > 0),
    FOREIGN KEY (venda_id)   REFERENCES vendas(id)   ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT
);
