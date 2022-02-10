#include "parametre.h"
#include <Servo.h>

Servo servo[5];
#define NUM_SERVOS (sizeof(servo) / sizeof(Servo))
const int sernum = NUM_SERVOS;
const byte pinsetup[] = {sr1, sr2, sr3, sr4, sr5};
int maxx = 180;
String spa = space;
String input = "";
bool debug = debugb;
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


//---------------------------------------------------------------------------
// nezabudni na to že pohyb na základni sú 2 servá
//  -3689,7823,14682,25,500

bool movMe(Servo *ser , float *_beta, int betan , int _cas, float *_alfa, int alfan, int special = 0) {
  digitalWrite(LED_BUILTIN, HIGH);
  int cas = _cas;                   // zadaný čas na pohyb
  long t = special;                 // čas od začiatku pohybu

  float uh[betan];
  int oneskorenie = 19;             // pauza medzi intervalmi posielania uhlu do serva 

  aktMill = millis();               // potrebujeme kontrolovať aktuálne milisekundy v Arduine
  long predMill = aktMill;          // potrebujeme vedieť v ktorých milisekundách bola posledná akcia
  long predMillt = aktMill;         // pre výpočet

  while (cas >= (aktMill - predMill)) {

    for (int i = 0; i < betan ; i++) { // loopnem cez všetky uhly a vypočítam ich increment
      t += aktMill - predMillt;
      uh[i] = _alfa[i] + (((_beta[i] - _alfa[i]) / cas) * t );
      predMillt = aktMill;
    }
    aktMill = millis();             // stále potrebujeme aktualizovať aktMill  aby sme vedeli aké sú aktuálne milisekundy

    if ((aktMill - predMill) >= oneskorenie) { // ak sú aktuálne milisekundy mínus predošlé milisekundy väčšie alebo rovné oneskoreniu

      for (int i = 0; i < betan; i++) {
        if (t > cas) {
          uh[i] = uhol[i];
        }

        if (i == 1){ // toto musím spraviť kvôli "angry twin" servu
          servo[i].write(180-uh[i]);
          i++;
          servo[i].write(uh[i]);
          Serial.print("SPECIAL SERVO: ");Serial.println(180-uh[i]);
        }
        else{
          servo[i].write(uh[i]);
          Serial.print("normal SERVO: ");Serial.println(uh[i]);
        }
        
        if (debug) {
          Serial.print(debugs); Serial.print("t: "); Serial.println(t); // ser.write(uh);
          Serial.print(debugs); Serial.print("UH: "); Serial.print(i + " "); Serial.println(uh[i]);
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

//  -3689,7823,14682,25,500
void loop() {//========================================loop
  while (Serial.available() > 0) {
    
    char rec = Serial.read();
    
    if (rec == '\n') {
    
      if (debug) {Serial.println("------------------"); Serial.print(debugs); Serial.println("inpud: ");}
      
      for (int i = 0; i < input.length(); i++) {
        if (input.substring(i, i + 1) == ",") {         // hľadám "," o jeden dopredu
          uhol[counter] = input.substring(lastIndex, i).toFloat() / 100;
          
          if (counter == 3) {                           //pre posledný uhol ktorý je v %
            uhol[counter] = uhol[counter] * 180;
          }
          
          if (counter == 2) {                           //kvôli 3mu servu lebo je v hardweare opačne
            uhol[counter] = +(uhol[counter] - 180);
          }
          
          lastIndex = i + 1;
          
          if (debug) {Serial.print(debugs + " "); Serial.println(uhol[counter] + spa);}
          
          counter++;
        }
        
        else if (input.length() == i + 1) {             // posledný block (milisekundy) nemajú za sebou "," tak tie musím zapísať od posledného zápisu po koniec dátového blocku
          milis = input.substring(lastIndex, i + 1).toInt();
          
          if (debug) {Serial.print(debugs + " milis: "); Serial.println(milis);}
        }
      }
      //Serial.println(uhol[0] + spa + uhol[1] + spa + uhol[2] + spa + uhol[3] + spa + milis);
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
    //movMe(servo, uhol, (sizeof(uhol) / 2) / 2, milis, beta, (sizeof(beta) / 2) / 2);
    //Serial.println("---DONE---");
    loo = (((uhol[0] != beta[0]) or (uhol[1] != beta[1]) or ((uhol[3] != beta[3]) or (uhol[2] != beta[2]))));

    
  }
  
}
