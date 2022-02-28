import subprocess
import sys
import serial
import serial.tools.list_ports      # python -m serial.tools.list_ports -v
import time
import locale
import asyncio
from math import sqrt, atan2, degrees, atan
from csv import DictReader

baud_rate = 115200

debug = {
    '0': bool(1),            # celkový debug
    'csv': bool(1),          # čítanie CSV súboru
    'math': bool(1),         # matematika
    'ini': bool(1),          # inicializačný
    'fromser': bool(0),      # z sériového portu
    'text': '\x1b[1;33;33m' + 'debug:' + '\x1b[0m',     # samotný text "debug:"
    'space': '\x1b[1;33;33m' + 'I ' + '\x1b[0m',        # žltý medzerník
    'gtext': '\33[92m' + 'I ' + '\33[0m',               # zelený medzerník
    'Error': '\x1b[1;30;41m' + '\tE ' + '\x1b[0m'       # VEĽKÉ červené "E "
}


class CustomError(Exception):
    """môj vlastný error handler.. spravil som ho hľavne kvôli tomu
     aby som vedel zachitiť errori ale aj kvôli tomu že to bola sranda naprogramovať"""

    # zachitím error a vypíšem ho bez toho aby som musel zastaviť celí
    # program a robiť odznova celú inicializáciu a podobne

    # teda ak je to error ktorý som schopný obýsť.. ak to je niečo fatálnejšie tak to crashne celé
    def __init__(self, exception, i=None):
        if i!=None:
            # ak to je očakávaný error (bez veľkého červeného E na začiatku)
            print('\r' + debug['space'] + str(exception))
        else:
            i = None
            print('\r' + debug['space'] + debug['Error'] + str(exception))
        pass

