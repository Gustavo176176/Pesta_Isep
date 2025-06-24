#include <Wire.h>         //I2C
#include <MFRC522_I2C.h>  //Ler RFID
#include <SPI.h>          //Comunicação Ethernet
#include <ETH.h>
#include <M5_Ethernet.h>  //Hardware
#include "M5PoECAM.h"     //Dispostivio POECAM
#include <ArduinoHttpClient.h> //HTTP
#include <EthernetClient.h> 

#define SDA_PIN 25   // SDA do RFID
#define SCL_PIN 33   // SCL do RFID
#define RST_PIN -1   // RST Pin do RFID ->apenas para evitar erros
#define reedPin 3    // Reed switch no G3

MFRC522_I2C mfrc522(0x28, RST_PIN, &Wire);    //Barramento I2C para a leitura dos cartões
int estadoAnterior = HIGH;                    //Armário inicialmente assume como fechado


byte mac[] = { 0x2E, 0xBC, 0xBB, 0x82, 0x41, 0xB0 };
const char* serverName ="192.168.1.128";

int serverPort = 8000;

int ultimoAcessoAutorizado = -1;
EthernetClient c;
HttpClient client = HttpClient(c, serverName, serverPort);


void setup() 
{
  pinMode(reedPin, INPUT_PULLUP);   //lê o estado da porta aberto/fechado
  Serial.begin(9600);
  while (!Serial);

  Wire.begin(SDA_PIN, SCL_PIN);
  delay(100);
  mfrc522.PCD_Init();
 
  SPI.begin(M5_POE_CAM_ETH_CLK_PIN, M5_POE_CAM_ETH_MISO_PIN, M5_POE_CAM_ETH_MOSI_PIN, -1);
  Ethernet.init(M5_POE_CAM_ETH_CS_PIN);

  if (Ethernet.begin(mac) == 0) 
  {
    Serial.println("Falha ao obter IP via DHCP. Verifique o cabo ou servidor DHCP.");
  } 
  else
  {
    Serial.print("IP obtido via DHCP: ");
    Serial.println(Ethernet.localIP());
  }

}

void loop()
{
  int estadoAtual = digitalRead(reedPin);   //lê continuadamente o estado da porta
  String rfid_uid = "";                     //string para armazenar o UID lido
  String response = "";                     //string para guardar a resposta da API

  if (estadoAtual != estadoAnterior)        //se for diferente,foi aberto
  {
    if (estadoAtual == HIGH) 
    {
      Serial.println("Armário Aberto");
      response = sendPostRequestEstadoPorta("aberto_a_espera");
      delay(1000);

      Serial.println("Passe o cartão");

      unsigned long tempoInicio = millis(); //tempo inicial
      bool cartaoLido = false;

      while (millis() - tempoInicio < 10000)  //10 segundos para o utilizador passar o cartão
      {
        if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) 
        {
          Serial.print("UID: ");
          for (byte i = 0; i < mfrc522.uid.size; i++) 
          {
            if (mfrc522.uid.uidByte[i] < 0x10) Serial.print("0");
            rfid_uid += String(mfrc522.uid.uidByte[i], HEX);  //converte para hexadecimal
            Serial.print(mfrc522.uid.uidByte[i], HEX);
            Serial.print(" ");
          }
          Serial.println();
          mfrc522.PICC_HaltA();  
          mfrc522.PCD_StopCrypto1();
          cartaoLido = true;
          break;
        }
        
      }
      if (!cartaoLido) 
      {
        Serial.println("Tempo expirado!");      //Passou 10 segundos e não foi lido o cartão do utilizador
        sendPostRequestAcessos("TEMPO_EXPIRADO");
         ultimoAcessoAutorizado == 0;
         
      } 

      else 
      {
        Serial.println("Iniciando requisição POST...");
        response = sendPostRequestAcessos(rfid_uid);  
        if (response.indexOf("\"acesso\":1") != -1)
        {
          Serial.println("Acesso autorizado e registado.");
          ultimoAcessoAutorizado = 1;
          response = sendPostRequestEstadoPorta("aberto_autorizado");

        } 
        else if (response.indexOf("\"acesso\":0") != -1) 
        {
          Serial.println("Acesso não autorizado.");
          ultimoAcessoAutorizado = 0;
        }
        else 
        {
          Serial.print("Erro ao enviar requisição POST: ");
        }

      }
    } 
    else 
    {
      Serial.println("Armário Fechado");
      if (ultimoAcessoAutorizado == 1) 
      {
        response = sendPostRequestEstadoPorta("fecho_permitido");
      }
      else 
      {
        response = sendPostRequestEstadoPorta("fecho_negado");
      }
    ultimoAcessoAutorizado = -1; 
    } 

    estadoAnterior = estadoAtual;
  }
  delay(4000); 
}




//Envio do UID 
String sendPostRequestAcessos(String rfid_uid) 
{
  const char* URLPath = "/acessos";
  String body = rfid_uid;
  
  Serial.print("Enviando: ");
  Serial.println(body);

  client.post(URLPath, "text/plain", body);

  int httpResponseCode = client.responseStatusCode();

  Serial.print("Código de resposta HTTP: ");
  Serial.println(httpResponseCode);

  if (httpResponseCode > 0) 
  {
    String response = client.responseBody();
    Serial.println("Resposta da API:");
    Serial.println(response);
    return response;
  }
  return "";
}


//Estado da porta
String sendPostRequestEstadoPorta(String estado) 
{
  const char* URLPath = "/estado-porta";
  String body = estado;
  
  Serial.print("Enviando: ");
  Serial.println(body);

  client.post(URLPath, "text/plain", body);

  int httpResponseCode = client.responseStatusCode();

  Serial.print("Código de resposta HTTP: ");
  Serial.println(httpResponseCode);

  if (httpResponseCode > 0) 
  {
    String response = client.responseBody();
    Serial.println("Resposta da API:");
    Serial.println(response);
    return response;
  }
  return "";
}