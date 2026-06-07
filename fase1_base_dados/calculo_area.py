"""
FarmTech Solutions - Fase 7 | Pessoa 1
calculo_area.py - Area e volume de plantio por talhao.

Cafe: talhao retangular (comprimento x largura)
Soja: talhao circular  (pivo central, usa o raio)
"""

import math


def area_retangular(comprimento_m, largura_m):
    """Area de um talhao retangular (cafe), em m2."""
    return comprimento_m * largura_m


def area_circular(raio_m):
    """Area de um talhao circular (soja, pivo central), em m2."""
    return math.pi * (raio_m ** 2)


def volume_preparo_solo(area_m2, profundidade_m=0.20):
    """Volume de solo preparado (m3) = area x profundidade.

    Profundidade padrao de 0,20 m (20 cm), faixa comum de preparo/aracao.
    """
    return area_m2 * profundidade_m


if __name__ == "__main__":
    a_cafe = area_retangular(200, 150)
    a_soja = area_circular(75)
    print(f"Cafe (200m x 150m): area = {a_cafe:.2f} m2 | "
          f"volume preparo = {volume_preparo_solo(a_cafe):.2f} m3")
    print(f"Soja (raio 75m):    area = {a_soja:.2f} m2 | "
          f"volume preparo = {volume_preparo_solo(a_soja):.2f} m3")
