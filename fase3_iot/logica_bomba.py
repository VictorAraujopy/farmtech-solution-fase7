"""
FarmTech Solutions - Fase 7 | Pessoa 1
logica_bomba.py - Regra de acionamento da bomba de irrigacao.

Mesma logica do esp32_irrigacao.ino, reescrita em Python para rodar no PC
e alimentar o banco. A bomba LIGA somente se TODAS as condicoes valem:
  - umidade do solo abaixo de 60%
  - pH (valor do LDR) na faixa ideal 1500..2500
  - nenhum nutriente (N, P, K) em falta
"""

UMIDADE_MINIMA = 60
PH_MIN = 1500
PH_MAX = 2500


def decidir_bomba(umidade, ph_ldr, falta_n, falta_p, falta_k):
    """Devolve 'LIGADA' ou 'DESLIGADA' conforme a regra de irrigacao."""
    solo_seco = umidade < UMIDADE_MINIMA
    ph_ok = PH_MIN <= ph_ldr <= PH_MAX
    nutrientes_ok = not (falta_n or falta_p or falta_k)

    if solo_seco and ph_ok and nutrientes_ok:
        return "LIGADA"
    return "DESLIGADA"


if __name__ == "__main__":
    print("seco + pH ok + NPK ok ->", decidir_bomba(45, 2000, False, False, False))
    print("solo umido            ->", decidir_bomba(75, 2000, False, False, False))
    print("falta N               ->", decidir_bomba(45, 2000, True, False, False))
    print("pH fora da faixa      ->", decidir_bomba(45, 1000, False, False, False))
