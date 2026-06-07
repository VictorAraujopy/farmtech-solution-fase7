"""
FarmTech Solutions - Fase 7 | Pessoa 1
api_meteorologica.py - Consome a API publica Open-Meteo e gera o
arquivo dados_meteorologicos.csv, que alimenta a analise em R (analise_r.R).

Open-Meteo e gratuita e NAO exige chave de API (diferente do OpenWeatherMap).
Doc: https://open-meteo.com/
Usa apenas a biblioteca padrao do Python (urllib), sem dependencias externas.
"""

import csv
import json
import urllib.request
import urllib.error
from pathlib import Path

# Regiao agricola de referencia: Ribeirao Preto/SP (polo de cafe)
LATITUDE = -21.17
LONGITUDE = -47.81
FORECAST_DAYS = 7

PASTA = Path(__file__).resolve().parent
CSV_PATH = PASTA / "dados_meteorologicos.csv"

URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    "&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
    "&timezone=America/Sao_Paulo"
    f"&forecast_days={FORECAST_DAYS}"
)


def buscar_dados():
    """Chama a Open-Meteo e devolve o bloco 'hourly' (um dict de listas)."""
    req = urllib.request.Request(URL, headers={"User-Agent": "FarmTech-Fase7"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        dados = json.loads(resp.read().decode("utf-8"))
    return dados["hourly"]


def salvar_csv(hourly):
    """Grava as leituras horarias no dados_meteorologicos.csv e devolve a contagem."""
    colunas = ["data_hora", "temperatura_c", "umidade_pct", "precipitacao_mm", "vento_kmh"]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(colunas)
        for i in range(len(hourly["time"])):
            escritor.writerow([
                hourly["time"][i],
                hourly["temperature_2m"][i],
                hourly["relative_humidity_2m"][i],
                hourly["precipitation"][i],
                hourly["wind_speed_10m"][i],
            ])
    return len(hourly["time"])


if __name__ == "__main__":
    try:
        hourly = buscar_dados()
        n = salvar_csv(hourly)
        print(f"OK: {n} leituras horarias salvas em '{CSV_PATH.name}'.")
    except (urllib.error.URLError, KeyError, TimeoutError) as erro:
        print(f"Falha ao consultar a API ({erro}). Confira a conexao com a internet.")
