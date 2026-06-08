"""
FarmTech Solutions - Fase 7 | Pessoa 2
visualizacoes.py - Graficos interativos com Plotly Express.

Funcoes disponiveis:
    plotar_evolucao_umidade(df)   - linha temporal de umidade
    plotar_status_bomba(df)       - pizza de acionamentos da bomba
    plotar_ph_ldr(df)             - linha temporal da leitura do LDR
    plotar_npk(df)                - barras empilhadas de deficiencias N/P/K
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def plotar_evolucao_umidade(df: pd.DataFrame):
    """
    Gera grafico de linha da umidade do solo ao longo do tempo.

    Args:
        df: DataFrame com colunas 'data_hora' e 'umidade'.

    Returns:
        Figura Plotly ou None se dados insuficientes.
    """
    if df.empty or "data_hora" not in df.columns or "umidade" not in df.columns:
        return None

    fig = px.line(
        df,
        x="data_hora",
        y="umidade",
        title="Monitoramento de Umidade do Solo",
        labels={"data_hora": "Data / Hora", "umidade": "Umidade (%)"},
        markers=True,
    )
    # Linha de referencia: limiar de irrigacao (60%)
    fig.add_hline(
        y=60,
        line_dash="dash",
        line_color="red",
        annotation_text="Limiar irrigacao (60%)",
        annotation_position="top left",
    )
    fig.update_layout(yaxis_range=[0, 100])
    return fig


def plotar_status_bomba(df: pd.DataFrame):
    """
    Gera grafico de pizza com a proporcao de acionamentos da bomba.

    Args:
        df: DataFrame com coluna 'status_bomba' (valores: 'LIGADA' / 'DESLIGADA').

    Returns:
        Figura Plotly ou None se dados insuficientes.
    """
    if df.empty or "status_bomba" not in df.columns:
        return None

    fig = px.pie(
        df,
        names="status_bomba",
        title="Frequencia de Acionamento da Bomba",
        color="status_bomba",
        color_discrete_map={"LIGADA": "#2ecc71", "DESLIGADA": "#e74c3c"},
    )
    fig.update_traces(textinfo="percent+label")
    return fig


def plotar_ph_ldr(df: pd.DataFrame):
    """
    Gera grafico de linha da leitura bruta do sensor LDR ao longo do tempo.
    A faixa ideal de pH (LDR 1500-2500) e destacada.

    Args:
        df: DataFrame com colunas 'data_hora' e 'ph_ldr'.

    Returns:
        Figura Plotly ou None se dados insuficientes.
    """
    if df.empty or "data_hora" not in df.columns or "ph_ldr" not in df.columns:
        return None

    fig = px.line(
        df,
        x="data_hora",
        y="ph_ldr",
        title="Leitura do Sensor LDR (pH simulado)",
        labels={"data_hora": "Data / Hora", "ph_ldr": "Leitura LDR (0-4095)"},
        markers=True,
    )
    # Faixa ideal de pH (LDR 1500-2500)
    fig.add_hrect(
        y0=1500, y1=2500,
        fillcolor="green", opacity=0.1,
        line_width=0,
        annotation_text="Faixa ideal",
        annotation_position="top right",
    )
    fig.update_layout(yaxis_range=[0, 4095])
    return fig


def plotar_npk(df: pd.DataFrame):
    """
    Gera grafico de barras empilhadas mostrando a contagem de leituras
    com deficiencia de N, P e K ao longo do tempo.

    Args:
        df: DataFrame com colunas 'data_hora', 'falta_n', 'falta_p', 'falta_k'.

    Returns:
        Figura Plotly ou None se dados insuficientes.
    """
    colunas = ["data_hora", "falta_n", "falta_p", "falta_k"]
    if df.empty or not all(c in df.columns for c in colunas):
        return None

    df_npk = df[colunas].copy()
    df_npk = df_npk.rename(columns={
        "falta_n": "Nitrogenio (N)",
        "falta_p": "Fosforo (P)",
        "falta_k": "Potassio (K)",
    })
    df_melted = df_npk.melt(id_vars="data_hora", var_name="Nutriente", value_name="Deficiencia")
    df_melted = df_melted[df_melted["Deficiencia"] == 1]

    if df_melted.empty:
        return None

    fig = px.bar(
        df_melted,
        x="data_hora",
        color="Nutriente",
        title="Ocorrencias de Deficiencia de Nutrientes",
        labels={"data_hora": "Data / Hora", "count": "Ocorrencias"},
        barmode="stack",
    )
    return fig
