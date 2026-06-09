"""
FarmTech Solutions - Fase 7 | Pessoa 3
lambda_alertas.py - AWS Lambda que processa eventos SNS e envia e-mail via SES.

Fluxo:
  SNS Topic → trigger → Lambda → SES (e-mail para equipe de campo)

Variaveis de ambiente necessarias na Lambda (AWS Console → Configuration → Env vars):
  EMAIL_REMETENTE   ex: alertas@farmtech.com  (verificado no SES)
  EMAIL_DESTINATARIO ex: equipe@farmtech.com
  AWS_REGION_SES    ex: us-east-1
"""

import json
import logging
import os
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Variaveis de ambiente configuradas no painel da Lambda
EMAIL_REMETENTE    = os.environ.get("EMAIL_REMETENTE",    "alertas@farmtech.com")
EMAIL_DESTINATARIO = os.environ.get("EMAIL_DESTINATARIO", "equipe@farmtech.com")
REGIAO_SES         = os.environ.get("AWS_REGION_SES",     "us-east-1")


def enviar_email_ses(severidade: str, detalhes: str) -> bool:
    """
    Envia e-mail de alerta para a equipe de campo via Amazon SES.

    Args:
        severidade: Nivel do alerta (CRITICA, ALTA, MEDIA, BAIXA).
        detalhes:   Descricao do incidente e acao corretiva.

    Returns:
        True se e-mail enviado com sucesso, False caso contrario.
    """
    cliente_ses = boto3.client("ses", region_name=REGIAO_SES)

    # Cores por severidade para o corpo HTML do e-mail
    cores = {
        "CRITICA": "#c0392b",
        "ALTA":    "#e67e22",
        "MEDIA":   "#f39c12",
        "BAIXA":   "#27ae60",
    }
    cor = cores.get(severidade, "#2c3e50")

    assunto = f"[FARMTECH] Alerta {severidade} — Acao Necessaria"

    corpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; 
                    border-radius: 8px; padding: 30px; border-top: 6px solid {cor};">
            <h2 style="color: {cor};">🌱 FarmTech Solutions — Alerta Operacional</h2>
            <hr>
            <p><strong>Severidade:</strong>
                <span style="color: {cor}; font-weight: bold;">{severidade}</span>
            </p>
            <p><strong>Detalhes do incidente:</strong></p>
            <div style="background: #f9f9f9; border-left: 4px solid {cor}; 
                        padding: 12px; border-radius: 4px;">
                {detalhes}
            </div>
            <hr>
            <p style="color: #888; font-size: 12px;">
                Este e-mail foi gerado automaticamente pelo sistema FarmTech Solutions.<br>
                Nao responda a este e-mail.
            </p>
        </div>
    </body>
    </html>
    """

    corpo_texto = f"[FARMTECH] Alerta {severidade}\n\n{detalhes}\n\nMensagem automatica."

    try:
        cliente_ses.send_email(
            Source=EMAIL_REMETENTE,
            Destination={"ToAddresses": [EMAIL_DESTINATARIO]},
            Message={
                "Subject": {"Data": assunto, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": corpo_texto, "Charset": "UTF-8"},
                    "Html": {"Data": corpo_html,  "Charset": "UTF-8"},
                },
            },
        )
        logger.info(f"E-mail enviado para {EMAIL_DESTINATARIO} — severidade {severidade}")
        return True

    except ClientError as e:
        logger.error(f"Erro ao enviar e-mail via SES: {e.response['Error']['Message']}")
        return False


def lambda_handler(event, context):
    """
    Entry point padrao para execucao Serverless no ambiente AWS Lambda.

    Escuta o topico SNS, processa o payload de alerta e envia e-mail
    via Amazon SES para a equipe de campo da fazenda.

    Args:
        event:   Evento SNS com lista de Records.
        context: Contexto de execucao da Lambda (fornecido pela AWS).

    Returns:
        Dict com statusCode e mensagem de resultado.
    """
    logger.info("Lambda acionada via SNS!")
    emails_enviados = 0
    erros = 0

    for record in event.get("Records", []):
        try:
            mensagem_raw  = record["Sns"]["Message"]
            payload       = json.loads(mensagem_raw)

            severidade = payload.get("severidade", "INDEFINIDO")
            detalhes   = payload.get("detalhes",   "Sem detalhes.")
            origem     = payload.get("origem",      "FarmTech Solutions")

            logger.info(f"Processando alerta [{severidade}] de '{origem}': {detalhes}")

            sucesso = enviar_email_ses(severidade, detalhes)

            if sucesso:
                emails_enviados += 1
            else:
                erros += 1

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar payload SNS: {e}")
            erros += 1
        except KeyError as e:
            logger.error(f"Campo ausente no evento SNS: {e}")
            erros += 1

    resultado = (
        f"{emails_enviados} e-mail(s) enviado(s) com sucesso. "
        f"{erros} erro(s)."
    )
    logger.info(resultado)

    return {
        "statusCode": 200 if erros == 0 else 207,
        "body": resultado,
    }
