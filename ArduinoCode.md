#include <LiquidCrystal.h>

// Configurazione del display LCD
LiquidCrystal lcd(A0, A1, A2, A3, A4, A5);

void setup() {
  lcd.begin(16, 2); // Imposta il display a 16 colonne e 2 righe
  lcd.print("Test Display"); // Visualizza "Test Display"
}

void loop() {
  // Non serve altro per il test
}