// ==========================================================
// CÓDIGO FINALÍSSIMO - AGORA VAI
// Peço desculpas pela confusão. Este código bate 100% com a sua imagem.
// ==========================================================

// PARTE 1: INCLUIR BIBLIOTECAS E DEFINIR PINOS E VARIÁVEIS
#include "DHT.h"

// --- Definição dos Pinos (CONFORME A SUA IMAGEM COM ZOOM) ---
#define DHT_PIN 15      // Pino de dados do sensor DHT22
#define LDR_PIN 34      // Pino do sensor de luz (LDR)
#define BOTAO_N_PIN 21  // Pino do botão N
#define BOTAO_P_PIN 22  // Pino do botão P
#define BOTAO_K_PIN 23  // Pino do botão K
#define BOMBA_PIN 4     // Pino que aciona o relé da bomba

// --- Criação dos Objetos ---
DHT dht(DHT_PIN, DHT22);


// PARTE 2: FUNÇÕES AUXILIARES
void controlarBomba(bool ligar) {
  if (ligar) {
    digitalWrite(BOMBA_PIN, HIGH); // Liga o relé
    Serial.println(">> A BOMBA FOI LIGADA! <<");
  } else {
    digitalWrite(BOMBA_PIN, LOW);  // Desliga o relé
    Serial.println(">> A BOMBA FOI DESLIGADA! <<");
  }
}

// PARTE 3: SETUP - RODA APENAS UMA VEZ
void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(BOTAO_N_PIN, INPUT_PULLUP);
  pinMode(BOTAO_P_PIN, INPUT_PULLUP);
  pinMode(BOTAO_K_PIN, INPUT_PULLUP);

  pinMode(BOMBA_PIN, OUTPUT);
  digitalWrite(BOMBA_PIN, LOW); // Garante que a bomba comece desligada
}


// PARTE 4: LOOP - O CÓDIGO PRINCIPAL QUE FICA REPETINDO
void loop() {
  // --- Leitura de todos os sensores ---
  float umidade = dht.readHumidity();
  int nivelPH = analogRead(LDR_PIN);
  bool n_pressionado = !digitalRead(BOTAO_N_PIN);
  bool p_pressionado = !digitalRead(BOTAO_P_PIN);
  bool k_pressionado = !digitalRead(BOTAO_K_PIN);

  // --- Exibição dos dados brutos no Monitor Serial ---
  Serial.println("==========================================");
  Serial.println("Monitor Serial de Dados:");
  
  if (umidade >= 0) {
    Serial.print("Umidade do Solo (DHT22): ");
    Serial.print(umidade);
    Serial.println(" %");
  } else {
    Serial.println("Umidade do Solo (DHT22): Falha na leitura!");
  }

  Serial.print("Nível de pH (LDR - 0 a 4095): ");
  Serial.println(nivelPH);

  Serial.println("Status dos Nutrientes:");
  Serial.print("N: "); Serial.print(n_pressionado ? "SIM" : "NAO");
  Serial.print(" | P: "); Serial.print(p_pressionado ? "SIM" : "NAO");
  Serial.print(" | K: "); Serial.println(k_pressionado ? "SIM" : "NAO");

  // --- LÓGICA DE DECISÃO INTELIGENTE E COMBINADA ---
  const int UMIDADE_MINIMA = 60;
  const int PH_MINIMO_LDR = 1500;
  const int PH_MAXIMO_LDR = 2500;

  Serial.println("---------- Análise e Ações ----------");

  // A bomba SÓ LIGA se TODAS as 5 condições a seguir forem verdadeiras
  if ( (umidade < UMIDADE_MINIMA && umidade >= 0) &&                
       (nivelPH >= PH_MINIMO_LDR && nivelPH <= PH_MAXIMO_LDR) &&    
       (!n_pressionado) &&                                         
       (!p_pressionado) &&
       (!k_pressionado) ) {                                         

      Serial.println("STATUS: Condições ideais. Acionando a irrigação.");
      controlarBomba(true);

  } else {
      Serial.println("STATUS: Irrigação não necessária ou condição do solo inadequada.");
      controlarBomba(false);
  }

  Serial.println("==========================================");
  delay(2000);
}