#include "parametre.h"
#include <Servo.h>

Servo servo[4];
#define NUM_SERVOS (sizeof(servo) / sizeof(Servo))
const int sernum = NUM_SERVOS;

const byte pinsetup[] = {sr1, sr2, sr3, sr4};   // nezabudni na to keď máš viacej sérv spraviť viac Servo "objektov"
String spa = space;
String input = "";
bool debug = debugb;
String debugs = "debug:";

float uhol[] = {0, 0, 0, 0};
float beta[] = {0, 0, 0, 0};
int milis;

String base = _base, waist = _waist, arm1 = _arm1, arm2 = _arm2, hook = _hook;

unsigned long aktMill = millis();
bool ndone = true, loo = false;

//-----------------------------------------------------------------------------------------------
void setup() {//========================================setup

  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(SERIAL_BAUD);

  while (!Serial) { // nikdy nepôjde lebo napájame arduina z usb portu takže vždy bude zapnutý sériový port
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    delay(200);
  }
  Serial.print(serStart);
  Serial.print(base + spa + waist + spa + arm1 + spa + arm2 + spa + hook);
  Serial.print('\n');

  // možno neskôr rozbehnúť auto setup pre servá
  for (int i = 0; i < NUM_SERVOS; i++) {
    servo[i].attach(pinsetup[i]);
    servo[i].write(90);           // záleží na serve.. môže byť nebezpečné!!!
  }

}











//------------ hlavná časť pre pohyb ------------
bool movMe(Servo *ser , float *_beta, int betan , int _cas, float *_alfa, int alfan, int special = 0) {
  digitalWrite(LED_BUILTIN, HIGH);
  int cas = _cas;                   // zadaný čas na pohyb
  long t = special;                       // čas od začiatku pohybu

  float uh[betan];
  int oneskorenie = 19;
  /*
    float beta[betan];
    float alfa[alfan];

    /*for (int i = 0 ; i < betan ; i++) {
      beta[i] = {_beta[i]};           // konečný uhol
      alfa[i] = {_alfa[i]};           // začiatočný uhol
      uh[i] = {0};                    // na ukladanie lokalneho uhlu
    }*/

  aktMill = millis();               // potrebujeme kontrolovať aktuálne milisekundy v Arduine
  long predMill = aktMill;          // potrebujeme vedieť v ktorých milisekundách bola posledná akcia
  long predMillt = aktMill;         // pre výpočet

  while (cas >= (aktMill - predMill)) {

    for (int i = 0; i < sernum ; i++) { // loopnem cez všetky uhly a vypočítam ich increment
      t += aktMill - predMillt;
      uh[i] = _alfa[i] + (((_beta[i] - _alfa[i]) / cas) * t );
      predMillt = aktMill;
    }
    aktMill = millis();             // stále potrebujeme aktualizovať aktMill  aby sme vedeli aké sú aktuálne milisekundy

    if ((aktMill - predMill) >= oneskorenie) { // ak sú aktuálne milisekundy mínus predošlé milisekundy väčšie alebo rovné oneskoreniu

      for (int i = 0; i < sernum; i++) {
        if (t > cas) {
          uh[i] = uhol[i];
        }
        servo[i].write(uh[i]);
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

  //if (debug) {Serial.println("---out of loop--");}



  /*
    if (debug) {
    Serial.print(debugs); Serial.println("-------------");
    Serial.print(debugs); Serial.print("beta: "); Serial.println(beta);
    Serial.print(debugs); Serial.print("cas: "); Serial.println(cas);
    Serial.print(debugs); Serial.print("alfa: "); Serial.println(alfa);
    }
    /* while (beta != uh) {

    akltualMillis = millis();   // stále aktualizujem čas
    if ((akltualMillis - predMillis >= oneskorenie) and (uh < beta))
    {
      t += akltualMillis - predMillis;
      uh = alfa + (((beta - alfa) / cas) * t );
      predMillis = akltualMillis;   //zapametaj si cas
      if (debug) {
        Serial.print(debugs); Serial.print("t: "); Serial.println(t); //ser.write(uh);
        Serial.print(debugs); Serial.print("UH: "); Serial.println(uh);
      }
      ser[0].write(uh);
    }


    }



    /*
    while (beta != uh) {

    akltualMillis = millis();   // stále aktualizujem čas

    if ((akltualMillis - predMillis >= oneskorenie) and (uh < beta))
    {
      t += akltualMillis - predMillis;
      uh = alfa + (((beta - alfa) / cas) * t );
      predMillis = akltualMillis;   //zapametaj si cas
      if (debug) {
        Serial.print(debugs); Serial.print("t: "); Serial.println(t); //ser.write(uh);
        Serial.print(debugs); Serial.print("UH: "); Serial.println(uh);
      }
      ser[0].write(uh);
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
      ser[0].write(-uh);
    }
    if (t >= cas) {
      beta = uh;
    }
    }


    if (beta == uh)
    {
    Serial.println("1");
    if (debug) {
      Serial.print(debugs); Serial.println("--Uhol dokončený--");
    }
    }*/
}

int counter = 0;
int lastIndex = 0;

void loop() {//=============================================loop

  while (Serial.available() > 0) {
    char rec = Serial.read();
    if (rec == '\n') {
      if (debug) {
        Serial.println("------------------"); Serial.print(debugs); Serial.println("inpud: ");
      }
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
          if (debug) {
            Serial.print(debugs + " "); Serial.println(uhol[counter] + spa);
          }
          counter++;
        }
        else if (input.length() == i + 1) {             // posledný block (milisekundy) nemajú za sebou "," tak tie musím zapísať od posledného zápisu po koniec dátového blocku
          milis = input.substring(lastIndex, i + 1).toInt();
          if (debug) {
            Serial.print(debugs + " milis: "); Serial.println(milis);
          }
        }
      }
      //Serial.println(uhol[0] + spa + uhol[1] + spa + uhol[2] + spa + uhol[3] + spa + milis);
      input = "";
      counter = 0;
      lastIndex = 0;
      rec = "";
      ndone = true;
    }
    else {
      input += rec;
    }
  }

  //  if ((/*((uhol[0] != 0) or (uhol[1] != 0)) or ((uhol[2] != 0) or ( uhol[3] != 0))*/uhol[1] != 0) and (done)) {

  //Serial.println(sizeof(pinsetup));

  loo = (((uhol[0] != beta[0]) or (uhol[1] != beta[1]) or ((uhol[3] != beta[3]) or (uhol[2] != beta[2]))));

  if (loo and ndone) {
    movMe(servo, uhol, (sizeof(uhol) / 2) / 2, milis, beta, (sizeof(beta) / 2) / 2);
    movMe(servo, uhol, (sizeof(uhol) / 2) / 2, milis, beta, (sizeof(beta) / 2) / 2);
    //Serial.println("---DONE---");
    loo = (((uhol[0] != beta[0]) or (uhol[1] != beta[1]) or ((uhol[3] != beta[3]) or (uhol[2] != beta[2]))));

    /*for (int i = 0; i < 5; i++) {
      //TODO dorobiť lineárny pohyb všetkých sérv kontinuálne

      //if (debug) {Serial.println(uhol[i]);}
      beta[i] = movMe(servo[i], uhol[i], milis, beta[i]);
      uhol[i] = beta[i];
      //if (debug) {Serial.println("moveDone");}

      }
      //beta[i] = movMe(servo[i], uhol[i], milis, beta[i]);
    */
  }
  //}
}
