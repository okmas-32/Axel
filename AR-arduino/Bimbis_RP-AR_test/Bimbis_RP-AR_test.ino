#include "parametre.h"
#include <Servo.h>

/*
 * všetko dôležité je vysvetlené v Angie kóde.. tu sú len špecificné veci 
 * ktoré Angie kód nemá vysvetlené.. ostatné je to isté
 * 
 * môžete si pozrieť celí projekt a dokoumentáciu na https://github.com/okmas-32/Axel
 * 
 */

Servo servo[5];
#define NUM_SERVOS (sizeof(servo) / sizeof(Servo))
const int sernum = NUM_SERVOS;

const byte pinsetup[] = {sr1, sr2, sr3, sr4, sr5};
String spa = space;
String input = "";
bool debug = debugb;
/* 
 * ak kód nefunguje keď je zapojený do počítaču kde beží Axel Python program 
 * tak skontroluj či v parametroch neni debug daný na true.. to neočakáva Python 
 */
String debugs = "debug:";

float uhol[4] = {0, 0, 0, 0};
float beta[4] = {0, 0, 0, 0};
int milis;

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
  
  for (int i = 0; i < NUM_SERVOS; i++) {
    servo[i].attach(pinsetup[i]);
    delay(20);
  }
}


bool movMe(Servo *ser , float *_beta, int betan , int _cas, float *_alfa, int alfan, int special = 0) {
  digitalWrite(LED_BUILTIN, HIGH);
  int cas = _cas;
  long t = 0;

  float uh[betan];
  int oneskorenie = 19;

  aktMill = millis();
  long predMill = aktMill;
  long predMillt = aktMill;

  while (cas >= (aktMill - predMill)) {

    for (int i = 0; i < betan ; i++) { 
      t += aktMill - predMillt;
      uh[i] = _alfa[i] + (((_beta[i] - _alfa[i]) / cas) * t );
      predMillt = aktMill;
    }
    
    aktMill = millis();

    if ((aktMill - predMill) >= oneskorenie) {

      for (int i = 0; i < betan; i++) {
        if (t > cas) {
          uh[i] = uhol[i];
        }

        // toto musím spraviť kvôli "angry twin" servu
        if (i == 1){ 
          servo[i].write(180-uh[i]);
          if (debug) {Serial.print("SPECIAL SERVO: ");Serial.println(180-uh[i]);}
          i++;
          servo[i].write(uh[i]);
        }
        else{
          servo[i].write(uh[i]);
          if (debug) {Serial.print("normal SERVO: ");Serial.println(uh[i]);}
        }
        
        if (debug) {
          Serial.print(debugs); Serial.print("t: ");Serial.println(t); // ser.write(uh);
          Serial.print(debugs); Serial.print("UH: ");Serial.println(uh[i]);
        }
      }
      predMill = aktMill;
    }
    for (int i = 0; i < betan ; i++) {
      if ((t > cas) or (uhol[i] == beta[i])) {
        beta[i] = uh[i];
        Serial.println("1");
        digitalWrite(LED_BUILTIN, LOW);
        ndone = false;
        delay(30);
        
        return;
      }
    }
  }
}


int counter = 0;
int lastIndex = 0;

void loop() {//========================================loop
  while (Serial.available() > 0) {
    char rec = Serial.read();
    if (rec == '\n') {
      
      if (debug) {Serial.println("------------------"); Serial.print(debugs); Serial.println("inpud: ");}
      
      for (int i = 0; i < input.length(); i++) {
        if (input.substring(i, i + 1) == ",") {
          uhol[counter] = input.substring(lastIndex, i).toFloat() / 100;
          
          if (counter == 3) {
            uhol[counter] = uhol[counter] * 180;
          }
          
          if (counter == 2) {
            uhol[counter] = +(uhol[counter] - 180);
          }
          
          lastIndex = i + 1;
          
          if (debug) {Serial.print(debugs + " "); Serial.println(uhol[counter] + spa);}
          
          counter++;
        }
        
        else if (input.length() == i + 1) {
          milis = input.substring(lastIndex, i + 1).toInt();
          
          if (debug) {Serial.print(debugs + " milis: "); Serial.println(milis);}
        }
      }
      input = "";
      counter = 0;
      lastIndex = 0;
      rec = "";
      ndone = true;
      if (debug) {Serial.print('\n');}
    }
    else {
      input += rec;
    }
  }
  
  loo = (((uhol[0] != beta[0]) or (uhol[1] != beta[1]) or ((uhol[3] != beta[3]) or (uhol[2] != beta[2]))));
  
  if (loo and ndone) {
    movMe(servo, uhol, (sizeof(uhol) / 2) / 2, milis, beta, (sizeof(beta) / 2) / 2);
    loo = (((uhol[0] != beta[0]) or (uhol[1] != beta[1]) or ((uhol[3] != beta[3]) or (uhol[2] != beta[2]))));
  }
  
}
