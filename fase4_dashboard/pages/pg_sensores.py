"""
FarmTech Solutions - Fase 7 | Pessoa 2
pg_sensores.py - Aba de analise dos sensores IoT (Fase 3) com ML integrado.

Exibe as ultimas leituras do banco, graficos interativos,
recomendacao de manejo em tempo real e predicao do modelo ML.
"""

import sys
import pandas as pd
import streamlit as st
from pathlib import Path

# ---------------------------------------------------------------------------
# Ajuste de paths
# ---------------------------------------------------------------------------
PASTA_ATUAL = Path(__file__).resolve().parent
ROOT_DIR    = PASTA_ATUAL.parent.parent

sys.path.insert(0, str(ROOT_DIR / "fase3_iot"))
sys.path.insert(0, str(ROOT_DIR / "fase2_banco_dados"))
sys.path.insert(0, str(PASTA_ATUAL.parent))  # fase4_dashboard

import crud_sensores
from visualizacoes import (
    plotar_evolucao_umidade,
    plotar_status_bomba,
    plotar_ph_ldr,
    plotar_npk,
)
from ml_modelo import gerar_dados_simulados, treinar_modelo_irrigacao, prever_estado
from predicoes_irrigacao import avaliar_cenario_irrigacao

# ---------------------------------------------------------------------------
# Cabecalho
# ---------------------------------------------------------------------------
st.header("📡 Analise de Sensores IoT e Irrigacao")
st.caption("Dados das ultimas 30 leituras gravadas no banco pela Fase 3.")

# ---------------------------------------------------------------------------
# Leitura do banco
# ---------------------------------------------------------------------------
try:
    leituras_raw = crud_sensores.listar_leituras(limite=30)
except Exception as e:
    st.error(f"Nao foi possivel conectar ao banco de dados: {e}")
    st.stop()

if not leituras_raw:
    st.info("O banco de dados esta vazio. Simule uma leitura na pagina principal antes de continuar.")
    st.stop()

df = pd.DataFrame([dict(row) for row in leituras_raw])

# ---------------------------------------------------------------------------
# Tabela de leituras
# ---------------------------------------------------------------------------
with st.expander("Ver tabela de leituras brutas", expanded=False):
    st.dataframe(df, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Graficos — linha 1
# ---------------------------------------------------------------------------
st.subheader("📊 Graficos de monitoramento")

col1, col2 = st.columns(2)

with col1:
    fig_umidade = plotar_evolucao_umidade(df)
    if fig_umidade:
        st.plotly_chart(fig_umidade, use_container_width=True)
    else:
        st.warning("Dados de umidade insuficientes para o grafico.")

with col2:
    fig_bomba = plotar_status_bomba(df)
    if fig_bomba:
        st.plotly_chart(fig_bomba, use_container_width=True)
    else:
        st.warning("Dados de status da bomba insuficientes para o grafico.")

# ---------------------------------------------------------------------------
# Graficos — linha 2
# ---------------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    fig_ph = plotar_ph_ldr(df)
    if fig_ph:
        st.plotly_chart(fig_ph, use_container_width=True)

with col4:
    fig_npk = plotar_npk(df)
    if fig_npk:
        st.plotly_chart(fig_npk, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Recomendacao de manejo (ultima leitura)
# ---------------------------------------------------------------------------
st.subheader("🌿 Recomendacao de Manejo")

ultima = df.iloc[0]

prev_chuva = st.toggle("Previsao de chuva nas proximas horas?", value=False)

try:
    resultado = avaliar_cenario_irrigacao(
        umidade_atual=float(ultima.get("umidade", 50)),
        ldr_atual=float(ultima.get("ph_ldr", 2000)),
        prev_chuva=prev_chuva,
    )

    nivel_cor = {
        "CRITICO": "error",
        "ALERTA":  "warning",
        "ATENCAO": "warning",
        "ESTAVEL": "success",
    }.get(resultado["nivel"], "info")

    getattr(st, nivel_cor)(
        f"**{resultado['nivel']}** — {resultado['mensagem']}  \n"
        f"➡️ Acao sugerida: _{resultado['acao']}_"
    )
except Exception as e:
    st.warning(f"Nao foi possivel gerar recomendacao: {e}")

st.divider()

# ---------------------------------------------------------------------------
# Predicao com Machine Learning
# ---------------------------------------------------------------------------
st.subheader("🤖 Predicao com Machine Learning (RandomForest)")

st.caption(
    "O modelo e treinado com dados simulados (mesma logica do ESP32) "
    "e aplicado sobre a ultima leitura do banco."
)

if st.button("Treinar modelo e prever estado da bomba"):
    with st.spinner("Treinando modelo..."):
        try:
            df_treino  = gerar_dados_simulados(300)
            modelo     = treinar_modelo_irrigacao(df_treino)

            features = [[
                float(ultima.get("umidade",  50)),
                float(ultima.get("ph_ldr",  2000)),
                int(ultima.get("falta_n", 0)),
                int(ultima.get("falta_p", 0)),
                int(ultima.get("falta_k", 0)),
            ]]

            predicao = prever_estado(modelo, features)[0]

            if predicao == 1:
                st.success("✅ Modelo recomenda: **LIGAR a bomba** com base na leitura atual.")
            else:
                st.info("💧 Modelo recomenda: **manter bomba desligada** com base na leitura atual.")

            st.caption(
                f"Features usadas: umidade={features[0][0]}% | "
                f"LDR={features[0][1]} | "
                f"N={'falta' if features[0][2] else 'ok'} | "
                f"P={'falta' if features[0][3] else 'ok'} | "
                f"K={'falta' if features[0][4] else 'ok'}"
            )

        except Exception as e:
            st.error(f"Erro ao treinar/prever: {e}")
