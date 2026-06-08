"""
FarmTech Solutions - Fase 7 | Pessoa 2
inferencia.py - Pipeline de processamento de lote de imagens com YOLOv8.

Varre uma pasta inteira de imagens, executa deteccao em cada uma
e retorna os resultados estruturados para exibicao na dashboard.
"""

from pathlib import Path
import detector_yolo

# Extensoes de imagem aceitas pelo pipeline
EXTENSOES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def processar_pasta_imagens(caminho_pasta: str) -> list:
    """
    Processa todas as imagens de um diretorio com o modelo YOLOv8.

    O modelo e inicializado uma unica vez e reutilizado para todas
    as imagens, evitando overhead de carregamento repetido.

    Args:
        caminho_pasta: Caminho para o diretorio contendo as imagens.

    Returns:
        Lista de dicionarios, um por imagem processada:
            {
                'arquivo':   str,   # nome do arquivo
                'deteccoes': list   # lista retornada por inferir_em_imagem()
            }
        Lista vazia se a pasta nao contiver imagens validas.

    Raises:
        FileNotFoundError: Se o caminho informado nao existir.
    """
    pasta = Path(caminho_pasta)

    if not pasta.exists():
        raise FileNotFoundError(f"Pasta nao encontrada: {caminho_pasta}")

    arquivos = sorted([
        f for f in pasta.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSOES_VALIDAS
    ])

    if not arquivos:
        return []

    # Inicializa o modelo uma unica vez para o lote inteiro
    modelo    = detector_yolo.inicializar_modelo()
    resultados = []

    for arquivo in arquivos:
        deteccoes = detector_yolo.inferir_em_imagem(modelo, str(arquivo))
        resultados.append({
            "arquivo":   arquivo.name,
            "deteccoes": deteccoes,
        })

    return resultados


def resumo_lote(resultados: list) -> dict:
    """
    Gera um resumo estatistico dos resultados de um lote processado.

    Args:
        resultados: Lista retornada por processar_pasta_imagens().

    Returns:
        Dicionario com:
            'total_imagens'    - quantidade de imagens processadas
            'imagens_com_alerta' - imagens com ao menos 1 deteccao
            'total_deteccoes'  - soma de todas as deteccoes
            'classes_encontradas' - set com os nomes de classes detectadas
    """
    total_deteccoes    = sum(len(r["deteccoes"]) for r in resultados)
    imagens_com_alerta = sum(1 for r in resultados if r["deteccoes"])
    classes            = {d["nome"] for r in resultados for d in r["deteccoes"]}

    return {
        "total_imagens":       len(resultados),
        "imagens_com_alerta":  imagens_com_alerta,
        "total_deteccoes":     total_deteccoes,
        "classes_encontradas": classes,
    }


# ---------------------------------------------------------------------------
# Execucao standalone
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Rode este modulo via Streamlit na interface da Fase 4.")
    print("Ou importe processar_pasta_imagens() em outro script Python.")
