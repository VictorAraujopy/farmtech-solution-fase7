"""
FarmTech Solutions - Fase 7 | Pessoa 1
sensor_ldr_ph.py - Simulacao de pH a partir do sensor de luz (LDR).

No projeto o LDR (0..4095 no ADC do ESP32) representa a escala de pH.
Geramos o valor bruto e tambem convertemos para pH aproximado (0..14)
para facilitar a leitura humana.
"""

import random

ADC_MAX = 4095


def ler_ldr():
    """Valor bruto do LDR (0..4095), como o ESP32 leria no pino analogico."""
    return random.randint(0, ADC_MAX)


def ldr_para_ph(valor_ldr):
    """Converte o valor bruto do LDR (0..4095) para a escala de pH (0..14)."""
    return round(valor_ldr / ADC_MAX * 14, 2)


if __name__ == "__main__":
    for _ in range(3):
        v = ler_ldr()
        print(f"LDR={v} -> pH aprox {ldr_para_ph(v)}")
