#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <Keypad.h>
#include <LiquidCrystal.h>
#include <ArduinoJson.h>

// Configurazione WiFi
const char* ssid = "Memoli_WiFi";
const char* password = "Salvataaggioo";
const char* serverURL = "https://192.168.178.40:8000/blockchain/receive-data/";

// Certificato Root 
const char* root_ca = R"EOF(
-----BEGIN CERTIFICATE-----
MIID7zCCAtegAwIBAgIUC4lpYOqUViHuOhLPkNMRcxbMoOYwDQYJKoZIhvcNAQEL
BQAwgYYxCzAJBgNVBAYTAklUMQ4wDAYDVQQIDAVJdGFseTEPMA0GA1UEBwwGTmFw
bGVzMRMwEQYDVQQKDApEeW5hbWljRHVvMRIwEAYDVQQDDAlGcmFuY2VzY28xLTAr
BgkqhkiG9w0BCQEWHmYuZ2Fyb2ZhbG8xOUBzdHVkZW50aS51bmlzYS5pdDAeFw0y
NDEyMTQxMDU2MTVaFw0yNTEyMTQxMDU2MTVaMIGGMQswCQYDVQQGEwJJVDEOMAwG
A1UECAwFSXRhbHkxDzANBgNVBAcMBk5hcGxlczETMBEGA1UECgwKRHluYW1pY0R1
bzESMBAGA1UEAwwJRnJhbmNlc2NvMS0wKwYJKoZIhvcNAQkBFh5mLmdhcm9mYWxv
MTlAc3R1ZGVudGkudW5pc2EuaXQwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEK
...
-----END CERTIFICATE-----
)EOF";

// Configurazione Tastierino e Display LCD
const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};
byte rowPins[ROWS] = {26, 25, 33, 32};
byte colPins[COLS] = {14, 27, 12, 13};
const int buzzerPin = 5;
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);
LiquidCrystal lcd(15, 4, 16, 17, 18, 19);
String enteredCode = "";

void setup() {
  Serial.begin(115200);
  lcd.begin(16, 2);
  lcd.print("Inserire codice:");
  pinMode(buzzerPin, OUTPUT);

  // Connessione WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connessione al WiFi...");
    lcd.setCursor(0, 1);
    lcd.print("Connessione...");
  }

  Serial.println("WiFi Connesso!");
  lcd.clear();
  lcd.print("Connesso!");
  delay(2000);
  lcd.clear();
  lcd.print("Inserire codice:");
}

void loop() {
  char key = keypad.getKey();
  if (key) {
    buzz();
    if (key == '#') {
      if (enteredCode.length() == 6) {
        sendAccessRequest(enteredCode);
      } else {
        lcd.clear();
        lcd.print("Codice errato");
        delay(2000);
        lcd.clear();
        lcd.print("Inserire codice:");
      }
      enteredCode = "";
    } else if (key == '*') {
      enteredCode = "";
      lcd.clear();
      lcd.print("Inserire codice:");
    } else {
      enteredCode += key;
      lcd.clear();
      lcd.print("Codice: ");
      lcd.print(enteredCode);
    }
  }
}

#include <ArduinoJson.h>  // Libreria per il parsing JSON (assicurati di installarla)

void sendAccessRequest(String code) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure();  

    Serial.println("[DEBUG] Creazione connessione HTTPS...");

    HTTPClient https;
    if (!https.begin(client, serverURL)) {  
      Serial.println("[ERROR] Errore nell'inizializzazione della richiesta HTTPS!");
      return;
    }

    https.addHeader("Content-Type", "application/json");

    String payload = "{\"code\": \"" + code + "\"}";
    Serial.print("[DEBUG] Invio JSON: ");
    Serial.println(payload);

    int httpResponseCode = https.POST(payload);

    Serial.print("[DEBUG] Codice Risposta HTTP: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
      String response = https.getString();
      Serial.print("[DEBUG] Risposta Server: ");
      Serial.println(response);

      //  Usa ArduinoJson per analizzare la risposta
      DynamicJsonDocument doc(1024);
      DeserializationError error = deserializeJson(doc, response);

      if (error) {
        Serial.println("[ERROR] Errore nel parsing JSON!");
        lcd.clear();
        lcd.print("Errore JSON");
        delay(3000);
      } else {
        bool isValid = doc["is_valid"]; //  Estrai "is_valid" dal JSON
        Serial.print("[DEBUG] is_valid: ");
        Serial.println(isValid);

        lcd.clear();
        if (isValid) {
          lcd.print("Codice corretto");
        } else {
          lcd.print("Codice errato");
        }
        delay(3000);
      }
    } else {
      Serial.print("[ERROR] HTTP FALLITO, codice errore: ");
      Serial.println(httpResponseCode);
      lcd.clear();
      lcd.print("Errore server");
      delay(3000);
    }

    lcd.clear();
    lcd.print("Inserire codice:");
    https.end();
  } else {
    Serial.println("[ERROR] WiFi non connesso!");
    lcd.clear();
    lcd.print("WiFi assente!");
    delay(3000);
    lcd.clear();
    lcd.print("Inserire codice:");
  }
}


void buzz() {
  digitalWrite(buzzerPin, HIGH);
  delay(200);
  digitalWrite(buzzerPin, LOW);
}
