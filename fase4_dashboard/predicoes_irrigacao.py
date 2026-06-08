"""
FarmTech Solutions - Fase 7 | Pessoa 2
predicoes_irrigacao.py - Sugestoes de manejo baseadas em regras agronomicas.

Cruza dados de hardware (Fase 3) com previsao do tempo para
gerar recomendacoes de proxima acao ao operador.

Nota tecnica:
    O parametro 'ldr_atual' representa a leitura bruta do sensor LDR
    (escala 0-4095), conforme implementado em sensor_ldr_ph.py (Fase 3).
    Faixa de pH adequado corresponde a LDR entre 1500 e 2500.
"""


def avaliar_cenario_irrigacao(
    umidade_atual: float,
    ldr_atual: float,
    prev_chuva: bool
) -> dict:
    """
    Avalia o estado atual do talhao e retorna recomendacao de manejo.

    Args:
        umidade_atual: Umidade do solo em porcentagem (0.0 a 100.0).
        ldr_atual:     Leitura bruta do LDR (0 a 4095).
                       Faixa ideal: 1500-2500 (pH neutro a levemente acido).
        prev_chuva:    True se ha previsao de chuva nas proximas horas.

    Returns:
        Dicionario com:
            'nivel'       - 'CRITICO', 'ALERTA', 'ATENCAO' ou 'ESTAVEL'
            'mensagem'    - descricao da recomendacao para o operador
            'acao'        - acao sugerida em formato curto
    """
    solo_seco    = umidade_atual < 60
    ph_acido     = ldr_atual < 1500          # abaixo da faixa ideal -> mais acido
    ph_alcalino  = ldr_atual > 2500          # acima da faixa ideal  -> mais alcalino

    # --- Prioridade 1: Solo seco sem previsao de chuva ---
    if solo_seco and not prev_chuva:
        return {
            "nivel":    "CRITICO",
            "mensagem": (
                f"Solo seco ({umidade_atual:.1f}%) e sem previsao de chuva. "
                "Iniciar ciclo de irrigacao imediatamente."
            ),
            "acao": "Ligar bomba agora",
        }

    # --- Prioridade 2: Solo seco mas chuva prevista ---
    if solo_seco and prev_chuva:
        return {
            "nivel":    "ALERTA",
            "mensagem": (
                f"Solo seco ({umidade_atual:.1f}%), porem ha previsao de chuva. "
                "Monitorar nas proximas horas antes de irrigar."
            ),
            "acao": "Aguardar chuva — monitorar",
        }

    # --- Prioridade 3: pH fora da faixa (solo acido) ---
    if ph_acido:
        return {
            "nivel":    "ATENCAO",
            "mensagem": (
                f"Leitura LDR {ldr_atual:.0f} indica solo acido (abaixo da faixa 1500-2500). "
                "Avaliar aplicacao de calcario ou corretivo de pH."
            ),
            "acao": "Aplicar corretivo de acidez",
        }

    # --- Prioridade 4: pH alcalino ---
    if ph_alcalino:
        return {
            "nivel":    "ATENCAO",
            "mensagem": (
                f"Leitura LDR {ldr_atual:.0f} indica solo alcalino (acima da faixa 1500-2500). "
                "Considerar aplicacao de enxofre ou adubo acidificante."
            ),
            "acao": "Verificar corretivo de alcalinidade",
        }

    # --- Cenario estavel ---
    return {
        "nivel":    "ESTAVEL",
        "mensagem": (
            f"Umidade adequada ({umidade_atual:.1f}%) e pH dentro da faixa ideal. "
            "Nenhuma acao imediata necessaria."
        ),
        "acao": "Sem acao necessaria",
    }


# ---------------------------------------------------------------------------
# Execucao standalone para teste rapido
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cenarios = [
        {"umidade_atual": 45.0, "ldr_atual": 1800, "prev_chuva": False},
        {"umidade_atual": 45.0, "ldr_atual": 1800, "prev_chuva": True},
        {"umidade_atual": 70.0, "ldr_atual": 900,  "prev_chuva": False},
        {"umidade_atual": 70.0, "ldr_atual": 3000, "prev_chuva": False},
        {"umidade_atual": 75.0, "ldr_atual": 2000, "prev_chuva": False},
    ]

    print("=== Teste de cenarios de irrigacao ===\n")
    for c in cenarios:
        resultado = avaliar_cenario_irrigacao(**c)
        print(f"Entrada : umidade={c['umidade_atual']}% | LDR={c['ldr_atual']} | chuva={c['prev_chuva']}")
        print(f"Nivel   : {resultado['nivel']}")
        print(f"Mensagem: {resultado['mensagem']}")
        print(f"Acao    : {resultado['acao']}")
        print()
