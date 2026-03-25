-- =============================================
-- SISTEMA DE ESTOQUE E FARMÁCIA - GRUPO 3
-- BANCO DE DADOS POSTGRESQL
-- SCHEMA: projeto
-- =============================================

-- Criar schema
CREATE SCHEMA IF NOT EXISTS projeto;

-- =============================================
-- 1. TABELAS DE CADASTRO
-- =============================================

-- Medicamentos
CREATE TABLE IF NOT EXISTS projeto.medicamentos (
    codigo NUMERIC(20) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    principio_ativo VARCHAR(100),
    concentracao VARCHAR(30),
    forma_farmaceutica VARCHAR(30),
    controlado BOOLEAN DEFAULT FALSE,
    preco_venda NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lotes
CREATE TABLE IF NOT EXISTS projeto.lotes (
    id_lote SERIAL PRIMARY KEY,
    codigo_medicamento NUMERIC(20) NOT NULL REFERENCES projeto.medicamentos(codigo) ON DELETE RESTRICT,
    numero_lote VARCHAR(30) NOT NULL,
    data_fabricacao DATE,
    data_validade DATE NOT NULL,
    quantidade_inicial NUMERIC(6,3) NOT NULL,
    quantidade_atual NUMERIC(6,3) NOT NULL,
    preco_compra NUMERIC(10,2),
    preco_venda NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(codigo_medicamento, numero_lote)
);

-- =============================================
-- 2. TABELAS DE LOG
-- =============================================

-- Log das consultas
CREATE TABLE IF NOT EXISTS projeto.logs_consultas (
    id_log SERIAL PRIMARY KEY,
    arquivo_nome VARCHAR(100) NOT NULL,
    id_prescricao NUMERIC(30) NOT NULL,
    cpf_paciente NUMERIC(11) NOT NULL,
    codigo_medicamento NUMERIC(20) NOT NULL,
    quantidade NUMERIC(6,3) NOT NULL,
    disponivel BOOLEAN,
    lote_sugerido VARCHAR(30),
    validade_lote DATE,
    observacao VARCHAR(200),
    data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Log das reservas
CREATE TABLE IF NOT EXISTS projeto.logs_reservas (
    id_log SERIAL PRIMARY KEY,
    arquivo_nome VARCHAR(100) NOT NULL,
    id_prescricao NUMERIC(30) NOT NULL,
    cpf_paciente NUMERIC(11) NOT NULL,
    codigo_medicamento NUMERIC(20) NOT NULL,
    quantidade NUMERIC(6,3) NOT NULL,
    lote VARCHAR(30) NOT NULL,
    id_lote INTEGER REFERENCES projeto.lotes(id_lote),
    status VARCHAR(20) DEFAULT 'PROCESSADO',
    observacao VARCHAR(200),
    data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Log das baixas
CREATE TABLE IF NOT EXISTS projeto.logs_baixas (
    id_log SERIAL PRIMARY KEY,
    arquivo_nome VARCHAR(100) NOT NULL,
    id_prescricao NUMERIC(30) NOT NULL,
    cpf_paciente NUMERIC(11) NOT NULL,
    codigo_medicamento NUMERIC(20) NOT NULL,
    quantidade NUMERIC(6,3) NOT NULL,
    lote VARCHAR(30) NOT NULL,
    data_uso NUMERIC(6),
    id_lote INTEGER REFERENCES projeto.lotes(id_lote),
    status VARCHAR(20) DEFAULT 'PROCESSADO',
    observacao VARCHAR(200),
    data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Log dos consumos enviados
CREATE TABLE IF NOT EXISTS projeto.logs_consumos (
    id_log SERIAL PRIMARY KEY,
    arquivo_nome VARCHAR(100) NOT NULL,
    data_consumo DATE NOT NULL,
    total_itens INTEGER,
    total_valor NUMERIC(12,2),
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 3. TABELAS DE MOVIMENTAÇÃO E CONSUMO
-- =============================================

-- Movimentações de estoque
CREATE TABLE IF NOT EXISTS projeto.movimentacoes (
    id_mov SERIAL PRIMARY KEY,
    id_lote INTEGER NOT NULL REFERENCES projeto.lotes(id_lote),
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('ENTRADA', 'RESERVA', 'BAIXA', 'AJUSTE')),
    quantidade NUMERIC(6,3) NOT NULL,
    quantidade_anterior NUMERIC(6,3) NOT NULL,
    quantidade_nova NUMERIC(6,3) NOT NULL,
    referencia_id INTEGER,
    referencia_tabela VARCHAR(30),
    data_mov TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(50) DEFAULT 'SISTEMA'
);

-- Itens de consumo
CREATE TABLE IF NOT EXISTS projeto.itens_consumo (
    id_item SERIAL PRIMARY KEY,
    id_prescricao NUMERIC(30) NOT NULL,
    cpf_paciente NUMERIC(11) NOT NULL,
    codigo_medicamento NUMERIC(20) NOT NULL,
    quantidade NUMERIC(6,3) NOT NULL,
    preco_total NUMERIC(10,2) NOT NULL,
    data_uso NUMERIC(6) NOT NULL,
    lote VARCHAR(30) NOT NULL,
    id_lote INTEGER REFERENCES projeto.lotes(id_lote),
    id_baixa_log INTEGER REFERENCES projeto.logs_baixas(id_log),
    consolidado_em DATE DEFAULT CURRENT_DATE,
    enviado_para_g1 BOOLEAN DEFAULT FALSE,
    enviado_em TIMESTAMP
);

-- =============================================
-- 4. ÍNDICES
-- =============================================

CREATE INDEX IF NOT EXISTS idx_lotes_validade ON projeto.lotes(data_validade);
CREATE INDEX IF NOT EXISTS idx_lotes_medicamento ON projeto.lotes(codigo_medicamento);
CREATE INDEX IF NOT EXISTS idx_itens_consumo_enviado ON projeto.itens_consumo(enviado_para_g1);
CREATE INDEX IF NOT EXISTS idx_itens_consumo_data ON projeto.itens_consumo(consolidado_em);

-- =============================================
-- 5. VIEWS
-- =============================================

CREATE OR REPLACE VIEW projeto.vw_estoque_atual AS
SELECT 
    m.codigo,
    m.nome,
    l.numero_lote,
    l.data_validade,
    l.quantidade_atual,
    l.preco_venda,
    (l.data_validade - CURRENT_DATE) AS dias_para_vencer
FROM projeto.lotes l
JOIN projeto.medicamentos m ON m.codigo = l.codigo_medicamento
WHERE l.quantidade_atual > 0 AND l.data_validade >= CURRENT_DATE
ORDER BY m.nome, l.data_validade;