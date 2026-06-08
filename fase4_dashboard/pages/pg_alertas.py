"""
FarmTech Solutions - Fase 7 | Pessoa 2
pg_alertas.py - Aba de gerenciamento de alertas via AWS SNS (Fase 5).

Permite disparar alertas manuais para o topico SNS configurado,
com selecao de severidade e preview do payload antes do envio.
"""

import sys
import streamlit as st
from pathlib import Path

# ---------------------------------------------------------------------------
# Ajuste de paths
# ---------------------------------------------------------------------------
PASTA_ATUAL = Path(__file__).resolve().parent
ROOT_DIR    = PASTA_ATUAL.parent.parent

sys.path.insert(0, str(ROOT_DIR / "fase5_cloud_aws"))

# ---------------------------------------------------------------------------
# Importacao opcional do modulo AWS
# ---------------------------------------------------------------------------
try:
    import alerta_sns
    HAS_AWS = True
except ImportError:
    HAS_AWS = False

# ---------------------------------------------------------------------------
# Cabecalho
# ---------------------------------------------------------------------------
st.header("🚨 Gerenciamento de Alertas — AWS SNS (Fase 5)")
st.caption("Dispare notificacoes operacionais para a equipe de campo via Amazon SNS.")

# ---------------------------------------------------------------------------
# Aviso se AWS nao configurada
# ---------------------------------------------------------------------------
if not HAS_AWS:
    st.error(
        "**Modulo AWS nao disponivel.**  \n"
        "Verifique se `boto3` esta instalado e se `alerta_sns.py` esta em `fase5_cloud_aws/`.  \n"
        "Configure suas credenciais com `aws configure` antes de usar esta aba."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Formulario de disparo
# ---------------------------------------------------------------------------
st.subheader("Novo alerta")

col_sev, col_orig = st.columns(2)

with col_sev:
    severidade = st.selectbox(
        "Nivel de severidade",
        options=["CRITICA", "ALTA", "MEDIA", "BAIXA"],
        index=0,
        help="CRITICA = acao imediata necessaria | BAIXA = apenas informativo",
    )

with col_orig:
    origem = st.selectbox(
        "Origem do alerta",
        options=["Sensor IoT", "Visao Computacional (YOLO)", "Operador Manual", "Sistema"],
    )

mensagem = st.text_area(
    "Descricao do alerta",
    placeholder="Ex: Umidade do talhao de cafe abaixo de 40%. Irrigacao imediata necessaria.",
    height=120,
)

# Preview do payload
with st.expander("Ver payload JSON que sera enviado", expanded=False):
    import json
    payload_preview = {
        "origem": f"FarmTech Solutions — {origem}",
        "severidade": severidade,
        "detalhes": mensagem or "(sem mensagem)",
    }
    st.code(json.dumps(payload_preview, indent=2, ensure_ascii=False), language="json")

# Botao de envio
st.divider()
col_btn, col_vazio = st.columns([1, 3])

with col_btn:
    enviar = st.button(
        "📤 Disparar alerta no SNS",
        use_container_width=True,
        disabled=(not mensagem.strip()),
        help="Preencha a descricao do alerta para habilitar o envio.",
    )

if enviar:
    if not mensagem.strip():
        st.warning("Digite a descricao do alerta antes de enviar.")
    else:
        with st.spinner("Publicando no topico SNS..."):
            try:
                msg_id = alerta_sns.notificar_equipe(
                    mensagem=f"[{origem}] {mensagem}",
                    severidade=severidade,
                )
                st.success(
                    f"✅ Alerta publicado com sucesso!  \n"
                    f"**MessageID:** `{msg_id}`  \n"
                    f"**Severidade:** {severidade}"
                )
            except Exception as e:
                st.error(
                    f"Erro ao publicar no SNS.  \n"
                    f"Verifique suas credenciais em `~/.aws/credentials` e o ARN do topico.  \n"
                    f"Detalhe: `{e}`"
                )

# ---------------------------------------------------------------------------
# Rodape informativo
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Para configurar as credenciais AWS, execute `aws configure` no terminal "
    "e informe o Access Key com permissao `sns:Publish`."
)
