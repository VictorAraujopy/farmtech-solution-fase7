"""
FarmTech Solutions - Fase 7 | Pessoa 1
conexao_db.py - Conexao reutilizavel com o banco SQLite.

Todos os modulos (CRUD de talhoes e CRUD de sensores) abrem o banco
por aqui, garantindo que as chaves estrangeiras estejam sempre ativas
e que o caminho do banco seja o mesmo para o projeto inteiro.
"""

import sqlite3
from pathlib import Path

# Caminho ancorado neste arquivo -> funciona de qualquer pasta que rode o script
PASTA = Path(__file__).resolve().parent
DB_PATH = PASTA / "farmtech.db"
SCHEMA_PATH = PASTA / "schema.sql"


def conectar() -> sqlite3.Connection:
    """Abre o banco e devolve a conexao pronta para uso."""
    con = sqlite3.connect(str(DB_PATH))
    con.execute("PRAGMA foreign_keys = ON;")   # SQLite exige ligar a cada conexao
    con.row_factory = sqlite3.Row              # permite acessar colunas pelo nome
    return con


def criar_banco() -> None:
    """Cria (ou recria) o banco a partir do schema.sql - fonte unica do DDL."""
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    con = conectar()
    con.executescript(sql)
    con.commit()
    con.close()
    print(f"Banco pronto em: {DB_PATH}")


if __name__ == "__main__":
    # Rodar este arquivo cria o banco e confere as tabelas (teste rapido)
    criar_banco()
    con = conectar()
    tabelas = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    ).fetchall()
    print("Tabelas no banco:", [t["name"] for t in tabelas])
    con.close()
