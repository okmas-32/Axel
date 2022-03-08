#include "parametre.h"
#include <Servo.h>

/*
   všetko dôležité je vysvetlené v Angie kóde.. tu sú len špecificné veci
   ktoré Angie kód nemá vysvetlené.. ostatné je to isté

   môžete si pozrieť celí projekt a dokoumentáciu na https://github.com/okmas-32/Axel

*/

Servo servo[6];
#define NUM_SERVOS (sizeof(servo) / sizeof(Servo))
const int sernum = NUM_SERVOS;

const byte pinsetup[] = {sr1, sr2, sr3, sr4, sr5, sr6};
int ser1max = ser1maxp, ser1min = ser1minp,
ser2max = ser2maxp, ser2min = ser2minp,
ser3max = ser3maxp, ser3min = ser3minp,
ser4max = ser4maxp, ser4min = ser4minp,
ser5max = ser5maxp, ser5min = ser5minp,
ser6max = ser6maxp, ser6min = ser6minp;
const int serRozsah[] = {ser1max, ser1min, ser2max, ser2min, ser3max, ser3min, ser4max, ser4min, ser5max, ser5min, ser6max, ser6min};
String spa = space;
String input = "";
bool debug = debugb;
/*
   ak kód nefunguje keď je zapojený do počítaču kde beží Axel Python program
   tak skontroluj či v parametroch neni debug daný na true.. to neočakáva Python
*/
String debugs = "debug:";

float uhol[] = {0, 0, 0, 0, 0};
float beta[] = {0, 0, 0, 0, 0};
int milis = 2000;

String base = _base, waist = _waist, arm1 = _arm1, arm2 = _arm2, hook = _hook;

unsigned long aktMill = millis();
bool ndone = true, loo = false;

//-----------------------------------------------------------------------------------------------
void setup() {//========================================setup
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(SERIAL_BAUD);
  Serial.print(serStart);
  Serial.print(base + spa + waist + spa + arm1 + spa + arm2 + spa + hook);
  Serial.print('\n');

  // MÁŠ O JEDNO SERVO NAVIAC
  int count = 0;
  int u[] = {0,0,0,0,0,0};
  if (ARMservo) {
    for (int i = 0; i < sernum; i++) {
      servo[i].attach(pinsetup[i]);
      delay(20);
      u[i] = (serRozsah[count]-serRozsah[count+1]) / 2 ;
      count = count+2;
      if (debug){
        Serial.println(count);
        Serial.println(u[i]);
        Serial.println(pinsetup[i]);
      }
      servo[i].write(u[i]);
    }
    uhol[0] = u[0];
    uhol[1] = u[1];
    uhol[2] = u[3];
    uhol[3] = u[4];
    uhol[4] = u[5];
    
    beta[0] = u[0];
    beta[1] = u[1];
    beta[2] = u[3];
    beta[3] = u[4];
    beta[4] = u[5];
  }
  // radsej sa nepýtajte
  if (debug) {
    Serial.print('\n'); Serial.print("pocet serv s ktorym sa pocita: ");
    Serial.println(sernum);
  }
}


//  4500,4500,4500,25,25,2000

bool movMe(Servo *ser , float *_beta, int betan , int _cas, float *_alfa, int alfan, int special = 0) {
  digitalWrite(LED_BUILTIN, HIGH);
  int cas = _cas;
  long t = 0;

  Serial.print("betan: ");Serial.println(betan);
  Serial.print("alfan: ");Serial.println(alfan);
  Serial.print("betan1: ");Serial.println(_beta[0]);

  float uh[alfan];
  for (int i = 0; i < alfan; i++) {
    uh[i] = _alfa[i];
    if (debug) {
      Serial.println(uh[i]);
    }
  }
  int oneskorenie = 19;

  aktMill = millis();
  long predMill = aktMill;
  long predMillt = aktMill;

  while (true) {

    for (int i = 0; i < alfan ; i++) { //výpočet uhlov je vzhľadom k uhlom
      t += aktMill - predMillt;
      uh[i] = _alfa[i] + (((_beta[i] - _alfa[i]) / cas) * t );
      predMillt = aktMill;
    }

    aktMill = millis();

    if ((aktMill - predMill) >= oneskorenie) {
      int count_ser = 0;
      for (int i = 0; i < alfan; i++) {
        if (t > cas) {
          uh[i] = uhol[i];
        }

        if (i == 1) {
          if (ARMservo) {
            servo[count_ser].write(180 - uh[i]);
            servo[count_ser + 1].write(uh[i]);
            count_ser += 2;
          }
          if ((debug) or (justdbg)) {
            Serial.print("normal SERVO: ");
            Serial.println(uh[i - 1]);
            Serial.print("SPECIAL SERVO: ");
            Serial.println(180 - uh[i]);
          }
        }

        else {
          if ((debug) or (justdbg)) {
            Serial.print("normal SERVO: ");
            Serial.println(uh[i]);
          }
          else {
            if (ARMservo) {
              servo[count_ser].write(uh[i]);
              count_ser++;
            }
          }
        }

        if (debug) {
          Serial.print(debugs); Serial.print("t: "); Serial.println(t); // ser.write(uh);
          Serial.print(debugs); Serial.print("UH: "); Serial.println(uh[i]);
        }
      }
      if (debug) {
        Serial.print('\n'); Serial.print("-----------ciklus-----------"); Serial.print('\n');
      }
      predMill = aktMill;
    }
    
    if (t > cas) {
      for (int i = 0; i < sernum ; i++) {
        beta[i] = uh[i];
        if (i + 1 == sernum) {
          Serial.println("1");
          digitalWrite(LED_BUILTIN, LOW);
          ndone = false;
          return;
        }
      }
    }
  }
}


