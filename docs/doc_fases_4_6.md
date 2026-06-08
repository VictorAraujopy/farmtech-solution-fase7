# FarmTech Solutions — Fase 7 · Documentação das Fases 4 e 6 (Pessoa 2)

Esta parte do projeto cobre o **Dashboard Streamlit**, o **modelo de Machine Learning**
e a **Visão Computacional com YOLOv8**, integrados ao fluxo:

> **banco de dados → dashboard → ML / YOLO → alertas AWS**

## Estrutura da minha parte

```
farmtech_fase7/
├── fase4_dashboard/
│   ├── app.py                   # entry point Streamlit — hub central do projeto
│   ├── ml_modelo.py             # treino e predição com RandomForest (Scikit-Learn)
│   ├── visualizacoes.py         # gráficos interativos com Plotly Express
│   ├── predicoes_irrigacao.py   # sugestões automáticas de manejo
│   ├── requirements.txt         # dependências de todo o projeto
│   └── pages/
│       ├── pg_sensores.py       # aba dos dados IoT + ML (chama Fase 3)
│       ├── pg_visao_comp.py     # aba do YOLO (chama Fase 6)
│       └── pg_alertas.py        # aba dos alertas AWS (chama Fase 5)
└── fase6_visao_computacional/
    ├── detector_yolo.py         # carrega modelo e roda inferência em imagens
    ├── inferencia.py            # processa pasta de imagens, retorna classes + confiança
    ├── imagens_teste/           # imagens de lavoura para teste do pipeline
    └── modelos/                 # pesos treinados ou pré-treinados do YOLO
```

---

## Fase 4 — Dashboard Streamlit

### Como rodar

```bash
pip install -r fase4_dashboard/requirements.txt
streamlit run fase4_dashboard/app.py
```

### `app.py`

Entry point do Streamlit e hub central do projeto. Ajusta os `sys.path` para
importar módulos das Fases 1, 3 e 6, e expõe três ações rápidas na página principal:

- **Buscar Meteorologia** — chama `api_meteorologica.buscar_dados()` e `salvar_csv()` da Fase 1
- **Simular Leitura IoT** — chama `crud_sensores.gravar_leitura(talhao_id=1)` da Fase 3
- **Visão Computacional** — direciona o usuário para a aba `pg_visao_comp` no menu lateral

### `ml_modelo.py`

Treina um `RandomForestClassifier` (100 estimadores) para prever se a bomba de
irrigação deve ser acionada com base em leituras dos sensores.

**Features de entrada:**

| Feature | Tipo | Descrição |
|---------|------|-----------|
| `umidade` | float | Umidade do solo em % (0–100) |
| `ph_ldr` | int | Leitura bruta do sensor LDR (0–4095) |
| `falta_n` | int | Deficiência de Nitrogênio: 1=sim, 0=não |
| `falta_p` | int | Deficiência de Fósforo: 1=sim, 0=não |
| `falta_k` | int | Deficiência de Potássio: 1=sim, 0=não |

**Target:** `bomba_ligada` — 1=ligar, 0=não ligar

**Funções:**
- `gerar_dados_simulados(n_amostras)` → gera dataset sintético seguindo a mesma
  regra do `esp32_irrigacao.ino`, usado quando o banco ainda não tem leituras suficientes
- `treinar_modelo_irrigacao(df)` → treina, avalia (80/20) e imprime acurácia + relatório
- `prever_estado(modelo, novos_dados)` → retorna lista de predições para novos dados

**Split:** 80% treino / 20% teste, `random_state=42`

### `visualizacoes.py`

Gráficos interativos com Plotly Express consumidos pelas abas da dashboard:

- `plotar_evolucao_umidade(df)` → linha temporal de umidade com linha de referência
  em 60% (limiar de irrigação)
- `plotar_status_bomba(df)` → pizza de frequência de acionamento (`LIGADA`/`DESLIGADA`)
- `plotar_ph_ldr(df)` → linha temporal da leitura LDR com faixa ideal (1500–2500) destacada
- `plotar_npk(df)` → barras empilhadas de ocorrências de deficiência de N, P e K

### `predicoes_irrigacao.py`

Gera recomendação de manejo cruzando umidade, leitura do LDR e previsão de chuva.

**Nota técnica:** o parâmetro `ldr_atual` representa a leitura bruta do sensor LDR
(escala 0–4095), alinhado com `sensor_ldr_ph.py` da Fase 3. A faixa de pH adequado
corresponde a LDR entre 1500 e 2500.

| Condição | Nível | Ação sugerida |
|----------|-------|---------------|
| Umidade < 60% e sem chuva prevista | CRÍTICO | Ligar bomba agora |
| Umidade < 60% e com chuva prevista | ALERTA | Aguardar — monitorar |
| LDR < 1500 (solo ácido) | ATENÇÃO | Aplicar corretivo de acidez |
| LDR > 2500 (solo alcalino) | ATENÇÃO | Verificar corretivo de alcalinidade |
| Demais casos | ESTÁVEL | Sem ação necessária |

