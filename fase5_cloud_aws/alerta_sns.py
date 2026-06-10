"""
FarmTech Solutions - Fase 7 | Pessoa 3
alerta_sns.py - Publicacao de alertas no topico SNS da AWS.
"""

import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)

TOPICO_SNS_ARN = os.environ.get(
    "SNS_TOPIC_ARN",
    "arn:aws:sns:us-east-1:123456789012:TopicoAlertasFarmTech"
)


def _criar_cliente_sns():
    kwargs = {"region_name": os.environ.get("AWS_DEFAULT_REGION", "us-east-1")}
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key  = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if access_key and secret_key:
        kwargs["aws_access_key_id"]     = access_key
        kwargs["aws_secret_access_key"] = secret_key
    return boto3.client("sns", **kwargs)


def notificar_equipe(mensagem: str, severidade: str = "CRITICA") -> str:
    load_dotenv(override=True)
    cliente_sns = _criar_cliente_sns()
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


def verificar_sensor_e_alertar(umidade, ldr, falta_n, falta_p, falta_k):
    if umidade < 30:
        return notificar_equipe(f"URGENTE: Umidade {umidade:.1f}%. Acionar irrigacao imediatamente.", "CRITICA")
    if umidade < 60:
        return notificar_equipe(f"Umidade {umidade:.1f}% abaixo do limiar. Iniciar irrigacao.", "ALTA")
    if ldr < 1500:
        return notificar_equipe(f"LDR {ldr:.0f} indica solo acido. Aplicar calcario.", "MEDIA")
    if ldr > 2500:
        return notificar_equipe(f"LDR {ldr:.0f} indica solo alcalino. Verificar corretivo.", "MEDIA")
    nutrientes = [n for n, f in [("N", falta_n), ("P", falta_p), ("K", falta_k)] if f]
    if nutrientes:
        return notificar_equipe(f"Deficiencia de {', '.join(nutrientes)}. Aplicar fertilizante.", "MEDIA")
    return None


def alertar_deteccao_yolo(arquivo, deteccoes):
    if not deteccoes:
        return None
    resumo = ", ".join(f"{d['nome']} ({d['confianca']*100:.1f}%)" for d in deteccoes)
    return notificar_equipe(
        f"YOLO detectou anomalia em '{arquivo}': {resumo}. Inspecionar talhao.",
        "ALTA",
    )
