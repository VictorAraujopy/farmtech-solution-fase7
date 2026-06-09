# FarmTech Solutions — Política de Segurança (Fase 5)
## Aplicação das normas ISO 27001 e ISO 27002

---

## 1. Principio do Minimo Privilegio (ISO 27002 — 9.2.3)

O agente Boto3 que publica alertas no SNS opera com um usuario IAM isolado,
cuja policy concede **exclusivamente** a permissao `sns:Publish` apontando
para o ARN exato do topico `TopicoAlertasFarmTech`.

Beneficios:
- Em caso de vazamento da credencial, o atacante so consegue publicar
  mensagens naquele topico especifico — sem acesso a nenhum outro recurso AWS
- Previne escalada de privilegios (privilege escalation)
- Auditavel via CloudTrail: cada publicacao fica registrada com o IAM user

```json
{
  "Effect": "Allow",
  "Action": "sns:Publish",
  "Resource": "arn:aws:sns:us-east-1:CONTA:TopicoAlertasFarmTech"
}
```

[INSERIR PRINT] `iam_policy.png` — policy IAM mostrando restricao ao ARN exato

---

## 2. Criptografia em Transito (ISO 27002 — 10.1.1)

Todas as comunicacoes entre o sistema local e os endpoints AWS
(SNS, SES, Lambda) ocorrem nativamente via **TLS 1.2+**, garantido
pelo SDK Boto3 por padrao.

Protecoes ativas:
- **Confidencialidade**: dados dos sensores e alertas nao podem ser
  interceptados em transito (sniffing na rede rural da fazenda)
- **Integridade**: qualquer adulteracao do pacote invalida a conexao TLS
- **Autenticidade**: certificados AWS validam a identidade do endpoint,
  prevenindo ataques MITM (Man-in-the-Middle)

Nenhuma configuracao adicional e necessaria — o Boto3 recusa conexoes
sem TLS por padrao.

---

## 3. Log e Auditoria (ISO 27001 — A.12.4.1)

A AWS Lambda registra automaticamente toda execucao no **Amazon CloudWatch Logs**:

| O que e registrado | Para que serve |
|--------------------|----------------|
| Timestamp de cada invocacao | Rastrear quando o alerta foi processado |
| Severidade e detalhes do payload | Evidencia do incidente para auditoria |
| Sucesso ou falha do envio SES | Identificar falhas de notificacao |
| Erros de decodificacao JSON | Detectar mensagens malformadas ou ataques |

O LogGroup `/aws/lambda/lambda_alertas` tem retencao de 7 dias,
suficiente para analise forense de incidentes recentes.

[INSERIR PRINT] `cloudwatch_logs.png` — LogGroup com registros de execucao da Lambda

---

## 4. Gestao de Credenciais (ISO 27002 — 9.4.3)

As credenciais AWS nunca aparecem no codigo-fonte:

- Armazenadas localmente em `~/.aws/credentials` (configurado via `aws configure`)
- Variaveis sensiveis do projeto em `.env` (listado no `.gitignore`)
- `.env.example` com valores placeholder commitado no repositorio

```
# .env (NUNCA commitar)
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:SUA_CONTA:TopicoAlertasFarmTech
EMAIL_REMETENTE=alertas@farmtech.com
EMAIL_DESTINATARIO=equipe@farmtech.com

# .env.example (commitar)
SNS_TOPIC_ARN=SUBSTITUIR
EMAIL_REMETENTE=SUBSTITUIR
EMAIL_DESTINATARIO=SUBSTITUIR
```

---

## 5. Disponibilidade e Resiliencia (ISO 27001 — A.17.1.1)

| Servico | SLA AWS | Estrategia adotada |
|---------|---------|-------------------|
| SNS | 99.9% | Topico Standard com retry automatico |
| Lambda | 99.95% | Serverless — sem servidor para gerenciar |
| SES | 99.9% | Reenvio automatico em caso de falha temporaria |
| RDS | 99.95% | Backup automatico diario |

Em caso de falha no envio do e-mail, a Lambda registra o erro no
CloudWatch e retorna `statusCode 207`, permitindo reprocessamento.
