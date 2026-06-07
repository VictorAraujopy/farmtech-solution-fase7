# ============================================================
# FarmTech Solutions - Fase 7 | Pessoa 1
# analise_r.R - Analise estatistica dos dados meteorologicos.
#
# Le o dados_meteorologicos.csv (gerado por api_meteorologica.py) e
# calcula media, desvio padrao, minimo e maximo de cada variavel.
# Usa apenas R base - nao precisa instalar pacotes.
# Rodar:  Rscript analise_r.R
# ============================================================

# Localiza o CSV na mesma pasta deste script (funciona via Rscript)
args <- commandArgs(trailingOnly = FALSE)
arq_script <- sub("--file=", "", args[grep("--file=", args)])
pasta <- if (length(arq_script) > 0) dirname(normalizePath(arq_script)) else getwd()
csv <- file.path(pasta, "dados_meteorologicos.csv")

dados <- read.csv(csv, stringsAsFactors = FALSE)

# Mantem apenas as colunas numericas para o resumo estatistico
num <- dados[sapply(dados, is.numeric)]

resumo <- data.frame(
  variavel = names(num),
  media    = sapply(num, mean),
  desvio   = sapply(num, sd),
  minimo   = sapply(num, min),
  maximo   = sapply(num, max),
  row.names = NULL
)

cat("=== Analise estatistica - dados meteorologicos ===\n")
cat("Total de leituras:", nrow(dados), "\n\n")
print(resumo, digits = 4)

# Leitura agronomica simples a partir da umidade media
umid_media <- mean(dados$umidade_pct)
cat("\nUmidade relativa media:", round(umid_media, 1), "%\n")
if (umid_media < 60) {
  cat(">> Umidade baixa: atencao redobrada com a irrigacao.\n")
} else {
  cat(">> Umidade em faixa confortavel para a maioria das culturas.\n")
}
