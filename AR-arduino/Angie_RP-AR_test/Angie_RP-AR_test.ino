#include "parametre.h"
#include <Servo.h>

Servo servo[4];
int pinsetup[4] = {sr1, sr2, sr3, sr4};
String spa = space;
String input = "";
bool debug = debugb;
String debugs = "debug:";

float uhol[4] = {0, 0, 0, 0};
float beta[4] = {0, 0, 0, 0};
int milis;

String base = _base, waist = _waist, arm1 = _arm1, arm2 = _arm2, hook = _hook;


//-----------------------------------------------------------------------------------------------
void setup() {//========================================setup
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(SERIAL_BAUD);
  while (!Serial) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    delay(200);
  }
  Serial.print(serStart);
  Serial.print(base + spa + waist + spa + arm1 + spa + arm2 + spa + hook);
  Serial.print('\n');
  //for (int i = 0; i < 5; i++) {
  //  servo[i].attach(pinsetup[i]);
  //}
  servo[0].attach(pinsetup[0]);
  servo[1].attach(pinsetup[1]);
  servo[2].attach(pinsetup[2]);
  servo[3].attach(pinsetup[3]);
  servo[0].write(90);
  servo[1].write(90);
  servo[2].write(90);
  servo[3].write(0);
}

bool nerovnake(float _u1, float _u2, float _u3, float _u4, float u1, float u2, float u3, float u4) {
  return (((_u1 != u1) or (_u2 != u2)) or ((_u3 != u3) or (_u4 != u4)));
}

float movMe(Servo &ser, float _beta, int _cas, float _alfa, int special = 0) {
  float beta = _beta; // konečný uhol
  int cas = _cas;     // zadaný čas na pohyb
  float alfa = _alfa; // začiatočný uhol
  long t = 0;         // čas od začiatku pohybu
  float uh = 0;       // na ukladanie lokalneho uhlu

  int oneskorenie = 1;
  unsigned long akltualMillis = millis();
  long predMillis = akltualMillis;
  if (debug) {
    Serial.print(debugs); Serial.println("-------------");
    Serial.print(debugs); Serial.print("beta: "); Serial.println(beta);
    Serial.print(debugs); Serial.print("cas: "); Serial.println(cas);
    Serial.print(debugs); Serial.print("alfa: "); Serial.println(alfa);
  }
  while (beta != uh) {
    akltualMillis = millis();
    if ((akltualMillis - predMillis >= oneskorenie) and (uh < beta))
    {
      t += akltualMillis - predMillis;
      uh = alfa + (((beta - alfa) / cas) * t );
      predMillis = akltualMillis;   //zapametaj si cas
      if (debug) {
        Serial.print(debugs); Serial.print("t: "); Serial.println(t); //ser.write(uh);
        Serial.print(debugs); Serial.print("UH: "); Serial.println(uh);
      }
      ser.write(uh);
    }
    if ((akltualMillis - predMillis >= oneskorenie) and (uh > beta))
    {
      t += akltualMillis - predMillis;
      uh = alfa + (((beta - alfa) / cas) * t );
      predMillis = akltualMillis;   //zapametaj si cas
      if (debug) {
        Serial.print(debugs); Serial.print("-t: "); Serial.println(t); //ser.write(uh);
        Serial.print(debugs); Serial.print("-UH: "); Serial.println(uh);
      }
      ser.write(-uh);
    }
    if (t >= cas) {
      beta = uh;
    }
  }
  if (beta == uh)
  {
    if (debug) {
      Serial.print(debugs); Serial.println("--Uhol dokončený--");
    }
    return uh;
  }
}
int counter = 0;
int lastIndex = 0;
void loop() {//========================================loop
  while (Serial.available() > 0) {
    char rec = Serial.read();
    if (rec == '\n') {
      if (debug) {
        Serial.print('\n' + debugs); Serial.print("inpud: ");
      }
      for (int i = 0; i < input.length(); i++) {
        if (input.substring(i, i + 1) == ",") {// hľadám "," o jeden dopredu
          uhol[counter] = input.substring(lastIndex, i).toFloat() / 100;
          if (counter == 3) { //pre posledný uhol ktorý je v %
            uhol[counter] = uhol[counter] * 180;
          }
          if (counter == 2) { //kvôli 3mu servu lebo je v hardweare opačne
            uhol[counter] = +(uhol[counter] - 180);
          }
          lastIndex = i + 1;
          if (debug) {
            Serial.print(debugs);Serial.print(uhol[counter] + spa);
          }
          counter++;
        }
        else if (input.length() == i + 1) {// posledný block (milisekundy) nemajú za sebou "," tak tie musím zapísať od posledného zápisu po koniec dátového blocku
          milis = input.substring(lastIndex, i + 1).toInt();
          if (debug) {
            Serial.print(debugs);Serial.print(milis);
          }
        }
      }
      //Serial.println(uhol[0] + spa + uhol[1] + spa + uhol[2] + spa + uhol[3] + spa + milis);
      input = "";
      counter = 0;
      lastIndex = 0;
      rec = "";
    }
    else {
      input += rec;
    }
  }
  if ((((uhol[0] != 0) or (uhol[1] != 0)) or ((uhol[2] != 0) or ( uhol[3] != 0))) and (Serial.available() == 0)) {
    if ( 1 == nerovnake(uhol[0], uhol[1], uhol[2], uhol[3], beta[0], beta[1], beta[2], beta[3])) {
      for (int i = 0; i < 5; i++) {
        //TODO dorobiť lineárny pohyb všetkých sérv kontinuálne
        //if (debug) {Serial.println(uhol[i]);}
        beta[i] = movMe(servo[i], uhol[i], milis, beta[i]);
        uhol[i] = beta[i];
        //if (debug) {Serial.println("moveDone");}

      }
    }
  }
}
