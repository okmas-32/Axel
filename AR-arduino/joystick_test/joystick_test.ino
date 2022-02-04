#include "parametre.h"

String spa = ",";
String serData = "";
bool armME = false;
int VRx1 = _VRx1, VRy1 = _VRy1,
    VRx2 = _VRx2, VRy2 = _VRy2,
    SW1 = _SW1, SW2 = _SW2;

String maxj = _maxj;
String midx1 = _midx1, midy1 = _midy1, midx2 = _midx2, midy2 = _midy2;

void setup() {
  Serial.begin(SERIAL_BAUD);
  Serial.print(serStart);
  Serial.print(maxj + spa + midx1 + spa + midy1 + spa + midx2 + spa + midy2);
  //delay(1500);    //pauza kvôli tomu aby RP vôbec dokázal stihnúť prečítať čo je toto AR zač
  Serial.print('\n');

  // Joystick 1:
  pinMode(SW1, INPUT_PULLUP);
  digitalWrite(SW1, HIGH);

  // Joystick 2:
  pinMode(SW2, INPUT_PULLUP);
  digitalWrite(SW2, HIGH);

}

void loop() {
  if ((Serial.available() > 0) && (armME == false)) {
    char rec = Serial.read();
    delay(15);
    if (rec > 0) {
      if (rec == '1') {
        //Serial.println("dostal si 1 cislo");
        armME = true;
      }
      if (rec == 'A') {
        //Serial.println("dostal si 1");
        armME = true;
      }
      else {
        rec = "";
      }
    }
  }
  if ((armME == true) && (Serial)) {
    // Joystick 1:
    Serial.print(analogRead(VRx1));
    Serial.print(",");
    Serial.print(analogRead(VRy1));
    Serial.print(",");
    Serial.print(!digitalRead(SW1));
    Serial.print(",");
    delay(50);

    // Joystick 2:
    Serial.print(analogRead(VRx2));
    Serial.print(",");
    Serial.print(analogRead(VRy2));
    Serial.print(",");
    Serial.println(!digitalRead(SW2));
    delay(50);
  }
  else {
    delay(100);
  }


}
