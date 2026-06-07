"""
FarmTech Solutions - Fase 7 | Pessoa 1
sensor_dht22.py - Leitura do sensor de umidade/temperatura (DHT22).

No hardware real (esp32_irrigacao.ino) o DHT22 mede umidade e temperatura.
Sem a placa, simulamos leituras dentro de faixas realistas para alimentar
o restante do sistema (logica da bomba e gravacao no banco).
"""

import random


def ler_dht22():
    """Devolve uma leitura simulada: umidade (%) e temperatura (C)."""
    return {
        "umidade": round(random.uniform(30, 90), 1),
        "temperatura": round(random.uniform(15, 35), 1),
    }


if __name__ == "__main__":
    for _ in range(3):
        print(ler_dht22())
