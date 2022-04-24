
from subprocess import STDOUT
from sys import stdout, argv

try:
    #inicializuje sériovú komunikáciu
    ser = serial.Serial(port=argv[1], baudrate=int(argv[2]), timeout=2)
    ser.flushInput()
    #prečítam čo mi napísal z jeho setup()
    ser.readline()
    ser.flushInput()
    #napíšem mu 1 aby začal s posielaním dát o joisticku
    b = b'A\r\n'
    ser.write(b)
    #čítam dáta ktoré posiela
    while True:  # The program never ends... will be killed when master is over.
        output = ser.readline().decode('utf-8') # read output
        stdout.flush()
        stdout.write(output) # write output to stdout

except Exception as e:
    #ak je nejaký eror tak ho iba vypíše do "výstupu" tohoto bloku kódu
    stdout.write(e)
    stdout.flush()

except STDOUT:
    ser.close()

finally:
    #keď dokončí čo má tak zatvorý seriový port
    ser.close()