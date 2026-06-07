"""
FarmTech Solutions - Fase 7 | Pessoa 1
crud_sensores.py - Grava as leituras dos sensores IoT no banco (Fase 2).

Junta as 3 pecas da Fase 3:
  sensor_dht22 (umidade) + sensor_ldr_ph (pH) + logica_bomba (decisao)
e persiste cada ciclo na tabela leituras_sensores do farmtech.db.

Fluxo demonstrado:  sensor -> decisao da bomba -> CRUD -> banco
"""

import sys
import random
from pathlib import Path

# Permite importar o conexao_db.py, que vive na pasta da Fase 2
FASE2 = Path(__file__).resolve().parent.parent / "fase2_banco_dados"
sys.path.insert(0, str(FASE2))

import conexao_db as db                      # noqa: E402  (import apos ajustar o path)
from sensor_dht22 import ler_dht22           # noqa: E402
from sensor_ldr_ph import ler_ldr            # noqa: E402
from logica_bomba import decidir_bomba       # noqa: E402


def gravar_leitura(talhao_id=None):
    """Le os sensores, decide a bomba e grava 1 leitura. Devolve o que gravou."""
    dht = ler_dht22()
    ph_ldr = ler_ldr()
    # Status NPK simulado (na placa real vem dos botoes N/P/K)
    falta_n = random.random() < 0.15
    falta_p = random.random() < 0.15
    falta_k = random.random() < 0.15

    leitura = {
        "talhao_id": talhao_id,
        "umidade": dht["umidade"],
        "ph_ldr": ph_ldr,
        "status_n": "FALTA" if falta_n else "OK",
        "status_p": "FALTA" if falta_p else "OK",
        "status_k": "FALTA" if falta_k else "OK",
        "status_bomba": decidir_bomba(dht["umidade"], ph_ldr, falta_n, falta_p, falta_k),
    }

    con = db.conectar()
    con.execute(
        """INSERT INTO leituras_sensores
               (talhao_id, umidade, ph_ldr, status_n, status_p, status_k, status_bomba)
           VALUES (:talhao_id, :umidade, :ph_ldr, :status_n, :status_p, :status_k, :status_bomba)""",
        leitura,
    )
    con.commit()
    con.close()
    return leitura


def listar_leituras(limite=10):
    """Devolve as ultimas leituras gravadas no banco."""
    con = db.conectar()
    linhas = con.execute(
        """SELECT id, data_hora, umidade, ph_ldr, status_bomba
             FROM leituras_sensores
         ORDER BY id DESC
            LIMIT ?""",
        (limite,),
    ).fetchall()
    con.close()
    return linhas


if __name__ == "__main__":
    from crud_operacoes import inserir_talhao  # disponivel via path da Fase 2

    db.criar_banco()  # banco limpo para a demonstracao
    tid = inserir_talhao(1, "Talhao Cafe Sul", 30000.0, 25, 80.0, 400.0, 800.0)
    print(f">> Talhao de teste criado (id={tid}). Simulando 5 ciclos de leitura...")

    for _ in range(5):
        l = gravar_leitura(talhao_id=tid)
        print(f"   umid={l['umidade']:.1f}% pH(LDR)={l['ph_ldr']:4d} "
              f"N/P/K={l['status_n']}/{l['status_p']}/{l['status_k']} -> bomba {l['status_bomba']}")

    print(">> Ultimas leituras no banco:")
    for r in listar_leituras():
        print(f"   [{r['id']}] {r['data_hora']} | umid={r['umidade']:.1f}% | bomba={r['status_bomba']}")
