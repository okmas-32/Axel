#include "parametre.h"
#include <Servo.h>

/*
   môžete si pozrieť celí projekt a dokoumentáciu na https://github.com/okmas-32/Axel
*/

Servo servo[4];
#define NUM_SERVOS (sizeof(servo) / sizeof(Servo))
const int sernum = NUM_SERVOS;

const byte pinsetup[] = {sr1, sr2, sr3, sr4};   // nezabudni na to keď máš viacej sérv spraviť viac Servo "objektov"
const int serRozsah[] = {ser1max, ser1min, ser2max, ser2min, ser3max, ser3min, ser4max, ser4min};
String spa = space;
String input = "";
int counter = 0;
int lastIndex = 0;

bool debug = debugb;
/*
   ak kód nefunguje keď je zapojený do počítaču kde beží Axel Python program
   tak skontroluj či v parametroch neni debug daný na true.. to neočakáva Python
*/
String debugs = "debug:";

float uhol[sernum] = {0, 0, 0, 0};
float beta[sernum] = {0, 0, 0, 0};
int milis = 2000;

String base = _base, waist = _waist, arm1 = _arm1, arm2 = _arm2, hook = _hook;

unsigned long aktMill = millis();
long predMilldon = aktMill;
bool ndone = true, loo = false;

//-----------------------------------------------------------------------------------------------
void setup() {//========================================setup

  // pre debugovanie a user "interface" (nič lepšie nemáme :D )
  pinMode(LED_BUILTIN, OUTPUT);

  // začať sériovú(USB) kominikáciu
  Serial.begin(SERIAL_BAUD);

  // zasielanie všetkých potrebných parametrov
  Serial.print(serStart);
  Serial.print(base + spa + waist + spa + arm1 + spa + arm2 + spa + hook);
  Serial.print('\n');

  int count = 0;
  // celé spravím iba ak chcem servamy hýbať servami (pre debug)
  if (ARMservo) {
    // inicializácia pinov a zasielanie pinom pozíciu 90°
    for (int i = 0; i < sernum; i++) {
      // attatchnem predurčený pin k objektu servo
      servo[i].attach(pinsetup[i]);
      delay(20);
      
      // voči sercu maximu↓ odpočítam minimum↓ a videlím dvomi↓
      int iniuh = ( serRozsah[count] - serRozsah[count+1] ) / 2;
      count = count+2;

      // uložím aby som vedel kde je servo
      beta[i] = iniuh;
      uhol[i] = iniuh;
      if (debug){
        Serial.println(iniuh);
        Serial.println(i);
      }

      // vpíšem vypočítaný uhol do serva
      servo[i].write(iniuh);
    }
  }
}

// 4500,4500,4500,25,2000

//------------ hlavná časť pre pohyb ------------
bool movMe(Servo *ser , float *_beta, int betan , int _cas, float *_alfa, int alfan, int special = 0) {
  digitalWrite(LED_BUILTIN, HIGH);
  int cas = _cas;                   // zadaný čas na pohyb
  long t = 0;                 // čas od začiatku pohybu

  float uh[sernum];
  for (int i = 0; i < sernum; i++) {
    uh[i] = _alfa[i];
    if (debug) {
      Serial.println(_alfa[i]);
    }
  }
  int oneskorenie = 19;             // pauza medzi intervalmi posielania uhlu do serva

  aktMill = millis();               // potrebujeme kontrolovať aktuálne milisekundy v Arduine
  long predMill = aktMill;          // potrebujeme vedieť v ktorých milisekundách bola posledná akcia
  long predMillt = aktMill;         // pre výpočet

  // proste while true loop
  while (true) {
    // loopnem cez všetky uhly a vypočítam ich increment
    for (int i = 0; i < sernum ; i++) {
      t += aktMill - predMillt;
      uh[i] = _alfa[i] + (((_beta[i] - _alfa[i]) / cas) * t );
      predMillt = aktMill;
    }

    // stále potrebujeme aktualizovať aktMill  aby sme vedeli aké sú aktuálne milisekundy
    aktMill = millis();

    // ak sú aktuálne milisekundy mínus predošlé milisekundy väčšie alebo rovné oneskoreniu
    if ((aktMill - predMill) >= oneskorenie) {
      // loopnem toľko krát koľko mám sérv
      for (int i = 0; i < sernum; i++) {
        // ak čas od začiatku programu je väčší ako zadaný
        if (t > cas) {
          // uhol serva dám na poslanú hodnotu
          uh[i] = uhol[i];
        }
        // vpisovanie vypočítaných uhlov do daného serva
        if (ARMservo) {
          servo[i].write(uh[i]);
        }
        
        // debuuuug
        if (debug) {
          Serial.print(debugs);
          Serial.print("t: ");
          Serial.println(t);
          Serial.print(debugs);
          Serial.print("UH: ");
          Serial.println(uh[i]);
          
        }
      }

      // spravil som pohyb tak prepýšem predošlé milis na aktuálne
      predMill = aktMill;
      if (debug) {
        Serial.print('\n'); Serial.print("-----------ciklus-----------"); Serial.print('\n');
      }
    }

    // ak čas od začiatku programu je väčší ako zadaný čas
    if (t > cas) {

      // idem cez všetky uhly
      for (int i = 0; i < sernum; i++) {

        // prepýšem aktuálny uhol na né uhly
        beta[i] = uh[i];

        if (i + 1 == sernum) {

          // informujem druhú stranu sériového portu že je pohyb dokončený
          Serial.println("1");

          // informujem aj užívateľa aj kód že pohyb bol dokončený
          digitalWrite(LED_BUILTIN, LOW);
          ndone = false;

          // vráti sa
          return;
        }
      }
    }
  }
}


