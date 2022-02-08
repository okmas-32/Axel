import subprocess
import sys
import serial
import serial.tools.list_ports
import time
import locale
from math import sqrt, atan2, degrees, atan

baud_rate = 115200

debug = {
    '0':bool(1),
    'math':bool(0),
    'ini':bool(1),
    'fromser':bool(0),
    'text':'\x1b[1;33;33m' + 'debug:' + '\x1b[0m',  # hehe found coloring printout
    'space':'\x1b[1;33;33m' + 'I ' + '\x1b[0m',
    'gtext':'\33[92m' + 'I ' + '\33[0m',            # green alebo good text
    'Error':'\x1b[1;30;41m' + '\tE ' + '\x1b[0m'
}

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

class Axel():
    def __init__(self):
        """tu si iba určím aké parametre bude držať objekt v classe Axel ako napr. port v ktorom je Arduino alebo dĺžku ramena ruky"""
        self.u1 = 45
        self.u2 = 45
        self.u3 = 45
        self.u4 = 0

        #ports in serial
        self.A = serial.Serial()        # ser. pre Angie
        self.B = serial.Serial()        # ser. pre Bimbisa
        self.joy = serial.Serial()      # ser. pre joystick ale aj tak sa nepoužíva lebo ho zapína subprocess

        #ports in string
        self.Aport = ""
        self.Bport = ""
        self.joyPort = ""

        #parameters in dictionary
        self.AParametre = {}
        self.BParametre = {}
        self.joyParametre = {}

        #baud rate for all Arduinos
        self.baud_rate = baud_rate

        self.notAxel = [0]*5

        self.X = 90
        self.Y = 90
        self.Z = 0
        self.rjoy = None
        # self.mathAX2(self.X, self.Y, self.Z, 143, 96, 7)
        # self.inicializacia()

    def inicializacia(self, Ax = None):

        if Ax is None:
            print("E: Neni sú žiadne porty v liste")
            return
        ArduinoPort=[]
        for p in self.ports:
            port = str(p)
            if debug['0']:print(port)
            portEH=port.split(' ', 1)
            with serial.Serial(portEH[0], self.baud_rate, timeout=2) as ser:
