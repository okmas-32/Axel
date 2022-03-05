#include "parametre.h"

String spa = sspace;
String serData = "";
bool armME = false;
bool debug = debugb;  // ak chcem dostávať čistý výstup z arduina tak to nechám vypnuté
String debugs = "debug:";
const byte  VRx1 = _VRx1, VRy1 = _VRy1,
            VRx2 = _VRx2, VRy2 = _VRy2,
            SW1 = _SW1, SW2 = _SW2,
            SW3 = _SW3, SW4 = _SW4,
            SW5 = _SW5, SW6 = _SW6,
            SW7 = _SW7;

String maxj = _maxj, joff = _off;

void setup() {
  Serial.begin(SERIAL_BAUD);

  // inicializačné data pre python
  Serial.print(serStart + maxj + spa + joff);
  Serial.print('\n');

  // Joystick 1 setup
  pinMode(SW1, INPUT_PULLUP);
  digitalWrite(SW1, HIGH);

  // Joystick 2 setup
  pinMode(SW2, INPUT_PULLUP);
  digitalWrite(SW2, HIGH);

  // tlačítka setup
  pinMode(SW3, INPUT_PULLUP);
  digitalWrite(SW3, HIGH);
  pinMode(SW4, INPUT_PULLUP);
  digitalWrite(SW4, HIGH);
  pinMode(SW5, INPUT_PULLUP);
  digitalWrite(SW5, HIGH);
  pinMode(SW6, INPUT_PULLUP);
  digitalWrite(SW6, HIGH);
  pinMode(SW7, INPUT_PULLUP);
  digitalWrite(SW7, HIGH);
}

void loop() {

  // čakám kým niečo neni poslané na seriovom porte
  if ((Serial.available() > 0) && (armME == false)) {
    char rec = Serial.read();
    delay(15);
    
    // ak niečo prečítam z serioveho portu
    if (rec > 0) {

      // a je to 1
      if (rec == '1') {
        // tak zapnem kontinuálne posielanie dát z joisticku a tlačítiek
        armME = true;
      }

      // alebo A
      if (rec == 'A') { // pre debug
        armME = true;
      }
      else {
        // ak nič z toho vyčistím vstup
        rec = "";
      }
    }
  }

  if ((armME == true) && (Serial)) {
    
    // Joystick 1:
    Serial.print(analogRead(VRx1));
    Serial.print(",");Serial.print(analogRead(VRy1));
    Serial.print(",");Serial.print(!digitalRead(SW1));
    
    // Joystick 2:
    Serial.print(",");Serial.print(analogRead(VRx2));
    Serial.print(",");Serial.print(analogRead(VRy2));
    Serial.print(",");Serial.print(!digitalRead(SW2));
    
    // tlačítka
    Serial.print(",");Serial.print(!digitalRead(SW3));
    Serial.print(",");Serial.print(!digitalRead(SW4));
    Serial.print(",");Serial.print(!digitalRead(SW5));
    Serial.print(",");Serial.print(!digitalRead(SW6));
    Serial.print(",");Serial.print(!digitalRead(SW7));
    Serial.print('\n');

    // oneskorenie
    delay(50);
  }
  else {
    delay(100);
  }


}
