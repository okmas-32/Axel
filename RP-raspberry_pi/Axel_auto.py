import sys
import serial
import serial.tools.list_ports      # python -m serial.tools.list_ports -v
import time
import locale
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
        if i is not None:
            # ak to je očakávaný error (bez veľkého červeného E na začiatku)
            print('\r' + debug['space'] + str(exception))
        else:
            i = None
            print('\r' + debug['space'] + debug['Error'] + str(exception))
        pass


class Axel():
    def __init__(self):
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

        self.pos = None
        self.pos1 = None

        self.ini()

        if __name__ == "__main__":
            # čítanie z CSV
            # p = glob(".\*.csv")
            # csv = str(p[0])
            # while True:
            #     time.sleep(5)
            self.pos = self.CSVr('.\positions.csv')
            self.pos1 = self.CSVr('.\positions1.csv')
            if debug['csv']:
                print(self.pos)
                print(self.pos1)


        self.X = 90
        self.Y = 90
        self.Z = 0
        self.rjoy = None

    def ini(self):
        """funkcia na získanie (inicializácie) portov v ktorých je Arduino a získanie dát z Arduina o samotnej ruke
        (funguje aj vo windowse☺)"""

        portsini = []
        for port, _, _ in sorted(serial.tools.list_ports.comports()):
            portsini.append(port)

        # hľadá Arduína kým sú neni pripojené všetky
        while not (self.Aport and self.Bport):  # počká sekundu potom skontroluje či sú nové porty ak tak skontroluje či sú to Arduiná s Axelom

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
                            self.A = ser
                            ser.close()
                            self.A.open()
                            self.Aport = portEH[i]
                            self.AParametre = {
                                'name':  str(Ax[1]),
                                'base':  int(Ax[2]),
                                'waist': int(Ax[3]),
                                'arm1':  int(Ax[4]),
                                'arm2':  int(Ax[5]),
                                'tool':  int(Ax[6])
                            }
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

                        if debug['0'] and debug['ini']:
                            print(debug['gtext'] + str(Ax))
                            print('------------------------\r')

                    except Exception as e:
                        CustomError(e, 0)
                        pass

                    # keď nenájde žiadne Axelovské Arduina
                    if not (self.Aport or self.Bport):
                        print(debug['text'] + '\r' + debug['space'] + "Nenašiel som žiadne porty s Axel doskami")
                        pass
                portsini = ports

    def CSVr(self,csvfile):
        pos = []
        with open(csvfile, 'r') as csvf:
            csv_diktionary = DictReader(csvf)
            for row1 in csv_diktionary:
                pos.append(row1)
                if debug['csv']:
                    print(debug['gtext'] + debug['text'] + f' CSV: \r')
                    print(debug['gtext'] + f' {row1}')
            if debug['csv']:
                for po in pos:
                    print(po['X'])
            return pos


    def sendAxel(self, ser,gama ,alfa, beta, milis=500):
        c = 0
        rou = 100  # zaokruhlenie(pre posledné servo čiže chnapačky) / zjednodušenie(aby som nemusel posielať desatinné čísla) pri posielaní do sériového portu
        serdata = "heh... you failed"

        while c == 0:
            if self.sendData:
                serdata = str(int(round(gama, 2) * rou)) + self.spacer + str(
                        int(round(alfa, 2) * rou)) + self.spacer + str(
                        int(round(beta, 2) * rou)) + self.spacer + str(
                        int(round(self.ar1u4, 2) / 180 * 100)) + self.spacer + str(milis)

            if self.sendData1:
                serdata = str(
                        int(round(gama, 2) * rou)) + self.spacer + str(  # prvý uhol
                        int(round(alfa, 2) * rou)) + self.spacer + str(
                        # druhý uhol (ktorý sa preopčítavá na dve servá v Arduine)
                        int(round(beta, 2) * rou)) + self.spacer + str(
                        # tretí uhol ktorý má limiter na arduine na min 90°
                        int(round(self.ar2u4, 2) / 180 * 100)) + self.spacer + str(  # zápästie
                        int(round(self.ar2u5, 2) / 180 * 100)) + self.spacer + str(
                        # toola ktorá má tiež v Arduine svoje minimum a Maximum
                        milis)
            else:
                CustomError("neviem kde ale musíš zadať správne arduino na ktoré chceš poslať dáta")

            if debug['0']: print(serdata)
            ser.write((serdata + '\r\n').encode(locale.getpreferredencoding().rstrip()))
            c = ser.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()
            if debug['0']: print(c)
        if c == '1':
            self.sendData = bool(1)
            if debug['0']: print("pohyb dokon čený")

    def mathAX2(self,_X, _Y, _Z, base, waist, arm1, arm2, tool):  # TODO niekedy optimalizovať
        """matika na výpočet uhlov z súradníc pre 2kĺbového robota + výpočet rotácie základne
         s Z (roboj je v zmysle že je položený a pracovnú plochu má okolo seba)"""

        print(base)

        X = int(_X)
        Y = int(_Y)
        Z = int(_Z)

        Y = Y - (base + waist)

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
        if (base == self.AParametre['base']):
            self.ar1u1 = gama   # uhol základni (pohyb : do ľava, do prava)
            self.ar1u2 = alfa   # uhol na základni (pohyb : hore, dole)
            self.ar1u3 = beta   # uhol zápestia (pohyb : hore, dole)

        return gama, alfa, beta

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

            self.sendAxel(ser, gama,alfa,beta)
        pass


    def cloSER(self):
        """funkcia na uzatvaranie seriovích komunikácii... ano viem mohol som použiť build in funkcie
        __enter__ a __exit__ ale bolo málo času"""

        self.A.close()
        self.B.close()
        self.joy.close()





if __name__ == "__main__":

    # spravý prvú inicializáciu celého prostredia
    ar = Axel()

    try:
        while True:
            if ar.sendData:
                ar.program(ar.pos, ar.A, ar.AParametre)
            if ar.sendData1:
                ar.program(ar.pos1, ar.B, ar.BParametre)

            else: print("čakám na pohyb")

    except KeyboardInterrupt:  # očakáva Ctrl + C prerušenie programu
        if debug['0'] and debug['ini']:
            print('\r' + debug['text'])
            print(debug['space'] + f'A arduino: {ar.A}')
            print(debug['space'] + f'b arduino: {ar.B}')
            print(debug['space'] + f'joy arduino: {ar.joy}')
        ar.cloSER()
        print(f'\nAxel bol zastavený s commandom Ctrl + C\n')
        if debug['0'] and debug['ini']:
            print(debug['space'] + f'A arduino: {ar.A}')
            print(debug['space'] + f'b arduino: {ar.B}')
            print(debug['space'] + f'joy arduino: {ar.joy}')
        sys.exit(1)

    except Exception as e:
        ar.cloSER()
        raise CustomError(e)
        # print(f'\nExeption: ({e})')

    finally:  # "čisté" ukončenie programu
        ar.cloSER()
        if debug['0']:
            print('\r')
            print(debug['text'])
            print(debug['space'] + str(ar.A))
            print(debug['space'] + str(ar.Aport))
            print(debug['space'] + str(ar.AParametre))
            print(debug['space'] + str(ar.B))
            print(debug['space'] + str(ar.Bport))
            print(debug['space'] + str(ar.BParametre))
            print(debug['space'] + str(ar.joy))
            print(debug['space'] + str(ar.joyPort))
            print(debug['space'] + str(ar.joyParametre))
        sys.exit(0)  # "čisté" ukončenie programu