Retorna dicionário com `nivel`, `mensagem` e `acao`.

### `pages/pg_sensores.py`

Aba de análise dos sensores IoT. Consome as últimas 30 leituras do banco via
`crud_sensores.listar_leituras(limite=30)` e exibe:

- Tabela de leituras brutas (expansível)
- Quatro gráficos: umidade, status da bomba, LDR e deficiências NPK
- Recomendação de manejo em tempo real com toggle de previsão de chuva
- Botão para treinar o modelo ML e predizer o estado da bomba com a última leitura

### `pages/pg_visao_comp.py`

Aba de visão computacional. Oferece dois modos:

1. **Lote** — varre `fase6_visao_computacional/imagens_teste/` e processa todas as imagens
2. **Upload avulso** — usuário envia uma imagem diretamente pela interface para análise instantânea

Exibe para cada imagem: classes detectadas, confiança em % e quantidade de objetos.

### `pages/pg_alertas.py`

Aba de alertas AWS. Permite disparar mensagens manuais no tópico SNS com:

- Seletor de severidade: `CRÍTICA`, `ALTA`, `MÉDIA`, `BAIXA`
- Seletor de origem: Sensor IoT, YOLO, Operador Manual ou Sistema
- Preview do payload JSON antes do envio
- Feedback com `MessageID` retornado pelo SNS

---

## Fase 6 — Visão Computacional (YOLOv8)

### `detector_yolo.py`

Carrega o modelo YOLOv8 Nano (`yolov8n.pt`) e executa detecção em uma imagem.
Os pesos são baixados automaticamente pela biblioteca `ultralytics` na primeira execução.

**Funções:**
- `inicializar_modelo(caminho_peso)` → carrega e retorna instância `YOLO`
- `inferir_em_imagem(modelo, img_path, confianca_min=0.30)` → retorna lista de detecções,
  cada uma com `classe_id`, `nome` e `confianca`, filtradas pelo limiar mínimo e
  ordenadas por confiança decrescente

Para usar pesos próprios treinados no dataset agrícola, substitua o arquivo em
`fase6_visao_computacional/modelos/yolo_farmtech.pt`.

### `inferencia.py`

Processa um diretório inteiro de imagens de forma otimizada: o modelo é inicializado
uma única vez e reutilizado para todo o lote.

**Funções:**
- `processar_pasta_imagens(caminho_pasta)` → varre a pasta, processa cada imagem
  e retorna lista de dicionários `{arquivo, deteccoes}`
- `resumo_lote(resultados)` → retorna estatísticas do lote: total de imagens,
  imagens com alerta, total de detecções e conjunto de classes encontradas

**Extensões aceitas:** `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`

### Como rodar a Fase 6

Coloque imagens em `fase6_visao_computacional/imagens_teste/` e acesse a aba
**Visão Computacional** na dashboard, ou teste direto:

```bash
# Teste via dashboard (recomendado)
streamlit run fase4_dashboard/app.py

# Teste standalone do detector
cd fase6_visao_computacional
python3 detector_yolo.py
```

---

## Fluxo completo: banco → dashboard → ML / YOLO

```
[farmtech.db] leituras_sensores
        │
        ▼
[pg_sensores] exibe tabela + gráficos
        │
        ├──► [ml_modelo] treina RandomForest → prediz estado da bomba
        │
        └──► [predicoes_irrigacao] regras agronômicas → recomendação de manejo

[imagens_teste/] ou upload do usuário
        │
        ▼
[detector_yolo] YOLOv8 → bounding boxes
        │
        ▼
[pg_visao_comp] exibe classes e confiança
        │
        ▼ (se praga detectada)
[pg_alertas] dispara SNS → Lambda (Fase 5)
```

---

## Resumo: rodar tudo do zero

```bash
# 1) instalar dependências
pip install -r fase4_dashboard/requirements.txt

# 2) garantir que o banco existe (Fase 2) e tem leituras (Fase 3)
cd fase2_banco_dados && python3 conexao_db.py && cd ..
cd fase3_iot && python3 crud_sensores.py && cd ..

# 3) subir a dashboard
streamlit run fase4_dashboard/app.py
```

## Decisões técnicas (resumo)

- **`gerar_dados_simulados()`** — garante que o modelo ML pode ser treinado e demonstrado
  mesmo sem leituras no banco, usando a mesma lógica do `esp32_irrigacao.ino` como ground truth.
- **YOLOv8 Nano** — modelo mais leve da família YOLOv8, adequado para rodar localmente
  sem GPU; pesos baixados automaticamente na primeira execução.
- **Dois modos no YOLO** — lote automático para uso em produção, upload avulso para
  demonstração rápida na apresentação.
- **`ldr_atual` em vez de `ph_atual`** — nomenclatura alinhada com a Fase 3,
  evitando confusão entre a leitura bruta do LDR (0–4095) e o pH real (0–14).
- **`python-dotenv`** no `requirements.txt` — permite carregar credenciais AWS do
  `.env` sem expor no código.
