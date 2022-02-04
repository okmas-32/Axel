import subprocess
import sys
import serial
import serial.tools.list_ports
import time
import locale
from math import sqrt, atan2, degrees, atan

baud_rate = 115200

debug = [bool(1), "debug: "]

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
        self.ser = ''
        self.A = serial.Serial()
        self.B = serial.Serial()
        self.joy = serial.Serial()
        self.Aport = ""
        self.Bport = ""
        self.joyPort = ""
        self.baud_rate = baud_rate
        self.parametre = '' #TODO dorobiť dostávanie parametrov z arduina na výpočet
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
            if debug[0]:print(port)
            portEH=port.split(' ', 1)
            with serial.Serial(portEH[0], self.baud_rate, timeout=2) as ser:
#TODO https://stackoverflow.com/questions/58268507/how-define-a-serial-port-in-a-class-in-python
#TODO https://python.hotexamples.com/examples/serial/Serial/write/python-serial-write-method-examples.html
                x = ser.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()
                Ax = x.split(',')
                if debug[0]:print(Ax)
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
                    if debug[0]:print(str(portEH[0])+" Neni Arduino")
            if debug[0]:print('\r')
        if 2>(len(self.joy) + len(self.B) + len(self.A)):
            print("Nenašiel som žiadne Arduino")
            return
        print("---------------")
        return

    def mathAX2(self,_X, _Y, _Z, dlzka1, dlzka2, dlzka3):  # TODO niekedy optimalizovať
        """matika na výpočet uhlov z súradníc pre 2kĺbového robota + výpočet rotácie základne s Z (roboj je v zmysle že je položený a pracovnú plochu má okolo seba)"""
        X = _X
        Y = _Y
        Z = _Z

        dlzka2 += dlzka3


        # X = 12
        # Y = 1.2
        # Z = 5
        # dlzka1 = 14.3
        # dlzka2 = 9.6

        t = dlzka2 ** 2 - dlzka1 ** 2 - X ** 2 - Y ** 2

        a = 4 * (X ** 2 + Y ** 2)
        b = 4 * Y * t
        c = t ** 2 - 4 * dlzka1 ** 2 * X ** 2

        D = b ** 2 - 4 * a * c
        print(D)

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
        if debug[0]:
            print(f'{debug[1]}\n\tT= {t}')
            print(f'\ta= {a}')
            print(f'\tb= {b}')
            print(f'\tc= {c}')
            print(f'\tD= {D}')
            print(f'\tYb1= {Yb1}')
            print(f'\tYb2= {Yb2}')
            print(f'\tXb1= {Xb1}')
            print(f'\tXb2= {Xb2}')

        alfa = degrees(atan2(Yb, Xb))
        beta = (degrees(atan2(Y - Yb, X - Xb))) - alfa + 180
        gama = degrees(atan(Z / X))

        if Z<0:
            gama = -gama

        if debug[0]: print(debug[1], str(gama), str(alfa), str(beta))
        self.u1 = gama
        self.u2 = alfa
        self.u3 = beta
        # -3689,7823,14682,25,90'

    def closeSER(self):
        self.A.close()
        self.B.close()
        self.joy.close()

    def readJOY(self):
        if self.rjoy is None:
            self.joy.write(('1' + '\r\n').encode(locale.getpreferredencoding().rstrip()))
        c = self.joy.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()
        print(c)
        if debug[0]:print(c)
        if self.rjoy != c:
            if self.rjoy is None:
                self.rjoy = c
                return
            self.rjoy = c
            x = c.split(',')
            print(x)
        return

    def ini(self):
        """funkcia na získanie portov v ktorých je Arduino a získanie dát z Arduina o samotnej ruke
        (funguje aj vo windowse☺)"""
        portEH = []
        for i, p in enumerate(ports):
            port = str(p)
            p = port.split(' ', 1)
            portEH.append(p[0])
            if debug[0]:
                print(i)
                print(f'port: {port}')
            try:
                ser = serial.Serial(portEH[i], self.baud_rate, timeout=2)
                if ser.isOpen():
                    ser.close()
                ser.open()
                x = ser.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()
                Ax = x.split(',')
                if debug[0]: print(Ax)
                if Ax[0] == 'Axel' and Ax[1] == 'Angie':
                    if debug[0]: print(f'{portEH[i]} Angie Arduino')
                    self.A = ser
                    ser.close()
                    self.A.open()
                    self.Aport = portEH[i]
                if Ax[0] == 'Axel' and Ax[1] == 'Bimbis:)':
                    if debug[0]: print(f'{portEH[i]} Bimbis Arduino')
                    self.B = ser
                    ser.close()
                    self.B.open()
                    self.Bport = portEH[i]
                if Ax[0] == 'Axel' and Ax[1] == 'joy':
                    if debug[0]: print(f'{portEH[i]} joystick Arduino')
                    ser.close()
                    self.joy = ser
                    # self.joy.open()
                    self.joyPort = portEH[i]

            except:
                pass

if __name__ == "__main__":
    ar = Axel()
    try:
        ports = list(serial.tools.list_ports.comports())
        ar.ini()
        p1 = subprocess.Popen(['python', './joy_ReadCOM.py', str(ar.joyPort), str(ar.baud_rate)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        if debug[0]:
            for _ in range(10):
                ar.rjoy = p1.stdout.readline().decode().rstrip()
                print(f'joyAR says: {ar.rjoy}')

        while True:

            # ar.joy.write(('1' + '\r\n').encode(locale.getpreferredencoding().rstrip()))
            # x = ar.joy.readline().decode(locale.getpreferredencoding().rstrip()).rstrip()
            # print(x)
            time.sleep(0.01)
            # time.sleep(2)
            # p = list(serial.tools.list_ports.comports())
            # if p != ports:
            #     ports = list(serial.tools.list_ports.comports())
            #     ar.ini()
            # ar.readJOY()
            ar.rjoy = p1.stdout.readline().decode().rstrip()



    except KeyboardInterrupt:
        print(f'A arduino: {ar.A}')
        print(f'b arduino: {ar.B}')
        print(f'joy arduino: {ar.joy}')
        ar.closeSER()
        print(f'\nAxel bol zastavený s commandom Ctrl + C\n')
        print(f'A arduino: {ar.A}')
        print(f'b arduino: {ar.B}')
        print(f'joy arduino: {ar.joy}')
        sys.exit(1)
    except Exception as e:
        ar.closeSER()
        print(f'\nExeption: {e}')
    finally:
        ar.closeSER()
        sys.exit(0)

