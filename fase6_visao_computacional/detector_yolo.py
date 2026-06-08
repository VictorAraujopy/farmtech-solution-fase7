"""
FarmTech Solutions - Fase 7 | Pessoa 2
detector_yolo.py - Carrega pesos do YOLOv8 e executa inferencia em imagens.

O modelo padrao e o YOLOv8 Nano (yolov8n.pt), baixado automaticamente
pela biblioteca ultralytics na primeira execucao.

Para usar pesos proprios treinados no dataset agricola, substitua o
arquivo em fase6_visao_computacional/modelos/yolo_farmtech.pt e passe
o caminho via 'inicializar_modelo(caminho_peso=...)'.
"""

from pathlib import Path
from ultralytics import YOLO

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
PASTA_ATUAL    = Path(__file__).resolve().parent
PASTA_MODELOS  = PASTA_ATUAL / "modelos"
MODELO_PADRAO  = PASTA_MODELOS / "yolov8n.pt"

# Confianca minima para aceitar uma deteccao (0.0 a 1.0)
CONFIANCA_MINIMA = 0.30


# ---------------------------------------------------------------------------
# Inicializacao
# ---------------------------------------------------------------------------

def inicializar_modelo(caminho_peso: str = str(MODELO_PADRAO)) -> YOLO:
    """
    Carrega o modelo YOLOv8 na memoria.

    Se o arquivo de pesos nao existir no caminho informado, a biblioteca
    ultralytics faz o download automatico do modelo publico correspondente.

    Args:
        caminho_peso: Caminho para o arquivo .pt dos pesos.
                      Padrao: modelos/yolov8n.pt (YOLOv8 Nano).

    Returns:
        Instancia do modelo YOLO pronta para inferencia.
    """
    PASTA_MODELOS.mkdir(parents=True, exist_ok=True)
    return YOLO(caminho_peso)


# ---------------------------------------------------------------------------
# Inferencia em imagem unica
# ---------------------------------------------------------------------------

def inferir_em_imagem(
    modelo: YOLO,
    img_path: str,
    confianca_min: float = CONFIANCA_MINIMA,
) -> list:
    """
    Executa deteccao de objetos em uma unica imagem.

    Args:
        modelo:        Modelo carregado por inicializar_modelo().
        img_path:      Caminho completo para o arquivo de imagem.
        confianca_min: Limiar minimo de confianca para incluir uma deteccao.
                       Deteccoes abaixo deste valor sao descartadas.

    Returns:
        Lista de dicionarios, um por objeto detectado:
            {
                'classe_id': int,   # indice da classe no modelo
                'nome':      str,   # nome legivel da classe
                'confianca': float  # probabilidade (0.0 a 1.0)
            }
        Lista vazia se nenhum objeto for detectado acima do limiar.
    """
    resultados = modelo(img_path, verbose=False)
    lista_deteccoes = []

    for result in resultados:
        for caixa in result.boxes:
            confianca = round(float(caixa.conf[0].item()), 3)

            # Filtra deteccoes com confianca abaixo do limiar
            if confianca < confianca_min:
                continue

            cls_id = int(caixa.cls[0].item())
            lista_deteccoes.append({
                "classe_id": cls_id,
                "nome":      modelo.names[cls_id],
                "confianca": confianca,
            })

    # Ordena por confianca decrescente (mais confiavel primeiro)
    lista_deteccoes.sort(key=lambda d: d["confianca"], reverse=True)
    return lista_deteccoes
