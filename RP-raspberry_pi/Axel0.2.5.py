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
spacer = ","

debug = {
    '0': bool(1),            # celkový debug
    'csv': bool(0),          # čítanie CSV súboru
    'math': bool(1),         # matematika
    'ini': bool(1),          # inicializačný
    'fromser': bool(1),      # z sériového portu
    'autoprogram': bool(1),  # proste automatický mód
    'zasielanie': bool(1),   # kontrola zasielania
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

        #ports in string
        self.Aport = bool(0)
        self.Bport = bool(0)
        self.joyPort = bool(0)

        self.notAxel = []

        self.pos1 = {}
        self.pos2 = {}

        if __name__ == "__main__": # prečíta automaticky csv len ak je spustený ako hlavný program
            self.CSVr(poss)

            if debug['csv']:
                print(debug['gtext'] + debug['text'] + f' CSV-saved↓ \r')
                print(f'\t{self.pos1}')
                print(f'\t{self.pos2}')
                print(f'počet príkazov z CSV pre 1: {len(self.pos1)}')
                print(f'počet príkazov z CSV pre 2: {len(self.pos2)}')
                print('\r')

        self.X = 300
        self.Y = 250
        self.Z = 0

        # inicializácia
        # self.ini()

        # toto mám iba na testovanie Arduina
        #                      ↓↓ čas na pohyb v milisekundách
        # -3689,7823,14682,25,500

        # self.mathAX2(self.X, self.Y, self.Z, 143, 96, 7)


    def mathAX2(self, Xi, Yi, Zi, arm1, arm2, tool, base):  # TODO niekedy optimalizovať
        """matika na výpočet uhlov z súradníc pre 2kĺbového robota + výpočet rotácie základne
         s Z (roboj je v zmysle že je položený a pracovnú plochu má okolo seba)"""


        #note base predpokladám že bude súčet base a waist (pre matiku to je v podsatate iba offset od "zeme")

        if debug['math']:
            print(debug['text'] + f' Matika-neznáme↓')
            print(f'\t_X = {Xi}')
            print(f'\t_Y = {Yi}')
            print(f'\t_Z = {Zi}')
            print(f'\tbase = {base}')
            print(f'\tarm1 = {arm1}')
            print(f'\tarm2 = {arm2}')
            print(f'\ttool = {tool}')

        X = int(Xi)
        Y = int(Yi) - (base)
        Z = int(Zi)

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
        beta = degrees(atan2(Yb, Xb))
        gama_ = degrees(atan2(Y - Yb, X - Xb))  #nemam tucha prečo ale musí to byť takto s beta_ lebo inak to dáva iné divné čísla
        gama = gama_ - beta + 180
        alfa = degrees(atan(Z / X))

        # kontrolovanie či Z súradnica je v negative ak tak sa prehodí aj uhol lebo matika je spravená aby počítala iba s kladným Z
        if Z<0:
            alfa = -alfa

        if debug['math']: print(debug['text'], str(alfa), str(beta), str(gama))

        return alfa, beta, gama


    def CSVr(self, csvfile):
        """Na čítanie z .csv filov"""

        with open(csvfile, 'r') as csvf:
            csv_diktionary = DictReader(csvf)

            if debug['csv']:print(debug['gtext'] + debug['text'] + f' CSV↓ \r')

            posCount1 = 0
            posCount2 = 0
            for row1 in csv_diktionary:
                if debug['csv']: print(row1)
                if row1['ar'] == '1':
                    posCount1 += 1
                    self.pos1[posCount1] = {
                        'X':row1['X'],
                        'Y': row1['Y'],
                        'Z': row1['Z']
                    }
                    if debug['csv']:print(self.pos1)

                if row1['ar'] == '2':
                    posCount2 += 1
                    self.pos2[posCount2] = {
                        'X':row1['X'],
                        'Y': row1['Y'],
                        'Z': row1['Z']
                    }
                    if debug['csv']:print(self.pos2)

                else:pass

                if debug['csv']:print(debug['gtext'] + f' {row1}')

        if debug['csv']:print('\r')
        return


    def autoMove(self, loop=0):
        zap_grip = 0, 0
        for i in self.pos1:
            if debug['autoprogram']:
                print(f'Suradnice 1: {self.pos1[i]}')
                print(f'Suradnice 2: {self.pos2[i]}')

            alfa, beta, gama = self.mathAX2(
                            self.pos1[i]['X'],
                            self.pos1[i]['Y'],
                            self.pos1[i]['Z'],
                            self.Angi.parametre['info']['arm1'],
                            self.Angi.parametre['info']['arm2'],
                            self.Angi.parametre['info']['tool'],
                            self.Angi.parametre['info']['waist'] + self.Angi.parametre['info']['base']
                    )
            print(alfa, beta, gama)

            self.Angi.sendAxel(
                    self.mathAX2(
                            self.pos1[i]['X'],
                            self.pos1[i]['Y'],
                            self.pos1[i]['Z'],
                            self.Angi.parametre['info']['arm1'],
                            self.Angi.parametre['info']['arm2'],
                            self.Angi.parametre['info']['tool'],
                            self.Angi.parametre['info']['waist'] + self.Angi.parametre['info']['base']
                    ).append(0)   #hook / gripper? / hák


            )
            zap_grip = 0, 0
            self.Bimb.sendAxel(
                    self.mathAX2(
                            self.pos1[i]['X'],
                            self.pos1[i]['Y'],
                            self.pos1[i]['Z'],
                            self.Angi.parametre['info']['arm1'],
                            self.Angi.parametre['info']['arm2'],
                            self.Angi.parametre['info']['tool'],
                            self.Angi.parametre['info']['waist'] + self.Angi.parametre['info']['base']
                    ).extend(zap_grip) # zápästie a gripper "zatvorenosť"
            )
            if loop and len(self.pos1) == i+1:
                i = 1


    def ini(self):
        """funkcia na získanie (inicializácie) portov v ktorých je Arduino a získanie dát z Arduina o samotnej ruke
        (funguje aj vo windowse☺)"""

        # TODO https://stackoverflow.com/questions/58268507/how-define-a-serial-port-in-a-class-in-python
        # TODO https://python.hotexamples.com/examples/serial/Serial/write/python-serial-write-method-examples.html

        portsini = []
        for port, _, _ in sorted(serial.tools.list_ports.comports()):
            portsini.append(port)

        if debug['ini']: print(portsini)

        # hľadá Arduína kým sú neni pripojené všetky
        if not ((self.Aport and self.Bport) and self.joyPort):  # počká sekundu potom skontroluje či sú nové porty ak tak skontroluje či sú to Arduiná s Axelom

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
                        print('\r\n' + str(i))
                        print(f'port: {port}')

                    with serial.Serial(portEH[i], baud_rate, timeout=2) as ser:

                        if ser.isOpen():
                            ser.close()
                        ser.open()

                        try:
                            x = ser.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()

                            Ax = x.split(',')

                            if debug['fromser']: print(f'z serioveho portu {Ax}')

                            if Ax[1] == 'Angie':  # ak poslalo Arduino v riadku druhé (za ",") angie tak :
                                # vypíšem debuuug že som našiel na "tomto" porte Angie
                                if debug['0'] and debug['ini']: print(debug['gtext'] + f'{portEH[i]} Angie Arduino')

                                ser.close()
                                start = [300, 100, 0]
                                self.Angi = arduino.ruka(Ax, start, ser)
                                self.Aport = bool(1)

                            elif Ax[1] == 'Bimbis:)':  # ak je Bimbis tak spravím to isté ako pri Angie (lebo oboje sú ruky)
                                if debug['0'] and debug['ini']: print(debug['gtext'] + str(portEH[i]) + f' Bimbis Arduino')

                                ser.close()
                                start = [300, 250, 0]
                                self.Bimb = arduino.ruka(Ax, start, ser)
                                self.Bport = bool(1)

                            elif Ax[1] == 'joy':  # ak Arduino pošle že je joystick
                                # debuuuug
                                if debug['0'] and debug['ini']: print(debug['gtext'] + f'{portEH[i]} joystick Arduino')

                                ser.close()
                                self.Joy = arduino.joy(Ax, ser)
                                self.joyPort = bool(1)

                            else:
                                ser.close()
                                pass

                            if debug['0'] and debug['ini']:
                                print(debug['gtext'] + str(Ax))
                                print('------------------------\r\n')


                        # vypíšem Error ak nejaký nastane.. aaa pokračuje :D
                        except Exception as e:
                            CustomError(e, 0)
                            pass

                        # keď nenájde žiadne Axelovské Arduina
                if not ((self.Aport or self.Bport) or self.joyPort):
                    print(debug['text'] + '\r' + debug['space'] + "Nenašiel som žiadne porty s Axel doskami")
                    pass
                    portsini = ports

            time.sleep(1)
            print("čakám na pripojenie Arduín")

        if ((self.Aport and self.Bport) and self.joyPort): print('\r\n' + debug['gtext'] + debug['gtext'] + debug['gtext'] + '\33[92m' + ' inicializácia Axel prostredia je ukončená' + '\33[0m' + '\r\n')


class arduino():
    class ruka():
        def __init__(self, parametre, zaklad, serPort = serial.Serial()):
            self.serPort = serPort
            self.serPort.open()

            self.serPort.flushInput()
            self.name = parametre[1]
            self.sendData = bool(0)

            print(parametre)
            self.parametre = {
                'info': {
                    'name':  str(parametre[1]),
                    'base':  int(parametre[2]),
                    'waist': int(parametre[3]),
                    'arm1':  int(parametre[4]),
                    'arm2':  int(parametre[5]),
                    'tool':  int(parametre[6])
                },
                'suradnice': {
                    'X': int(zaklad[0]),
                    'Y': int(zaklad[1]),
                    'Z': int(zaklad[2])
                },
                'uhly': [
                    0,
                    0,
                    0,
                    0
                ]
            }

            if self.name == 'Bimbis:)': #pre gripper
                self.parametre['uhly'].append(0)

            self.parametre['uhly'][0], self.parametre['uhly'][1], self.parametre['uhly'][2] = object.mathAX2(
                    self.parametre['suradnice']['X'],
                    self.parametre['suradnice']['Y'],
                    self.parametre['suradnice']['Z'],
                    self.parametre['info']['arm1'],
                    self.parametre['info']['arm2'],
                    self.parametre['info']['tool'],
                    self.parametre['info']['base'] + self.parametre['info']['waist']
            )

            self.sendAxel(self.parametre['uhly'], 2000)

            if debug['ini'] and self.sendData: print(debug['gtext'] + debug['gtext'] + f'inicializácia {parametre[1]} hotová')


        def sendAxel(self, data, milis=1500): #TODO dať do subprocess alebo aspoň do asyncu
            """táto funkcia slúži na zasielanie uhlov a času za ktorý sa majú servá pohnúť do Axel Arduina"""


            if debug['zasielanie']: print(f'\rdata v send Data = {data}')

            rou = 100  # zaokruhlenie(pre posledné servo čiže chnapačky) / zjednodušenie(aby som nemusel posielať desatinné čísla) pri posielaní do sériového portu
            serdata = "heh... you failed"
            if self.name == 'Angie':
                # zostaviť sériové dáta
                serdata = ((str(round(int((data[0])), 2) * rou) if (int(data[0]) != 0) else str(0)) + spacer +
                           (str(round(int((data[1])), 2) * rou) if (int(data[1]) != 0) else str(0)) + spacer +
                           (str(round(int((data[2])), 2) * rou) if (int(data[2]) != 0) else str(0)) + spacer +
                           (str(round(int((data[3])), 2) / 180 * 100) if (int(data[3]) != 0) else str(0)) + spacer +
                           str(milis))
                data.pop()

            elif self.name == 'Bimbis:)':
                serdata = ((str(round(int((data[0])), 2) * rou) if (int(data[0]) != 0) else str(0)) + spacer + str(         # prvý uhol
                        (round(int((data[1])), 2) * rou) if (int(data[1]) != 0) else str(0)) + spacer + str(           # druhý uhol (ktorý sa preopčítavá na dve servá v Arduine)
                        (round(int((data[2])), 2) * rou) if (int(data[2]) != 0) else str(0)) + spacer + str(           # tretí uhol ktorý má limiter na arduine na min 90°
                        (round(int((data[3])), 2) / 180 * 100) if (int(data[3]) != 0) else str(0)) + spacer + str(     # zápästie
                        (round(int((data[4])), 2) / 180 * 100) if (int(data[4]) != 0) else str(0)) + spacer + str(     # toola ktorá má tiež v Arduine svoje minimum a Maximum
                            milis))
                data.pop()
            else:
                CustomError("neviem kde ale musíš zadať správne arduino na ktoré chceš poslať dáta")

            if debug['zasielanie']: print(f'posielanie dat = {serdata}')

            while not self.sendData:
                self.serPort.write((serdata + '\r\n').encode(locale.getpreferredencoding().rstrip()))
                time.sleep((milis-50)/1000)
                c = self.serPort.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()
                if debug['autoprogram']: print(debug['gtext'] + f'pohyb dokončený z Arduina?: {c}')
                if c == '1':
                    self.sendData = bool(1)
                    if debug['autoprogram']: print(debug['gtext'] + f"pohyb dokončený\r\n")
                else:
                    print('\x1b[1;33;33m' + 'čakanie na dokončenie pohybu' + '\x1b[0m')
                    print(c + '\n')
                    self.serPort.flushInput()



        def __exit__(self, exc_type=0, exc_val=0, exc_tb=0):
            if self.serPort.isOpen():
                serdata = 'reset'
                self.serPort.write((serdata + '\r\n').encode(locale.getpreferredencoding().rstrip()))
                self.serPort.close()
            else:
                CustomError(f'Port {self.serPort.name} už bol zatvorený')


        def __str__(self):
            return str(self.__class__) + '\n' + '\n'.join(
                    ('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))


    class joy():
        def __init__(self, parametre, serPort=serial.Serial()):
            self.serPort = serPort
            self.name = parametre[1]

            # iniciuje proces 1 (p1) ako clobálne a dá mu dubprocess s python programom (joy_ReadCOM.py) + port a baud rate v ktorom pracujeme
            global p1
            p1 = subprocess.Popen(
                    ['python', './joy_ReadCOM.py', str(self.serPort.name), str(self.serPort._baudrate)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # keď je debug zapnutý tak vypíše 10 riadkov z subprocessu čo prečítal (proste či to ide)
            if debug['0'] and debug['ini']:
                for _ in range(10):
                    rjoy = p1.stdout.readline().decode().rstrip()
                    print(debug['gtext'] + f'joyAR says: {rjoy}')

            self.Parametre = {
                                'name':   str(parametre[1]),
                                'max':    int(parametre[2]),
                                'dead':   int(parametre[3]),
                                'center': int(int(parametre[2]) / 2)
                            }


        def __exit__(self, exc_type=0, exc_val=0, exc_tb=0):
            self.serPort.close()
            if self.serPort.isOpen():
                CustomError(f'Port {self.serPort.name} sa nepodarilo zatvoriť')


        def __str__(self):
            return str(self.__class__) + '\n' + '\n'.join(
                    ('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))


# toto pôjde jedine ak to je spustené ako main program
if __name__ == "__main__":

    # spravý prvú inicializáciu celého prostredia

    # note v Raspberry sa musí vymeniť "\" za "/"... nepítaj sa prečo iba to sprav
    object = Axel('.\positions.csv')
    object.ini()

    object.autoMove(1)


    try:
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



        print(object.Angi.name)
        print(object.Bimb.name)
        print(object.Joy.name)
        print('\r\n')
        print(object.Angi)
        time.sleep(10)

    except KeyboardInterrupt: # očakáva Ctrl + C prerušenie programu
        if debug['0'] and debug['ini']:
            print('\r' + debug['text'])
            print(debug['space'] + f'Angie arduino je zatvorene: {not object.Angi.serPort.isOpen()}')
            print(debug['space'] + f'Bimb arduino je zatvorene: {not object.Bimb.serPort.isOpen()}')
            print(debug['space'] + f'joy arduino je zatvorene: {not object.Joy.serPort.isOpen()}')

        print(f'\nAxel bol zastavený s commandom Ctrl + C\n')

        sys.exit(1)

    except Exception as e:
        if debug['0'] and debug['ini']:
            print('\r' + debug['text'])
            print(debug['space'] + f'Angie arduino je zatvorene: {not object.Angi.serPort.isOpen()}')
            print(debug['space'] + f'Bimb arduino je zatvorene: {not object.Bimb.serPort.isOpen()}')
            print(debug['space'] + f'joy arduino je zatvorene: {not object.Joy.serPort.isOpen()}')
        raise CustomError(e)
        # print(f'\nExeption: ({e})')

    finally:# "čisté" ukončenie programu
        if debug['0']:
            print('\r')
            print(debug['text'])
            print(debug['space'] + str(object.Angi.name))
            print(debug['space'] + str(object.Angi) + '\n')

            print(debug['space'] + str(object.Bimb.name))
            print(debug['space'] + str(object.Bimb) + '\n')

            print(debug['space'] + str(object.Joy.name))
            print(debug['space'] + str(object.Joy) + '\n')
        sys.exit(0)# "čisté" ukončenie programu