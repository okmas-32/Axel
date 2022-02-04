#include "parametre.h"

String serData = "";
int pinsetup[4] = {3, 5, 9, 10};
bool recb = false;
String spa = ",";

void setup() {
  Serial.begin(SERIAL_BAUD);
  Serial.print(serStart);
  //Serial.print(base + spa + waist + spa + arm1 + spa + arm2 + spa + hak); musia sa zadať!!!
  Serial.print('\n');
}

float serUh[sizeof(pinsetup)];

void loop() {
  while (Serial.available() > 0) {
    byte rec = Serial.read();
    if (rec>0/*rec == "S"/* || recb == true*/) {
      recb = true;
      if (rec == "E") {
        rec = "";
        recb = false;
      }
      serData += rec;
      Serial.println(serData);
    }


    
  }
  if (serData != "") {
    Serial.println(serData);
    serData = "";
  }
  /*
    if (serData != "") {
      Serial.println(serData.length());
      for (int i = 0; i < serData.length(); i++) {
        for (int y = 0; i < sizeof(pinsetup); i++) {
          if (serData.substring(i, i + 1) == ":") {
            if (y == 3) {
              serUh[y] = serData.substring(i - 3, i).toInt() * 100 * 180;
            }
            serUh[y] = serData.substring(i - 4, i).toInt() * 100;
          }
        }
        Serial.print("milis: ");
        Serial.println(serData.substring(i - 3, i).toInt());
      }
      for (int i = 0; i < 4; i++){
        Serial.print("uhol: ");
        Serial.println(serUh[i]);
      }
      serData = "";

    }
  */
  delay(10);
}
