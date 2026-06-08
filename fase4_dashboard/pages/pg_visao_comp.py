"""
FarmTech Solutions - Fase 7 | Pessoa 2
pg_visao_comp.py - Aba de visao computacional com YOLOv8 (Fase 6).

Oferece dois modos:
  1. Processar lote: varre a pasta imagens_teste/ automaticamente.
  2. Upload avulso: usuario sobe uma imagem direto pela interface.
"""

import sys
import tempfile
import streamlit as st
from pathlib import Path

# ---------------------------------------------------------------------------
# Ajuste de paths
# ---------------------------------------------------------------------------
PASTA_ATUAL = Path(__file__).resolve().parent
ROOT_DIR    = PASTA_ATUAL.parent.parent
FASE6_DIR   = ROOT_DIR / "fase6_visao_computacional"

sys.path.insert(0, str(FASE6_DIR))

import inferencia
import detector_yolo

# ---------------------------------------------------------------------------
# Cabecalho
# ---------------------------------------------------------------------------
st.header("🔍 Visao Computacional Agricola (YOLOv8)")
st.write(
    "Detecte pragas, doencas e anomalias nas lavouras usando "
    "redes neurais YOLOv8 sobre imagens capturadas por drones ou cameras de campo."
)
st.divider()

# ---------------------------------------------------------------------------
# Modo 1 — Processar lote da pasta imagens_teste/
# ---------------------------------------------------------------------------
st.subheader("📁 Modo 1 — Processar lote de imagens")
st.caption(f"Pasta monitorada: `{FASE6_DIR / 'imagens_teste'}`")

if st.button("Processar lote (imagens_teste/)", use_container_width=True):
    pasta_imagens = FASE6_DIR / "imagens_teste"

    if not pasta_imagens.exists():
        pasta_imagens.mkdir(parents=True)
        st.warning(
            f"A pasta `imagens_teste/` nao existia e foi criada. "
            "Adicione imagens `.jpg` ou `.png` nela e clique novamente."
        )
    else:
        with st.spinner("Carregando modelo YOLOv8 e processando imagens..."):
            try:
                resultados = inferencia.processar_pasta_imagens(str(pasta_imagens))

                if not resultados:
                    st.info("Nenhuma imagem encontrada na pasta. Adicione arquivos .jpg ou .png.")
                else:
                    st.success(f"{len(resultados)} imagem(ns) processada(s).")
                    for item in resultados:
                        with st.expander(f"📷 {item['arquivo']}", expanded=True):
                            if not item["deteccoes"]:
                                st.success("Nenhuma praga ou anomalia detectada.")
                            else:
                                st.warning(f"{len(item['deteccoes'])} objeto(s) detectado(s):")
                                for d in item["deteccoes"]:
                                    confianca_pct = f"{d['confianca'] * 100:.1f}%"
                                    st.write(
                                        f"- **{d['nome']}** "
                                        f"(classe #{d['classe_id']}) — "
                                        f"confianca: `{confianca_pct}`"
                                    )
            except Exception as e:
                st.error(f"Erro ao processar lote: {e}")

st.divider()

# ---------------------------------------------------------------------------
# Modo 2 — Upload avulso de imagem
# ---------------------------------------------------------------------------
st.subheader("📤 Modo 2 — Analisar imagem avulsa")
st.caption("Faca upload de uma foto diretamente pela interface para analise instantanea.")

arquivo_enviado = st.file_uploader(
    "Selecione uma imagem da lavoura",
    type=["jpg", "jpeg", "png"],
    help="Formatos aceitos: JPG, JPEG, PNG",
)

if arquivo_enviado is not None:
    st.image(arquivo_enviado, caption="Imagem enviada", use_column_width=True)

    if st.button("Analisar esta imagem", use_container_width=True):
        with st.spinner("Rodando inferencia YOLOv8..."):
            try:
                # Salva o upload em arquivo temporario para o YOLO processar
                sufixo = Path(arquivo_enviado.name).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
                    tmp.write(arquivo_enviado.read())
                    caminho_tmp = tmp.name

                modelo     = detector_yolo.inicializar_modelo()
                deteccoes  = detector_yolo.inferir_em_imagem(modelo, caminho_tmp)

                if not deteccoes:
                    st.success("Nenhuma praga ou anomalia detectada nesta imagem.")
                else:
                    st.warning(f"{len(deteccoes)} objeto(s) detectado(s):")
                    for d in deteccoes:
                        confianca_pct = f"{d['confianca'] * 100:.1f}%"
                        st.write(
                            f"- **{d['nome']}** "
                            f"(classe #{d['classe_id']}) — "
                            f"confianca: `{confianca_pct}`"
                        )

            except Exception as e:
                st.error(f"Erro ao analisar imagem: {e}")
