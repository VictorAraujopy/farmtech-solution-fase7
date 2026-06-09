# FarmTech Solutions — Fase 7 · Documentação da Fase 5 (Pessoa 3)

Esta parte do projeto cobre a **infraestrutura Cloud AWS**, o **servico de
mensageria** e a **seguranca da informacao**, integrados ao fluxo:

> **sensor critico / praga detectada → SNS → Lambda → e-mail equipe de campo**

## Estrutura da minha parte

```
farmtech_fase7/
└── fase5_cloud_aws/
    ├── alerta_sns.py        # publica no topico SNS (integrado com Fases 3 e 6)
    ├── lambda_alertas.py    # Lambda que processa SNS e envia e-mail via SES
    ├── infra_aws.md         # arquitetura completa dos servicos AWS
    ├── politica_seguranca.md # aplicacao ISO 27001/27002 ao projeto
    └── prints_aws/
        ├── sns_config.png   # topico SNS e subscription Lambda
        ├── lambda_config.png # trigger e variaveis de ambiente da Lambda
        ├── rds_setup.png    # instancia RDS com status Available
        └── ec2_instancia.png # instancia EC2 rodando a dashboard
```

---

## Fase 5 — Cloud AWS e Alertas

### Arquitetura

```
[ Sensor critico (Fase 3) ]  [ Praga detectada (Fase 6) ]
              │                           │
              └──────────┬────────────────┘
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
                         └──► [ CloudWatch ]  ──► auditoria
```

### `alerta_sns.py`

Publica alertas operacionais no topico SNS. Integrado diretamente com
as Fases 3 e 6 — e chamado pela dashboard (`pg_alertas.py`) e pelos
proprios modulos de sensor e visao computacional.

**Funcoes:**

- `notificar_equipe(mensagem, severidade)` → formata payload JSON e publica no SNS.
  Retorna o `MessageId` do SNS.

- `verificar_sensor_e_alertar(umidade, ldr, falta_n, falta_p, falta_k)` →
  avalia os dados do sensor IoT e dispara alerta automatico se necessario:

| Condicao | Severidade | Acao sugerida no e-mail |
|----------|------------|------------------------|
| Umidade < 30% | CRITICA | Acionar irrigacao imediatamente |
| Umidade entre 30-60% | ALTA | Iniciar ciclo de irrigacao |
| LDR < 1500 (solo acido) | MEDIA | Aplicar calcario |
| LDR > 2500 (solo alcalino) | MEDIA | Aplicar corretivo |
| Qualquer nutriente em falta | MEDIA | Aplicar fertilizante |

- `alertar_deteccao_yolo(arquivo, deteccoes)` → dispara alerta quando o YOLO
  detecta pragas ou doencas, incluindo nome da classe e confianca no e-mail.

### `lambda_alertas.py`

Funcao serverless acionada automaticamente pelo SNS. Processa o payload
e envia e-mail HTML formatado para a equipe de campo via Amazon SES.

**Variaveis de ambiente** (configuradas no painel da Lambda):

| Variavel | Descricao |
|----------|-----------|
| `EMAIL_REMETENTE` | Endereco verificado no SES (ex: alertas@farmtech.com) |
| `EMAIL_DESTINATARIO` | Equipe de campo (ex: equipe@farmtech.com) |
| `AWS_REGION_SES` | Regiao do SES (ex: us-east-1) |

O e-mail gerado e formatado em HTML com cor por severidade:
- 🔴 CRITICA — vermelho
- 🟠 ALTA — laranja
- 🟡 MEDIA — amarelo
- 🟢 BAIXA — verde

Todos os eventos sao registrados no CloudWatch Logs para auditoria.

### Como configurar na AWS

```
# 1. Topico SNS
SNS → Topics → Create topic → Standard → Nome: TopicoAlertasFarmTech

# 2. Funcao Lambda
Lambda → Create function → Python 3.12
Upload lambda_alertas.py → Handler: lambda_alertas.lambda_handler
Add trigger → SNS → selecionar TopicoAlertasFarmTech
Adicionar variaveis de ambiente: EMAIL_REMETENTE, EMAIL_DESTINATARIO, AWS_REGION_SES

# 3. Verificar e-mail no SES
SES → Verified identities → Create identity → Email address
Confirmar pelo link recebido no e-mail

# 4. Configurar credenciais locais
aws configure
# informar AccessKey com policy sns:Publish
```

### Como testar localmente

```bash
cd fase5_cloud_aws

# Testar alerta de sensor
python3 -c "
import alerta_sns
msg_id = alerta_sns.verificar_sensor_e_alertar(
    umidade=25.0, ldr=1800, falta_n=0, falta_p=0, falta_k=0
)
print('MessageId:', msg_id)
"

# Testar alerta de YOLO
python3 -c "
import alerta_sns
deteccoes = [{'nome': 'caterpillar', 'confianca': 0.87, 'classe_id': 0}]
msg_id = alerta_sns.alertar_deteccao_yolo('praga_soja_01.webp', deteccoes)
print('MessageId:', msg_id)
"
```

---

## Fluxo completo: sensor → e-mail

```
[crud_sensores] grava leitura
        │
        ▼
[alerta_sns] verifica_sensor_e_alertar()
        │ (se critico)
        ▼
[SNS Topic] publica payload JSON
        │
        ▼
[Lambda] lambda_handler() decodifica
        │
        ▼
[SES] envia e-mail HTML para equipe
        │
        ▼
[CloudWatch] registra execucao
```

---

## Decisoes tecnicas (resumo)

- **SES em vez de SNS SMS** — e-mail e mais adequado para alertas detalhados
  com instrucoes de acao corretiva; SMS seria melhor para notificacao critica
  simples, mas exige numero verificado e tem custo por mensagem.
- **Payload JSON no SNS** — permite que a Lambda extraia campos estruturados
  (severidade, detalhes, origem) sem parsing fragil de texto livre.
- **Variaveis de ambiente na Lambda** — e-mails configurados sem hardcode,
  facilitando troca de destinatario sem redeploy da funcao.
- **`verificar_sensor_e_alertar()` integrada ao `alerta_sns.py`** — a logica
  de decisao fica centralizada, evitando duplicacao entre a dashboard e
  possiveis chamadas diretas dos modulos de sensor.
- **Credenciais via `.env` + `python-dotenv`** — nunca expostas no codigo,
  alinhado com a politica de seguranca ISO 27002 secao 9.4.3.
