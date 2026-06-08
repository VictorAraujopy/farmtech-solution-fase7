"""
FarmTech Solutions - Fase 7 | Pessoa 2
app.py - Entry point do Streamlit (Fase 4).

Integra as execucoes do banco de dados (Fase 1 e 2),
dos sensores IoT (Fase 3) e visao computacional (Fase 6).

Execucao:
    streamlit run fase4_dashboard/app.py
"""

import sys
from pathlib import Path
import streamlit as st

# ---------------------------------------------------------------------------
# Ajuste de paths para importar modulos das outras fases
# ---------------------------------------------------------------------------
PASTA_ATUAL = Path(__file__).resolve().parent
ROOT_DIR = PASTA_ATUAL.parent

sys.path.insert(0, str(ROOT_DIR / "fase1_base_dados"))
sys.path.insert(0, str(ROOT_DIR / "fase3_iot"))
sys.path.insert(0, str(ROOT_DIR / "fase6_visao_computacional"))

# ---------------------------------------------------------------------------
# Configuracao da pagina
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FarmTech Solutions",
    page_icon="🌱",
    layout="wide",
)

st.title("🌱 FarmTech Solutions — Dashboard")
st.markdown(
    "Central integrada do projeto FarmTech. "
    "Use os botoes abaixo para acionar os modulos ou navegue pelas abas no menu lateral."
)
st.divider()

# ---------------------------------------------------------------------------
# Acoes rapidas na pagina principal
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🌦️ Meteorologia")
    st.caption("Fase 1 — Open-Meteo API")
    if st.button("Buscar dados meteorologicos", use_container_width=True):
        try:
            import api_meteorologica
            hourly = api_meteorologica.buscar_dados()
            n = api_meteorologica.salvar_csv(hourly)
            st.success(f"{n} leituras salvas em CSV com sucesso!")
        except ImportError:
            st.error("Modulo api_meteorologica nao encontrado. Verifique a Fase 1.")
        except Exception as e:
            st.error(f"Erro na API meteorologica: {e}")

with col2:
    st.subheader("📡 Sensores IoT")
    st.caption("Fase 3 — ESP32 simulado")
    if st.button("Simular leitura do sensor", use_container_width=True):
        try:
            import crud_sensores
            leitura = crud_sensores.gravar_leitura(talhao_id=1)
            st.success(
                f"Gravado no banco!  \n"
                f"Umidade: **{leitura['umidade']}%**  \n"
                f"Bomba: **{leitura['status_bomba']}**"
            )
        except ImportError:
            st.error("Modulo crud_sensores nao encontrado. Verifique a Fase 3.")
        except Exception as e:
            st.error(f"Erro ao simular sensor — verifique se o banco esta criado. Detalhe: {e}")

with col3:
    st.subheader("🔍 Visao Computacional")
    st.caption("Fase 6 — YOLOv8")
    st.info("Acesse a aba **Visao Computacional** no menu lateral para processar imagens.")

st.divider()
st.caption("FarmTech Solutions — Fase 7 | Grupo X")