int counter = 0;
int lastIndex = 0;
long predMilldon = aktMill;

void loop() {//========================================loop
  while (Serial.available() > 0) {
    char rec = Serial.read();
    if (rec == '\n') {

      if (debug) {
        Serial.println("------------------");
        Serial.print(debugs);
        Serial.print("inpud: ");
        Serial.println(input);
      }
      if (input == "reset") {
        for (int i = 0; i < 5; i++) {
          uhol[i] = 90;
          milis = 2000;
        }
        input = "";
        counter = 0;
        lastIndex = 0;
        rec = "";
        ndone = true;
        if (debug) {
          Serial.print("reset");
          Serial.print('\n');
        }
      }
      else {
        for (int i = 0; i < input.length(); i++) {
          if (input.substring(i, i + 1) == ",") {
            Serial.print(counter);

            uhol[counter] = input.substring(lastIndex, i).toFloat() / 100;

            if (counter == 0) {
              uhol[counter] = uhol[counter] + 90;
            }
            
            if (counter == 2) {
              uhol[counter] = (180 - uhol[counter]);
              if (uhol[counter] < 90) {
                uhol[counter] = 90;
              }
            }

            if (counter == 3) {
              uhol[counter] = uhol[counter] * 180;
            }
            if (counter == 4) { // úprava percent do rozsahu lebo servo nemá celý rozsah volný
              uhol[counter] = (uhol[counter] * (ser5max - ser5min));
            }

            lastIndex = i + 1;

            if (debug) {
              Serial.print(debugs + " ");
              Serial.println(uhol[counter] + spa);
            }

            /*
            if (counter > sernum + 1) {
              for (int i = 0; i < sernum; i++) {
                if (uhol[i] <= serRozsah[i]) {
                  uhol[i] = serRozsah[i];
                  i++;
                }
                if (uhol[i] >= serRozsah[i + 1]) {
                  uhol[i] = serRozsah[i + 1];
                  i++;
                }
                else {
                  i++;
                }
              }
              i = input.length();
            }
            */

            counter++;
          }

          if (input.length() == i + 1) {
            milis = input.substring(lastIndex, i + 1).toInt();

            if (debug) {
              Serial.print(debugs + " milis: ");
              Serial.println(milis);
            }
          }
        }
      }
      input = "";
      counter = 0;
      lastIndex = 0;
      rec = "";
      ndone = true;
      if (debug) {
        Serial.print('\n');
      }
    }
    else {
      input += rec;
    }
  }

  loo = ((uhol[0] != beta[0]) or (uhol[1] != beta[1]) or ((uhol[3] != beta[3]) or (uhol[2] != beta[2])) or ((uhol[4] != beta[4]) or (uhol[5] != beta[5])));

  if (loo and ndone) {
    movMe(servo, uhol, (sizeof(uhol) / sizeof(float)), milis, beta, (sizeof(beta) / sizeof(float)));
    loo = ((uhol[0] != beta[0]) or (uhol[1] != beta[1]) or ((uhol[3] != beta[3]) or (uhol[2] != beta[2])) or ((uhol[4] != beta[4]) or (uhol[5] != beta[5])));
    Serial.println("1");
  }

  aktMill = millis();
  if ((aktMill - predMilldon) >= milis) {
    Serial.println("1");
    predMilldon = aktMill;
  }

}
