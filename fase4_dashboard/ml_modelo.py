"""
FarmTech Solutions - Fase 7 | Pessoa 2
ml_modelo.py - Logica de treino e predicao com Scikit-Learn.

O modelo RandomForest aprende com leituras historicas dos sensores
para prever se a bomba de irrigacao deve ser acionada.

Features de entrada:
    umidade  (float) - porcentagem de umidade do solo (0-100)
    ph_ldr   (int)   - leitura bruta do sensor LDR (0-4095)
    falta_n  (int)   - deficiencia de Nitrogenio: 1=sim, 0=nao
    falta_p  (int)   - deficiencia de Fosforo:    1=sim, 0=nao
    falta_k  (int)   - deficiencia de Potassio:   1=sim, 0=nao

Target:
    bomba_ligada (int) - 1=bomba deve ligar, 0=nao ligar
"""

import random
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# ---------------------------------------------------------------------------
# Geracao de dados simulados (usado quando o banco ainda nao tem leituras)
# ---------------------------------------------------------------------------

def gerar_dados_simulados(n_amostras: int = 200) -> pd.DataFrame:
    """
    Gera um DataFrame sintetico com leituras de sensores simuladas,
    seguindo a mesma regra de decisao do esp32_irrigacao.ino:
      - umidade < 60%
      - LDR entre 1500 e 2500 (solo em pH adequado)
      - sem deficiencia de nutrientes
    """
    random.seed(42)
    registros = []

    for _ in range(n_amostras):
        umidade = round(random.uniform(20, 100), 1)
        ph_ldr  = random.randint(500, 3500)
        falta_n = random.randint(0, 1)
        falta_p = random.randint(0, 1)
        falta_k = random.randint(0, 1)

        # Mesma logica do sketch do ESP32
        bomba = int(
            umidade < 60
            and 1500 <= ph_ldr <= 2500
            and falta_n == 0
            and falta_p == 0
            and falta_k == 0
        )
        registros.append([umidade, ph_ldr, falta_n, falta_p, falta_k, bomba])

    return pd.DataFrame(
        registros,
        columns=["umidade", "ph_ldr", "falta_n", "falta_p", "falta_k", "bomba_ligada"]
    )


# ---------------------------------------------------------------------------
# Treino
# ---------------------------------------------------------------------------

def treinar_modelo_irrigacao(df_dados: pd.DataFrame) -> RandomForestClassifier:
    """
    Treina um RandomForestClassifier para prever a necessidade de irrigacao.

    Args:
        df_dados: DataFrame com colunas
                  [umidade, ph_ldr, falta_n, falta_p, falta_k, bomba_ligada].

    Returns:
        Modelo treinado, pronto para uso em prever_estado().
    """
    colunas_necessarias = ["umidade", "ph_ldr", "falta_n", "falta_p", "falta_k", "bomba_ligada"]
    for col in colunas_necessarias:
        if col not in df_dados.columns:
            raise ValueError(f"Coluna obrigatoria ausente no DataFrame: '{col}'")

    X = df_dados[["umidade", "ph_ldr", "falta_n", "falta_p", "falta_k"]]
    y = df_dados["bomba_ligada"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    predicoes = modelo.predict(X_test)
    acuracia  = accuracy_score(y_test, predicoes)

    print(f"[ML] Modelo treinado com {len(X_train)} amostras.")
    print(f"[ML] Acuracia no conjunto de teste: {acuracia:.2%}")
    print(classification_report(y_test, predicoes, target_names=["Desligada", "Ligada"]))

    return modelo


# ---------------------------------------------------------------------------
# Predicao
# ---------------------------------------------------------------------------

def prever_estado(modelo: RandomForestClassifier, novos_dados: list) -> list:
    """
    Gera predicoes sobre o estado da bomba.

    Args:
        modelo:      Modelo treinado por treinar_modelo_irrigacao().
        novos_dados: Lista de listas com 5 features cada:
                     [[umidade, ph_ldr, falta_n, falta_p, falta_k], ...]

    Returns:
        Lista de inteiros: 1 = ligar bomba, 0 = nao ligar.

    Exemplo:
        prever_estado(modelo, [[45.0, 1800, 0, 0, 0]])  # -> [1]
        prever_estado(modelo, [[80.0, 1800, 0, 0, 0]])  # -> [0]
    """
    return modelo.predict(novos_dados).tolist()


# ---------------------------------------------------------------------------
# Execucao standalone para teste rapido
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Teste do modulo ml_modelo.py ===\n")
    df = gerar_dados_simulados(300)
    print(f"Dataset gerado: {len(df)} amostras | Bomba ligada em {df['bomba_ligada'].sum()} casos\n")

    modelo = treinar_modelo_irrigacao(df)

    casos_teste = [
        [45.0, 1800, 0, 0, 0],   # umidade baixa, pH ok, sem falta -> ligar
        [80.0, 1800, 0, 0, 0],   # umidade alta                    -> nao ligar
        [40.0, 800,  0, 0, 0],   # pH fora da faixa                -> nao ligar
        [35.0, 2000, 1, 0, 0],   # falta N                         -> nao ligar
    ]
    resultados = prever_estado(modelo, casos_teste)
    print("\nPredicoes para casos de teste:")
    for caso, res in zip(casos_teste, resultados):
        status = "LIGAR BOMBA" if res == 1 else "nao ligar"
        print(f"  {caso} -> {status}")