void loop() {//=============================================loop

  // čakám na dáta z seriového portu
  while (Serial.available() > 0) {

    // čítať všetky charaktery postupne z sériového portu
    char rec = Serial.read();

    // ak je koniec "dátového balíčku" tak spracujem balíček
    if (rec == '\n') {

      // debug
      if (debug) {
        Serial.println("------------------");
        Serial.print(debugs);
        Serial.print("inpud: ");
        Serial.println(input);
      }

      if (input == "reset") {
        for (int z = 0; z < sernum; z++) {
          uhol[z] = 90;
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

        // prejdem cez všetky charakteri v stringu input
        for (int i = 0; i < input.length(); i++) {

          // hľadám "," o jeden dopredu
          if (input.substring(i, i + 1) == ",") {

            // uložím uhol od posledného indexu po teraz nájdené "," - 1 a celé to vydelím 100 (proste tak to posielam z pythonu)
            uhol[counter] = input.substring(lastIndex, i).toFloat() / 100;

            // pre posledný uhol ktorý je poslaný z pythonu v %
            if (counter == 3) {
              uhol[counter] = uhol[counter] * 180;
            }

            // kvôli 3 mu servu lebo je fyzicky opačne
            if (counter == 2) {
              uhol[counter] = (180 - uhol[counter]);
            }

            // pracovné prostredie má servo 0-180 nie 0+-90
            if (counter == 0) {
              uhol[counter] = uhol[counter] + 90;
            }

            // aktualizujem posledný index
            lastIndex = i + 1;

            // debuug
            if (debug) {
              Serial.print(debugs + " ");
              Serial.println(uhol[counter] + spa);
            }

            /* pre zatiaľ nepoužívam
            // protekcia keby sa pošle nejakým spôsom viacej dát než arduino potrebuje
            // a kontrola uhlov vzhľadom na min/max uhlov ruky
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

            // pridám 1 aby som uložil do ďaľšieho poľa v uhloch
            counter++;
          }

          // posledná hodnota (milisekundy) nemajú za sebou "," tak tie musím zapísať od posledného zápisu po koniec dátového blocku
          if (input.length() == i + 1) {
            milis = input.substring(lastIndex, i + 1).toInt();

            // debuUug
            if (debug) {
              Serial.print(debugs + " milis: ");
              Serial.println(milis);
            }
          }

        }

      }

      // resetovanie všetkého aby som bol pripravený na ďaľší "dátový balíček"
      input = "";
      counter = 0;
      lastIndex = 0;
      rec = "";
      ndone = true;

      // debuuug
      if (debug) {
        Serial.print('\n');
      }
    }

    // keď neni koniec "dátového balíčku" čítam ďalej čo posiela seriový port
    else {
      input += rec;
    }
  }

  // skontrolujem uhli aktuálne v servách voči uhlom zaslených cez sériovú komunikáciu
  loo = (((uhol[0] != beta[0]) or (uhol[1] != beta[1]) or ((uhol[3] != beta[3]) or (uhol[2] != beta[2]))));

  if (loo and ndone) {

    // zavolám funkciu na pohyb sérv
    movMe(servo, uhol, (sizeof(uhol) / 2) / 2, milis, beta, (sizeof(beta) / 2) / 2);

    // kontrolujem ďaľej uhli
    loo = (((uhol[0] != beta[0]) or (uhol[1] != beta[1]) or ((uhol[3] != beta[3]) or (uhol[2] != beta[2]))));
    Serial.println("1");
  }

  aktMill = millis();
  if ((aktMill - predMilldon) >= milis) {
    Serial.println("1");
    predMilldon = aktMill;
  }
  
}