class Axel():
    def __init__(self, poss):
        """tu si iba určím aké parametre bude držať objekt v
        classe Axel ako napr. port v ktorom je Arduino alebo dĺžku ramena ruky"""

        self.u1 = 0
        self.u2 = 0
        self.u3 = 0
        self.u4 = 0

        self.ar1u1 = 45
        self.ar1u2 = 45
        self.ar1u3 = 45
        self.ar1u4 = 0

        self.ar2u1 = 45
        self.ar2u2 = 45
        self.ar2u3 = 45
        self.ar2u4 = 90
        self.ar2u5 = 90

        self.A = serial.Serial()        # ser. pre Angie
        self.B = serial.Serial()        # ser. pre Bimbisa
        self.joy = serial.Serial()      # ser. pre joystick ale aj tak sa nepoužíva lebo ho zapína subprocess

        #ports in string
        self.Aport = None
        self.Bport = None
        self.joyPort = None

        #parameters in dictionary
        self.AParametre = {}
        self.BParametre = {}
        self.joyParametre = {}

        self.sendData = bool(1)
        self.sendData1 = bool(1)


        #baud rate for all Arduinos
        self.baud_rate = baud_rate

        self.notAxel = []

        self.spacer = ","

        self.pos1 = {}
        self.pos2 = {}

        if __name__ == "__main__": # prečíta automaticky csv len ak je spustený ako hlavný program
            self.CSVr(poss)

            if debug['csv']:
                print(debug['gtext'] + debug['text'] + f' CSV-saved↓ \r')
                print(f'\t{self.pos1}')
                print(f'\t{self.pos2}')
                print('\r')

        # self.mathAX2(90, 90, 0, 143, 96, 7)

        self.X = 90
        self.Y = 90
        self.Z = 0
        self.rjoy = None

        # inicializácia
        self.ini()

        # toto mám iba na testovanie Arduina
        #                      ↓↓ čas na pohyb v milisekundách
        # -3689,7823,14682,25,500

        # self.mathAX2(self.X, self.Y, self.Z, 143, 96, 7)

    def ini(self):
        """funkcia na získanie (inicializácie) portov v ktorých je Arduino a získanie dát z Arduina o samotnej ruke
        (funguje aj vo windowse☺)"""

        # TODO https://stackoverflow.com/questions/58268507/how-define-a-serial-port-in-a-class-in-python
        # TODO https://python.hotexamples.com/examples/serial/Serial/write/python-serial-write-method-examples.html

        portsini = []
        for port, _, _ in sorted(serial.tools.list_ports.comports()):
            portsini.append(port)

        # hľadá Arduína kým sú neni pripojené všetky
        while not ((self.Aport and self.Bport) and self.joyPort):  # počká sekundu potom skontroluje či sú nové porty ak tak skontroluje či sú to Arduiná s Axelom

            time.sleep(1)
            print("čakám na pripojenie Arduín")
            ports = list(serial.tools.list_ports.comports())

            # debug stuuf (keď nenájde žiadne porty)
            if not portsini:
                raise CustomError("Nenašiel som žiadne porty na hľadanie Axela", 1)
                pass

            if portsini != ports:
                portEH = []

                # prejde cez všetky porty ktoré mu dá serial.tools.list_ports knižnica
                for i, p in enumerate(reversed(ports)):

                    # hodí ich do stringu, splitne a zoberie si prvú hodnotu z toho splitu (to býva ten prvý port)
                    port = str(p)
                    p = port.split(' ', 1)
                    portEH.append(p[0])

                    # debuug
                    if debug['0']:
                        print(str(i))
                        print(f'port: {port}')

                    ser = serial.Serial(portEH[i], self.baud_rate, timeout=2)

                    if ser.isOpen():
                        ser.close()
                    ser.open()

                    try:
                        x = ser.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()

                        Ax = x.split(',')

                        if Ax[1] == 'Angie':  # ak poslalo Arduino v riadku druhé (za ",") angie tak :

                            # vypíšem debuuug že som našiel na "tomto" porte Angie
                            if debug['0'] and debug['ini']: print(debug['gtext'] + f'{portEH[i]} Angie Arduino')

                            # uložím seriový port (zavriem ten starý otvorým ten nový), port (ako text) a samotné parametre
                            # danej ruky (všetky dĺžky a meno)



                            # self.A = ser
                            # ser.close()
                            # self.A.open()
                            # self.Aport = portEH[i]
                            # self.AParametre = {
                            #     'name':  str(Ax[1]),
                            #     'base':  int(Ax[2]),
                            #     'waist': int(Ax[3]),
                            #     'arm1':  int(Ax[4]),
                            #     'arm2':  int(Ax[5]),
                            #     'tool':  int(Ax[6])
                            # }
                        if Ax[1] == 'Bimbis:)':  # ak je Bimbis tak spravím to isté ako pri Angie (lebo oboje sú ruky)
                            if debug['0'] and debug['ini']: print(debug['gtext'] + str(portEH[i]) + f' Bimbis Arduino')
                            self.B = ser
                            ser.close()
                            self.B.open()
                            self.Bport = portEH[i]
                            self.BParametre = {
                                'name':  str(Ax[1]),
                                'base':  int(Ax[2]),
                                'waist': int(Ax[3]),
                                'arm1':  int(Ax[4]),
                                'arm2':  int(Ax[5]),
                                'tool':  int(Ax[6])
                            }
                        if Ax[1] == 'joy':  # ak Arduino pošle že je joystick

                            # debuuuug
                            if debug['0'] and debug['ini']: print(debug['gtext'] + f'{portEH[i]} joystick Arduino')

                            # spravím to isté ako pri rukách len neotvorím nový port lebo bude otvorený pri subprocesse
                            ser.close()
                            self.joy = ser
                            self.joy.open()
                            time.sleep(2)
                            _ = self.joy.readline()
                            self.joyPort = portEH[i]

                            # uložím parametre ako maximum a "hluchú zónu" (nazval som to dead) ktorú pošle Arduino (center si vypočítam z max)
                            self.joyParametre = {
                                'name':   str(Ax[1]),
                                'max':    int(Ax[2]),
                                'dead':   int(Ax[3]),
                                'center': int(int(Ax[2]) / 2)
                            }

                            # iniciuje proces 1 (p1) ako clobálne a dá mu dubprocess s python programom (joy_ReadCOM.py) + port a baud rate v ktorom pracujeme
                            global p1
                            p1 = subprocess.Popen(
                                    ['python', './joy_ReadCOM.py', str(self.joyPort), str(self.baud_rate)],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                            # keď je debug zapnutý tak vypíše 10 riadkov z subprocessu čo prečítal (proste či to ide)
                            if debug['0'] and debug['ini']:
                                for _ in range(10):
                                    rjoy = p1.stdout.readline().decode().rstrip()
                                    print(debug['gtext'] + f'joyAR says: {rjoy}')

                        if debug['0'] and debug['ini']:
                            print(debug['gtext'] + str(Ax))
                            print('------------------------\r')

                    # vypíšem Error ak nejaký nastane.. aaa pokračuje :D
                    except Exception as e:
                        CustomError(e, 0)
                        pass

                    # keď nenájde žiadne Axelovské Arduina
                    if not ((self.Aport or self.Bport) or self.joyPort):
                        print(debug['text'] + '\r' + debug['space'] + "Nenašiel som žiadne porty s Axel doskami")
                        pass
                portsini = ports


    def mathAX2(self,_X, _Y, _Z, arm1, arm2, tool, base = 0):  # TODO niekedy optimalizovať
        """matika na výpočet uhlov z súradníc pre 2kĺbového robota + výpočet rotácie základne
         s Z (roboj je v zmysle že je položený a pracovnú plochu má okolo seba)"""


        #note base predpokladám že bude súčet base a waist (pre matiku to je v podsatate iba offset od "zeme")

        if debug['math']:
            print(debug['text'] + f' Matika-neznáme↓')
            print(f'\t_X = {_X}')
            print(f'\t_Y = {_Y}')
            print(f'\t_Z = {_Z}')
            print(f'\tbase = {base}')
            print(f'\tarm1 = {arm1}')
            print(f'\tarm2 = {arm2}')
            print(f'\ttool = {tool}')

        X = int(_X)
        Y = int(_Y) - (base)
        Z = int(_Z)

        # vypočítam si dĺžky na výpočet matematiky
        dlzka1 = arm1
        dlzka2 = arm2 + tool

        # skontrolovanie či sú všetky súradnice v dosahu ak nie tak ich prepíše na najbližšie v dosahu
        #TODO spraiviť dosah automaticky vypočítaný nie manuálne napísaný
        if X < 80:
            X = 80
        if Y < 1:
            Y = 1
        if Z < 80:
            Z = 80

        # TODO spraviť Q_sq.... cool stuff ;)

        # main math
        t = dlzka2 ** 2 - dlzka1 ** 2 - X ** 2 - Y ** 2

        a = 4 * (X ** 2 + Y ** 2)
        b = 4 * Y * t
        c = t ** 2 - 4 * dlzka1 ** 2 * X ** 2

        D = b ** 2 - 4 * a * c

        Yb1 = (((-b) + sqrt(abs(D))) / (2 * a))
        Yb2 = (((-b) - sqrt(abs(D))) / (2 * a))

        Xb1 = (-sqrt(dlzka2 ** 2 - (Y - Yb1) ** 2) + X)
        Xb2 = (-sqrt(dlzka2 ** 2 - (Y - Yb2) ** 2) + X)

        if (Yb1 >= Yb2):
            Xb = Xb1
            Yb = Yb1
        else:
            Xb = Xb2
            Yb = Yb2


        # debug stuff
        if debug['math'] and debug['0']:
            print(debug['text'])
            print(f'\tX= {X}')
            print(f'\tY= {Y}')
            print(f'\tZ= {Z}')
            print(f'\tdlzka1= {dlzka1}')
            print(f'\tdlzka2= {dlzka2}')
            print(f'\n\tT= {t}')
            print(f'\ta= {a}')
            print(f'\tb= {b}')
            print(f'\tc= {c}')
            print(f'\tD= {D}')
            print(f'\t\tYb1= {Yb1}')
            print(f'\t\tYb2= {Yb2}')
            print(f'\t\tXb1= {Xb1}')
            print(f'\t\tXb2= {Xb2}\r')
            print(f'\tXb= {Xb}')
            print(f'\tYb= {Yb}')

        # konečná matematika
        alfa = degrees(atan2(Yb, Xb))
        beta_ = degrees(atan2(Y - Yb, X - Xb))  #nemam tucha prečo ale musí to byť takto s beta_ lebo inak to dáva iné divné čísla
        beta =  beta_ - alfa + 180
        gama = degrees(atan(Z / X))

        # kontrolovanie či Z súradnica je v negative ak tak sa prehodí aj uhol lebo matika je spravená aby počítala iba s kladným Z
        if Z<0:
            gama = -gama

        if debug['math']: print(debug['text'], str(gama), str(alfa), str(beta))

        # ukladanie uhlov
        # if (arm1 == self.AParametre['base']):
        #     self.ar1u1 = gama   # uhol základni (pohyb : do ľava, do prava)
        #     self.ar1u2 = alfa   # uhol na základni (pohyb : hore, dole)
        #     self.ar1u3 = beta   # uhol zápestia (pohyb : hore, dole)
        #
        # if (arm1 == self.BParametre['base']):
        #     self.ar2u1 = gama
        #     self.ar2u2 = alfa
        #     self.ar2u3 = beta

        return gama, beta, alfa


    def cloSER(self):
        """funkcia na uzatvaranie seriovích komunikácii... ano viem mohol som použiť build in funkcie
        __enter__ a __exit__ ale bolo málo času"""

        serdata = 'reset'
        if self.A.isOpen():
            self.A.write((serdata + '\r\n').encode(locale.getpreferredencoding().rstrip()))
        if self.B.isOpen():
            self.B.write((serdata + '\r\n').encode(locale.getpreferredencoding().rstrip()))

        self.A.close()
        self.B.close()
        self.joy.close()


    def readJOY(self):
        self.joy.write(b'A\r\n')
        while True:
            ree = str(self.joy.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()).split(',')
            yield ree

    def readJOYdata(self):
        """tato funkcia je čisto na čítanie z joystick Arduina"""

        # na čítanie a analýzu údajov z joy_ReadCOM.py bežiaceho v subprocese

        try:
            # prečíta riadok z subprocessu
            re = p1.stdout.readline().decode().rstrip().split(',')
            for re in self.readJOY():
                print(re)

                rec = []

                if re[0] == 'Axel':  # ak sa nejakým spôsobom reštartuje Arduino (vyhodí error)
                    CustomError("Arduino joy bolo reštartované")
                    return

                # už rovno pri zapisovaní hodnnôt kontrolujem či sú väčšie ako "dead zone" zadaný v arduine
                # note ignorujem dáta o switchoch na joysticku sú nepoužitelné lebo na ich stlačenie sa často stáva že sa pohne aj joystick.. používame radšej externé tlačítka na krabičke
                rec[0] = int(int(re[0]) - self.joyParametre['center']) if (int(re[0]) > self.joyParametre['dead']) or ( int(re[0]) < self.joyParametre['dead']*(-1)) else None
                rec[1] = int(int(re[1]) - self.joyParametre['center']) if (int(re[1]) > self.joyParametre['dead']) or ( int(re[1]) < self.joyParametre['dead']*(-1)) else None
                rec[2] = int(int(re[3]) - self.joyParametre['center']) if (int(re[3]) > self.joyParametre['dead']) or ( int(re[3]) < self.joyParametre['dead']*(-1)) else None
                rec[3] = int(int(re[4]) - self.joyParametre['center']) if (int(re[4]) > self.joyParametre['dead']) or ( int(re[4]) < self.joyParametre['dead']*(-1)) else None

                print(rec)
                
                # čítanie externých tlačítiek
                # for i in range(5):
                #     rec[i+4] = bool(re[i+5] if ((not self.predInp) and bool(re[i+5]) == True) else False)
                #     self.predInp[i] = bool(re[i + 5])
                #     if debug['0']:
                #         print(rec[i+4])
                #         print(self.predInp[i])

                #  rec[] = [
                #           0-3: keď je poslaná hodnota väčšia ako "deadzone"(zadané Arduinom) tak uloží nie None hodnotu (v int)
                #           4-8: keď poslaná hodnota je

                # kontrolujem či niečo je v prečítaných dátach a ak ano tak polovičku z toho pri
                if rec[0] is not None:
                    self.u1 += int(rec[0]) / 2
                    self.sendData = bool(0)

                if rec[1] is not None:
                    self.u2 += int(rec[1]) / 2
                    self.sendData = bool(0)

                if rec[3] is not None:
                    self.u3 += int(rec[3]) / 2
                    self.sendData = bool(0)

                if rec[4] is not None:
                    self.u4 += int(rec[4]) / 2
                    self.sendData = bool(0)

                # None
                # 0
                # 0
                # 0
                # 0


                out = { # raw data z joysticku
                        1:{
                            'X' : int(re[0]),
                            'Y' : int(re[1]),
                            'SW' : int(re[2])       # nepoužívame lebo je ťažké stlačiť tlačítko a nepohnúť joystickom
                        },
                        2:{
                            'X' : int(re[3]),
                            'Y' : int(re[4]),
                            'SW' : int(re[5])       # nepoužívame lebo je ťažké stlačiť tlačítko a nepohnúť joystickom
                        },
                        'SW':{
                            1:bool(re[5]),
                            2:bool(re[6]),
                            3:bool(re[7]),
                            4:bool(re[8]),
                            5:bool(re[9])
                        }
                    }

                # ukladá dáta do lokálneho rjoy a vracia dáta
                self.rjoy = out

                time.sleep(0.05) # čakanie 50 miliseconds na ďaľší inpud (lebo Arduino posiela dáta každých 50 milisekúnd)
                return out

        # zaobchádzanie s errorom
        except Exception as e:
            CustomError(e)

    def sendAxel(self, ser, milis = 500): #TODO dať do subprocess alebo aspoň do asyncu
        """táto funkcia slúži na zasielanie uhlov a času za ktorý sa majú servá pohnúť do Axel Arduina"""

        rou = 100  # zaokruhlenie(pre posledné servo čiže chnapačky) / zjednodušenie(aby som nemusel posielať desatinné čísla) pri posielaní do sériového portu
        serdata = "heh... you failed"
        if ser == self.A:
            # zostaviť sériové dáta
            serdata = str(int(round(self.ar1u1, 2) * rou)) + self.spacer + str(int(round(self.ar1u2, 2) * rou)) + self.spacer + str(
                int(round(self.ar1u3, 2) * rou)) + self.spacer + str(int(round(self.ar1u4, 2) / 180 * 100)) + self.spacer + str(milis)

        if ser == self.B:
            serdata = str(
                        int(round(self.ar2u1, 2) * rou)) + self.spacer + str(           # prvý uhol
                        int(round(self.ar2u2, 2) * rou)) + self.spacer + str(           # druhý uhol (ktorý sa preopčítavá na dve servá v Arduine)
                        int(round(self.ar2u3, 2) * rou)) + self.spacer + str(           # tretí uhol ktorý má limiter na arduine na min 90°
                        int(round(self.ar2u4, 2) / 180 * 100)) + self.spacer + str(     # zápästie
                        int(round(self.ar2u5, 2) / 180 * 100)) + self.spacer + str(     # toola ktorá má tiež v Arduine svoje minimum a Maximum
                        milis)

        else: CustomError("neviem kde ale musíš zadať správne arduino na ktoré chceš poslať dáta")

        # debuuuuug
        if debug['0']:print(serdata)

        # samotné posielanie dát
        ser.write((serdata + '\r\n').encode(locale.getpreferredencoding().rstrip()))

        c = ser.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()

        # debuug stuuuf
        if debug['0']: print(c)

        # keď prečíta 1 reprezentujúcu "koniec pohybu" z arduina tak vypíše a zapíše do dát
        if c == '1':
            self.sendData = bool(1)
            if debug['0']:print("pohyb dokon čený")
            return

    def CSVr(self, csvfile):
        """Na čítanie z .csv filov"""
        pos = []
        with open(csvfile, 'r') as csvf:
            csv_diktionary = DictReader(csvf)

            if debug['csv']:
                print(debug['gtext'] + debug['text'] + f' CSV↓ \r')

            posCount1 = 0
            posCount2 = 0
            for row1 in csv_diktionary:
                print(row1)
                if row1['ar'] == '1':
                    posCount1 += 1
                    self.pos1[posCount1] = {
                        'X':row1['X'],
                        'Y': row1['Y'],
                        'Z': row1['Z']
                    }
                    print(self.pos1)

                if row1['ar'] == '2':
                    posCount2 += 1
                    self.pos2[posCount2] = {
                        'X':row1['X'],
                        'Y': row1['Y'],
                        'Z': row1['Z']
                    }
                    print(self.pos2)

                else:pass

                if debug['csv']:
                    print(debug['gtext'] + f' {row1}')

        print('\r')
        return


    def program(self, pos, ser, parametre):
        for po in pos:
            gama, alfa, beta = self.mathAX2(po['X'], po['Y'], po['Z'], parametre['base'], parametre['waist'],
                         parametre['arm1'], parametre['arm2'], parametre['tool'])
            if ser == self.A:
                self.ar1u1 = alfa
                self.ar1u2 = beta
                self.ar1u3 = gama

            if ser == self.B:
                self.ar2u1 = alfa
                self.ar2u2 = beta
                self.ar2u3 = gama

            self.sendAxel(ser, gama, alfa, beta)
        pass


# toto pôjde jedine ak to je spustené ako main program
if __name__ == "__main__":

    # spravý prvú inicializáciu celého prostredia
    object = Axel('.\positions.csv')

    try:

        while object.pos:
            if object.sendData:
                object.program(object.pos, object.A, object.AParametre)
            if object.sendData1:
                object.program(object.pos1, object.B, object.BParametre)

            else: print("čakám na pohyb")

        # #TODO spraviť na checkovanie či je raspberry ready (minimálne jedna RUKA)
        # #===============finnaly the while True loop
        # while True:
        #     time.sleep(0.01)
        #     x = object.readJOYdata()
        #     print(x)
        #     print(object.u1)
        #     print(object.u2)
        #     print(object.u3)
        #     print(object.u4)
        #     if (not object.sendData) and object.predInp[0]:
        #         object.sendAxel(object.A)
        #
        #     if (not object.sendData) and not object.predInp[0]:
        #         object.sendAxel(object.B)

    except KeyboardInterrupt: # očakáva Ctrl + C prerušenie programu
        if debug['0'] and debug['ini']:
            print('\r' + debug['text'])
            print(debug['space'] + f'A arduino: {object.A}')
            print(debug['space'] + f'b arduino: {object.B}')
            print(debug['space'] + f'joy arduino: {object.joy}')
        object.cloSER()
        print(f'\nAxel bol zastavený s commandom Ctrl + C\n')
        if debug['0'] and debug['ini']:
            print(debug['space'] + f'A arduino: {object.A}')
            print(debug['space'] + f'b arduino: {object.B}')
            print(debug['space'] + f'joy arduino: {object.joy}')
        sys.exit(1)

    except Exception as e:
        object.cloSER()
        raise CustomError(e)
        # print(f'\nExeption: ({e})')

    finally:# "čisté" ukončenie programu
        object.cloSER()
        if debug['0']:
            print('\r')
            print(debug['text'])
            print(debug['space'] + str(object.A))
            print(debug['space'] + str(object.Aport))
            print(debug['space'] + str(object.AParametre))
            print(debug['space'] + str(object.B))
            print(debug['space'] + str(object.Bport))
            print(debug['space'] + str(object.BParametre))
            print(debug['space'] + str(object.joy))
            print(debug['space'] + str(object.joyPort))
            print(debug['space'] + str(object.joyParametre))
        sys.exit(0)# "čisté" ukončenie programu

#TODO dorobiť data storage pre každé AR (ukladanie údajov pri inicializácii na neskorší výpočet)
# https://www.youtube.com/watch?v=WOwi0h_-dfA

#TODO spraviť cameru ktorá bude vedieť rozpoznať objekty/farby (Opencv knižnica)
# https://youtu.be/Vi9Y9AL13Rc?t=366

#TODO https://pypi.org/project/pyFirmata/

# class arPort():
#     def __init__(self, n, port, _baud_rate=baud_rate):
#         self.name = n
#         self.port = port
#         self.parametre = []