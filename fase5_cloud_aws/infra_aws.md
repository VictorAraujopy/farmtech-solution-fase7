# FarmTech Solutions — Infraestrutura AWS (Fase 5)

## Arquitetura Geral

```
[ ESP32 / Sensores Python ]
           │
           ▼
[ Banco SQLite / RDS PostgreSQL ]
           │
           ▼
[ Dashboard Streamlit (EC2) ] ──────────────────────────────┐
           │                                                 │
    (praga detectada                               (sensor critico
      pelo YOLO)                                   ou pH fora)
           │                                                 │
           └──────────────┬──────────────────────────────────┘
                          │
                    (boto3 publish)
                          │
                          ▼
                  [ Amazon SNS Topic ]
                  TopicoAlertasFarmTech
                          │
                    (subscription)
                          │
                          ▼
                  [ AWS Lambda ]
                  lambda_alertas.py
                          │
                          ├──► [ Amazon SES ] ──► e-mail equipe de campo
                          │
                          └──► [ CloudWatch Logs ] ──► auditoria
```

---

## Servicos Utilizados

### Amazon EC2
Instancia `t2.micro` (free tier) hospedando:
- Dashboard Streamlit (`streamlit run fase4_dashboard/app.py`)
- Scripts de backend das Fases 1, 3 e 6
- Sistema operacional: Ubuntu 22.04 LTS

### Amazon RDS
Instancia `db.t3.micro` PostgreSQL (substituicao do SQLite em producao):
- Database: `farmtech`
- Usuario: `farmtech_admin`
- Porta: 5432
- Backup automatico: 1 dia de retencao

### Amazon SNS
Topico do tipo **Standard** para mensageria assincrona:
- Nome: `TopicoAlertasFarmTech`
- Subscription: AWS Lambda
- Publisher: `alerta_sns.py` via Boto3

### AWS Lambda
Funcao serverless acionada pelo SNS:
- Runtime: Python 3.12
- Handler: `lambda_alertas.lambda_handler`
- Timeout: 30 segundos
- Variaveis de ambiente:
  - `EMAIL_REMETENTE`
  - `EMAIL_DESTINATARIO`
  - `AWS_REGION_SES`

### Amazon SES (Simple Email Service)
Servico de envio de e-mail:
- Remetente verificado: `alertas@farmtech.com`
- Destinatario: `equipe@farmtech.com`
- Formato: HTML + texto puro

### Amazon CloudWatch
Log e auditoria:
- LogGroup: `/aws/lambda/lambda_alertas`
- Retencao: 7 dias
- Metricas monitoradas: invocacoes, erros, duracao

---

## Fluxo Completo de um Alerta

1. Sensor IoT registra umidade < 60% ou YOLO detecta praga
2. `alerta_sns.py` formata payload JSON com severidade e detalhes
3. Boto3 publica no topico SNS via HTTPS/SSL
4. SNS aciona a Lambda automaticamente via subscription
5. Lambda decodifica o payload e chama `enviar_email_ses()`
6. SES envia e-mail HTML para a equipe de campo
7. CloudWatch registra toda a execucao para auditoria

---

## Setup na AWS Console

### 1. Criar o topico SNS
```
SNS → Topics → Create topic
  Type: Standard
  Name: TopicoAlertasFarmTech
```

### 2. Criar a funcao Lambda
```
Lambda → Create function
  Runtime: Python 3.12
  Handler: lambda_alertas.lambda_handler
  Upload: lambda_alertas.py
  Environment variables: EMAIL_REMETENTE, EMAIL_DESTINATARIO, AWS_REGION_SES
```

### 3. Conectar SNS → Lambda
```
SNS → TopicoAlertasFarmTech → Create subscription
  Protocol: AWS Lambda
  Endpoint: ARN da funcao lambda_alertas
```

### 4. Verificar e-mail no SES
```
SES → Verified identities → Create identity
  Type: Email address
  Email: alertas@farmtech.com  (confirmar pelo link recebido)
```

### 5. Configurar permissoes IAM
Policy minima para o usuario que roda o Boto3 local:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:us-east-1:SUA_CONTA:TopicoAlertasFarmTech"
    }
  ]
}
```

[INSERIR PRINT] `sns_config.png` — topico SNS criado com subscription Lambda ativa
[INSERIR PRINT] `lambda_config.png` — funcao Lambda com trigger SNS e variaveis de ambiente
[INSERIR PRINT] `rds_setup.png` — instancia RDS com status Available
[INSERIR PRINT] `ec2_instancia.png` — instancia EC2 rodando a dashboard
