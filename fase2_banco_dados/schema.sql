-- ============================================================
-- FarmTech Solutions - Fase 7 | Pessoa 1
-- schema.sql - Estrutura do banco de dados relacional (SQLite)
--
-- Modela o fluxo: cultura -> talhao -> leitura de sensor
--   . manejo agricola (talhoes/culturas) vem da Fase 1
--   . leituras dos sensores IoT vem da Fase 3 (ESP32)
-- Para criar o banco do zero:  sqlite3 farmtech.db < schema.sql
-- ============================================================

PRAGMA foreign_keys = ON;   -- SQLite nao forca FK por padrao; precisa ligar

-- Recria tudo do zero (ordem reversa por causa das chaves estrangeiras)
DROP TABLE IF EXISTS leituras_sensores;
DROP TABLE IF EXISTS talhoes;
DROP TABLE IF EXISTS culturas;

-- ------------------------------------------------------------
-- Tabela de dominio: as 2 culturas monitoradas no projeto
-- ------------------------------------------------------------
CREATE TABLE culturas (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT NOT NULL UNIQUE,        -- 'cafe' ou 'soja'
    descricao TEXT
);

-- ------------------------------------------------------------
-- Talhoes de plantio (Fase 1: calculo de area e de insumos)
-- ------------------------------------------------------------
CREATE TABLE talhoes (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    cultura_id     INTEGER NOT NULL,
    nome           TEXT    NOT NULL,
    area_m2        REAL    NOT NULL CHECK (area_m2 >= 0),
    ruas           INTEGER NOT NULL CHECK (ruas >= 0),
    metros_por_rua REAL    NOT NULL CHECK (metros_por_rua >= 0),
    dose_ml_por_m  REAL    NOT NULL CHECK (dose_ml_por_m >= 0),
    litros         REAL    NOT NULL CHECK (litros >= 0),
    FOREIGN KEY (cultura_id) REFERENCES culturas(id)
);

-- ------------------------------------------------------------
-- Leituras dos sensores IoT (Fase 3: ESP32 no Wokwi)
-- Espelha o dados_sensores.csv: umidade, pH(LDR), NPK e bomba
-- ------------------------------------------------------------
CREATE TABLE leituras_sensores (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    talhao_id    INTEGER,
    data_hora    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    umidade      REAL    NOT NULL CHECK (umidade BETWEEN 0 AND 100),
    ph_ldr       INTEGER NOT NULL CHECK (ph_ldr BETWEEN 0 AND 4095),
    status_n     TEXT    NOT NULL CHECK (status_n IN ('OK','FALTA')),
    status_p     TEXT    NOT NULL CHECK (status_p IN ('OK','FALTA')),
    status_k     TEXT    NOT NULL CHECK (status_k IN ('OK','FALTA')),
    status_bomba TEXT    NOT NULL CHECK (status_bomba IN ('LIGADA','DESLIGADA')),
    FOREIGN KEY (talhao_id) REFERENCES talhoes(id)
);

-- ------------------------------------------------------------
-- Indices para acelerar as consultas mais comuns
-- ------------------------------------------------------------
CREATE INDEX idx_talhoes_cultura ON talhoes(cultura_id);
CREATE INDEX idx_leituras_talhao ON leituras_sensores(talhao_id);
CREATE INDEX idx_leituras_data   ON leituras_sensores(data_hora);

-- ------------------------------------------------------------
-- Seed: as 2 culturas oficiais (FAZER PRIMEIRO do enunciado)
-- ------------------------------------------------------------
INSERT INTO culturas (nome, descricao) VALUES
    ('cafe', 'Cultura de cafe - talhao retangular (comprimento x largura)'),
    ('soja', 'Cultura de soja - talhao circular (pivo central, usa o raio)');
