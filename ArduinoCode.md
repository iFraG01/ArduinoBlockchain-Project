#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <Keypad.h>
#include <LiquidCrystal.h>


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
AoIBAQCgePIxqDgUm7htuWv59VUn34vy2zN88Yl/cxVoXX2ITPG1DdlLUsxo0sLo
N60ayZpLhv++Te7updbqpyn7aILtmD9XNaCyG3z9clJ+Nbl4OTzxHjHZXqI55/GO
Has7XENU6v21UdEGAWVUGHf4nsT/xCxRViK26mJrUkDMTX1pufXHDApbauNiC7kD
EC8R+Y34sQ7beU8K10ZmCAMW3i1sVNOxg+X7aV93mN+KS5ZUVvBa+PiIbMPUOt50
s1qzgSwMhRXOe4YGMmr2lzAcOx7oXlkbFIUzk/L83pzmkJncjYC7x2LrO0aVYzDC
lk8yGvp/evMvOjoagEpu4diqv0BrAgMBAAGjUzBRMB0GA1UdDgQWBBRTNKSozzB6
LXTynvnNSOoqBMKC9DAfBgNVHSMEGDAWgBRTNKSozzB6LXTynvnNSOoqBMKC9DAP
BgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQBOdset4ZC7C9mCsVO1
wJ7ETjJD35FUBaAt0UcS6HOBDJqpfToMmzDwLrPPRNlmJ3/qATTEfEOe2v6vt4UN
Ps23YpfhlIfzR47MvuSQMGo1iHpJAe41rDJPuctJSZau25ZFdwkq10+kiQAJyga5
2pGHdXq/QUJ4poKAKKh3hdo5dLR7P0zJ4rsUOm+QQRNtUafqXxpuWuFxmmRL30Cy
ofJgcbF8xKtSOCuaW6GzEhHjZb8BnN0KtZec4Wns0V4fa86dCnf2ZCvwwpl5sIAy
y9cVJtu0JwQdAzVsWSJrE06sEbKc5j4m8nrIbbTR9aqy94tMVkyAXVrVjJwqrs4R
Lvyu
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

void sendAccessRequest(String code) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    //client.setCACert(root_ca);  // Carica il certificato root per la verifica SSL
    client.setInsecure();  // Usa solo se vuoi bypassare SSL (non sicuro)


    Serial.println("[DEBUG] Creazione connessione HTTPS...");
    
    HTTPClient https;
    if (!https.begin(client, serverURL)) {  // Inizializza HTTPS con il client
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
    } else {
      Serial.print("[ERROR] HTTP FALLITO, codice errore: ");
      Serial.println(httpResponseCode);
    }

    https.end();
  } else {
    Serial.println("[ERROR] WiFi non connesso!");
  }
}


void buzz() {
  digitalWrite(buzzerPin, HIGH);
  delay(200);
  digitalWrite(buzzerPin, LOW);
}