#TODO https://stackoverflow.com/questions/58268507/how-define-a-serial-port-in-a-class-in-python
#TODO https://python.hotexamples.com/examples/serial/Serial/write/python-serial-write-method-examples.html
                x = ser.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()
                Ax = x.split(',')
                if debug['0']:print(Ax)
                if Ax[0] == 'Axel':
                    ArduinoPort.append(portEH[0])
                    ArduinoPort.append(Ax[1])
                    print(f'našiel som Arduino {str(Ax[1])} na porte: {str(portEH[0])}')

                    # if len(Ax)>2: #TODO get full data

                    if Ax[1] == 'Angie':
                        self.A = ArduinoPort[len(ArduinoPort)-2:len(ArduinoPort)+1:1]
                        ArduinoPort.pop(len(ArduinoPort)-1)
                        ArduinoPort.pop(len(ArduinoPort)-1)
                        rou = 100
                        space = ","

                        serdata = str(int(round(self.u1,2)*rou)) + space + str(int(round(self.u2,2)*rou)) + space + str(int(round(self.u3,2)*rou)) + space + str(int(round(self.u4,2)/180*100)) + space + str(500)
                        #note štvrtý uhol (uhol chnapaka/háku) je prepočítaný do % lebo neni potreba aby bol taký presný
                        #serdata = str(15)
                        print(serdata)
                        ser.write((serdata + '\r\n').encode(locale.getpreferredencoding().rstrip()))
                        c = ser.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()
                        print(c)
                    elif Ax[1] == 'Bimbis:)':
                        self.port.write("1".encode(locale.getpreferredencoding().rstrip()))
                        self.B = ArduinoPort[len(ArduinoPort)-2:len(ArduinoPort)+1:1]
                        ArduinoPort.pop(len(ArduinoPort)-1)
                        ArduinoPort.pop(len(ArduinoPort)-1)
                    elif Ax[1] == 'joy':
                        #self.port.write("1".encode(locale.getpreferredencoding().rstrip()))
                        self.joy = ArduinoPort[len(ArduinoPort)-2:len(ArduinoPort)+1:1]
                        ArduinoPort.pop(len(ArduinoPort)-1)
                        ArduinoPort.pop(len(ArduinoPort)-1)
                    else:print("Nezadefinovaný ovládač na Axela (alebo poškodenie sériových dát.. v tom prípade reset!")
                else:
                    if debug['0']:print(str(portEH[0])+" Neni Arduino")
            if debug['0']:print('\r')
        if 2>(len(self.joy) + len(self.B) + len(self.A)):
            print("Nenašiel som žiadne Arduino")
            return
        print("---------------")
        return

    def ini(self, ports):
        """funkcia na získanie portov v ktorých je Arduino a získanie dát z Arduina o samotnej ruke
        (funguje aj vo windowse☺)"""
        portEH = []
        for i, p in enumerate(ports):
            port = str(p)
            p = port.split(' ', 1)
            portEH.append(p[0])
            if debug['0']:
                print(str(i))
                print(f'port: {port}')
            if not portEH == self.notAxel[i]:
                try:
                    ser = serial.Serial(portEH[i], self.baud_rate, timeout=2)
                    if ser.isOpen():
                        ser.close()
                    ser.open()
                    x = ser.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()
                    Ax = x.split(',')
                    if not Ax[0] == 'Axel': self.notAxel = portEH
                    if Ax[1] == 'Angie':
                        if debug['0'] and debug['ini']: print(debug['gtext'] + f'{portEH[i]} Angie Arduino')
                        self.A = ser
                        ser.close()
                        self.A.open()
                        self.Aport = portEH[i]
                        self.AParametre = {
                            'name': str(Ax[1]),
                            'base': int(Ax[2]),
                            'waist':int(Ax[3]),
                            'arm1': int(Ax[4]),
                            'arm2': int(Ax[5]),
                            'tool': int(Ax[6])
                        }
                    if Ax[1] == 'Bimbis:)':

                        #
                        if debug['0'] and debug['ini']: print(debug['gtext'] + '\33[5m'+ str(portEH[i])+ '\33[0m' +f' Bimbis Arduino') #skúšal som či sa nedá blikať s stringom ale očividne nie
                        self.B = ser
                        ser.close()
                        self.B.open()
                        self.Bport = portEH[i]
                        self.BParametre = {
                            'name': str(Ax[1]),
                            'base': int(Ax[2]),
                            'waist':int(Ax[3]),
                            'arm1': int(Ax[4]),
                            'arm2': int(Ax[5]),
                            'tool': int(Ax[6])
                        }
                    if Ax[1] == 'joy':

                        #
                        if debug['0'] and debug['ini']: print(debug['gtext'] + f'{portEH[i]} joystick Arduino')
                        ser.close()
                        self.joy = ser
                        # self.joy.open()
                        self.joyPort = portEH[i]
                        self.joyParametre = {
                            'name':str(Ax[1]),
                            'max':int(Ax[2]),
                            'dead':int(Ax[3]),
                            'center':int(int(Ax[2])/2)
                        }

                        # iniciuje proces 1 (p1) ako clobálne a dá mu dubprocess s python programom (joy_ReadCOM.py) + port a baud rate v ktorom pracujeme
                        global p1
                        p1 = subprocess.Popen(['python', './joy_ReadCOM.py', str(self.joyPort), str(self.baud_rate)],
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        # will print out if debug to check if the subprocess is working
                        if debug['0'] and debug['ini']:
                            for _ in range(10):
                                rjoy = p1.stdout.readline().decode().rstrip()
                                print(debug['gtext'] + f'joyAR says: {rjoy}')

                    else:  self.notAxel[i] = portEH

                    #
                    if debug['0'] and debug['ini']:
                        print(debug['gtext'] + str(Ax))
                        print('------------------------\r')

                except:
                    pass

            #
            if not ((self.Aport or self.Bport) or self.joyPort):
                print(debug['text'] + '\r'+ debug['space'] +"Nenašiel som žiadne porty s Axel doskami")
                pass

    def mathAX2(self,_X, _Y, _Z):  # TODO niekedy optimalizovať
        """matika na výpočet uhlov z súradníc pre 2kĺbového robota + výpočet rotácie základne
         s Z (roboj je v zmysle že je položený a pracovnú plochu má okolo seba)"""
        X = _X
        Y = _Y
        Z = _Z

        # dlzka2 += dlzka3
        # X = 12
        # Y = 1.2
        # Z = 5
        # dlzka1 = 14.3
        # dlzka2 = 9.6

        # súradnice ktoré poslalo Arduino pri inicializácii
        Y -= self.AParametre['base'] + self.AParametre['waist']
        dlzka1 = self.AParametre['arm1']
        dlzka2 = self.AParametre['arm2'] + self.AParametre['tool']

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

        # finnal math
        alfa = degrees(atan2(Yb, Xb))
        beta_ = degrees(atan2(Y - Yb, X - Xb))  #nemam tucha prečo ale musí to byť takto s beta_ lebo inak to dáva iné divné čísla
        beta =  beta_ - alfa + 180
        gama = degrees(atan(Z / X))

        # kontrolovanie či Z súradnica je v negative ak tak sa prehodí aj uhol lebo matika je spravená aby počítala iba s kladným Z
        if Z<0:
            gama = -gama

        if debug['math']: print(debug['text'], str(gama), str(alfa), str(beta))

        # ukladanie uhlov
        self.u1 = gama  # uhol základni (do ľavo, do prava)
        self.u2 = alfa  # uhol na základni (hore, dole)
        self.u3 = beta  # uhol zápestia (hore, dole)

        #                      ↓↓ čas na pohyb v milisekundách
        # -3689,7823,14682,25,500

    def cloSER(self):
        '''funkcia na uzatvaranie seriovích komunikácii... ano viem mohol som použiť build in funkcie
        __enter__ a __exit__ ale bolo málo času'''
        self.A.close()
        self.B.close()
        self.joy.close()

    def readJOY(self):
        """tato funkcia je čisto na čítanie z joystick Arduina"""

        # if self.rjoy is None:
        #     self.joy.write(('1' + '\r\n').encode(locale.getpreferredencoding().rstrip()))
        # c = self.joy.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()
        # print(c)
        # if debug['0']:print(c)
        # if self.rjoy != c:
        #     if self.rjoy is None:
        #         self.rjoy = c
        #         return
        #     self.rjoy = c
        #     x = c.split(',')
        #     print(x)

        # na čítanie a analýzu údajov z joy_ReadCOM.py bežiaceho v subprocese
        try:
            re = p1.stdout.readline().decode().rstrip().split(',')

            rec = []

            if re[0] == 'Axel':
                CustomError("Arduino joy bolo reštartované")
                return

            rec[0] = int(int(re[0]) - self.joyParametre['center']) if (int(re[0]) > self.joyParametre['dead']) else None
            rec[1] = int(int(re[1]) - self.joyParametre['center']) if (int(re[1]) > self.joyParametre['dead']) else None
            rec[3] = int(int(re[3]) - self.joyParametre['center']) if (int(re[3]) > self.joyParametre['dead']) else None
            rec[4] = int(int(re[4]) - self.joyParametre['center']) if (int(re[4]) > self.joyParametre['dead']) else None

            if rec[0] is not None:
                self.u1 += rec[0] / 2

            if rec[1] is not None:
                self.u1 += rec[0] / 2

            if rec[3] is not None:
                self.u1 += rec[0] / 2

            if rec[4] is not None:
                self.u1 += rec[0] / 2

            out = {
                    1:{
                        'X' : int(re[0]),
                        'Y' : int(re[1]),
                        'SW' : int(re[2])
                    },
                    2:{
                        'X' : int(re[3]),
                        'Y' : int(re[4]),
                        'SW' : int(re[5])
                    }
                }
            self.rjoy = out
            return out
        except Exception as e:
            CustomError(e)

    def sendAxel(self, ser):

        rou = 100   # round
        space = "," # medzera aby to Arduino vedelo prečítať

        # zostaviť sériové dáta
        serdata = str(int(round(self.u1, 2) * rou)) + space + str(int(round(self.u2, 2) * rou)) + space + str(
            int(round(self.u3, 2) * rou)) + space + str(int(round(self.u4, 2) / 180 * 100)) + space + str(500)

        #
        if debug['0']:print(serdata)

        #
        ser.write((serdata + '\r\n').encode(locale.getpreferredencoding().rstrip()))
        c = ser.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()

        if c == '1':print("pohyb dokon čený")

        #
        if debug['0']:print(c)


class CustomError(Exception):
    """my custom 'error handlerer' mainly due to coloring outpud/debug stuff but also it was funn tu setup"""
    def __init__(self, Exception, i = None):
        if i != None:
            print('\r' + debug['space'] + str(Exception))
        else:
            print('\r' + debug['space'] + debug['Error'] + str(Exception))
        pass


# toto pôjde jedine ak to je spustené ako main program
if __name__ == "__main__":
    ar = Axel()
    portsini = list(serial.tools.list_ports.comports())
    try:
        # will make first inicialization of its environment
        ar.ini(portsini)

        # will do only if anny of Arduinos arnt connected
        while not ((ar.Aport and ar.Bport) and ar.joyPort):

            # and it will sleep for sec. then check if are anny new devices connected then check if ther are Axel bords
            time.sleep(1)
            print("čakám na pripojenie Arduín")
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                raise CustomError("Nenašiel som žiadne porty na hľadanie Axela", 1)
                pass
            if portsini != ports:
                ar.ini(ports)  # moest important peace of code
                portsini = ports


        #TODO spraviť na checkovanie či je raspberry ready (minimálne jedna RUKA)
        #===============finnaly the while True loop
        while True:
            time.sleep(0.01)
            x = ar.readJOY()
            print(x)

            ar.sendAxel(ar.A)
            

    # očakáva Ctrl + C prerušenie programu
    except KeyboardInterrupt:
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

    # očakáva akýkoľvek iný Error
    except Exception as e:
        ar.cloSER()
        raise CustomError(e)
        # print(f'\nExeption: ({e})')

    # "čisté" ukončenie programu
    finally:
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
        sys.exit(0)