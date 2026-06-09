"""
FarmTech Solutions - Fase 7 | Pessoa 3
alerta_sns.py - Publicacao de alertas no topico SNS da AWS.

Integrado com:
  - Sensores IoT (Fase 3): dispara quando umidade critica ou pH fora da faixa
  - Visao Computacional (Fase 6): dispara quando YOLO detecta praga ou doenca

Configuracao necessaria:
  - aws configure (AccessKey com policy sns:Publish)
  - Substituir TOPICO_SNS_ARN pelo ARN provisionado na sua conta AWS
  - Ou definir a variavel de ambiente SNS_TOPIC_ARN no .env
"""

import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ARN do topico SNS — substitua pelo provisionado na sua conta AWS
# ou defina a variavel de ambiente SNS_TOPIC_ARN no arquivo .env
TOPICO_SNS_ARN = os.environ.get(
    "SNS_TOPIC_ARN",
    "arn:aws:sns:us-east-1:123456789012:TopicoAlertasFarmTech"
)


def notificar_equipe(mensagem: str, severidade: str = "CRITICA") -> str:
    """
    Publica um alerta operacional no topico SNS.

    Args:
        mensagem:   Descricao do incidente ou acao corretiva necessaria.
        severidade: Nivel do alerta — 'CRITICA', 'ALTA', 'MEDIA' ou 'BAIXA'.

    Returns:
        MessageId retornado pelo SNS, ou 'N/A' em caso de falha.
    """
    cliente_sns = boto3.client("sns", region_name="us-east-1")

    payload = {
        "origem":     "FarmTech Solutions",
        "severidade": severidade,
        "detalhes":   mensagem,
    }

    resposta = cliente_sns.publish(
        TopicArn=TOPICO_SNS_ARN,
        Message=json.dumps(payload, ensure_ascii=False),
        Subject="[FARMTECH] Alerta Operacional Automatico",
    )
    return resposta.get("MessageId", "N/A")


def verificar_sensor_e_alertar(umidade: float, ldr: float,
                                falta_n: int, falta_p: int, falta_k: int) -> str | None:
    """
    Avalia os dados do sensor IoT e dispara alerta SNS se necessario.

    Regras:
      - Umidade < 30%          → CRITICA  (irrigacao urgente)
      - Umidade entre 30-60%   → ALTA     (irrigacao necessaria)
      - LDR fora de 1500-2500  → MEDIA    (corretivo de pH)
      - Qualquer nutriente FALTA → MEDIA  (aplicar fertilizante)

    Args:
        umidade: Umidade do solo em % (0-100).
        ldr:     Leitura bruta do LDR (0-4095).
        falta_n: 1 se ha deficiencia de Nitrogenio.
        falta_p: 1 se ha deficiencia de Fosforo.
        falta_k: 1 se ha deficiencia de Potassio.

    Returns:
        MessageId do SNS se alerta foi disparado, None caso contrario.
    """
    if umidade < 30:
        return notificar_equipe(
            f"URGENTE: Umidade do solo em {umidade:.1f}%. "
            "Acionar irrigacao imediatamente e verificar sistema de bombeamento.",
            severidade="CRITICA",
        )

    if umidade < 60:
        return notificar_equipe(
            f"Umidade do solo em {umidade:.1f}% (abaixo do limiar de 60%). "
            "Iniciar ciclo de irrigacao no talhao afetado.",
            severidade="ALTA",
        )

    if ldr < 1500:
        return notificar_equipe(
            f"Sensor LDR registrou {ldr:.0f} (abaixo de 1500 — solo acido). "
            "Aplicar calcario ou corretivo de acidez no talhao.",
            severidade="MEDIA",
        )

    if ldr > 2500:
        return notificar_equipe(
            f"Sensor LDR registrou {ldr:.0f} (acima de 2500 — solo alcalino). "
            "Verificar necessidade de corretivo de alcalinidade.",
            severidade="MEDIA",
        )

    nutrientes_faltando = []
    if falta_n: nutrientes_faltando.append("Nitrogenio (N)")
    if falta_p: nutrientes_faltando.append("Fosforo (P)")
    if falta_k: nutrientes_faltando.append("Potassio (K)")

    if nutrientes_faltando:
        return notificar_equipe(
            f"Deficiencia de nutrientes detectada: {', '.join(nutrientes_faltando)}. "
            "Realizar aplicacao de fertilizante conforme laudo agronomico.",
            severidade="MEDIA",
        )

    return None


def alertar_deteccao_yolo(arquivo: str, deteccoes: list) -> str | None:
    """
    Dispara alerta SNS quando o YOLO detecta pragas ou doencas em imagens.

    Args:
        arquivo:   Nome do arquivo de imagem processado.
        deteccoes: Lista de deteccoes retornada por detector_yolo.inferir_em_imagem().
                   Cada item: {'nome': str, 'confianca': float, 'classe_id': int}

    Returns:
        MessageId do SNS se alerta foi disparado, None se nenhuma deteccao.
    """
    if not deteccoes:
        return None

    resumo = ", ".join(
        f"{d['nome']} ({d['confianca']*100:.1f}%)"
        for d in deteccoes
    )

    return notificar_equipe(
        f"Visao Computacional detectou anomalia na imagem '{arquivo}': {resumo}. "
        "Inspecionar o talhao correspondente e acionar equipe de manejo fitossanitario.",
        severidade="ALTA",
    )
