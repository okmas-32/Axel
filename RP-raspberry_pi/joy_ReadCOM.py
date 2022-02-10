import subprocess
import sys
import serial

try:
    #inicializuje sériovú komunikáciu
    ser = serial.Serial(port=sys.argv[1], baudrate=int(sys.argv[2]), timeout=2)

    #uistím sa že je port otvorený
    if ser.isOpen():
        ser.close()
    ser.open()

    #prečítam čo mi napísal z jeho setup()
    ser.readline()

    #napíšem mu 1 aby začal s posielaním dát o joisticku
    ser.write(b'A\r\n')

    #čítam dáta ktoré posiela
    while True:  # The program never ends... will be killed when master is over.
        output = ser.readline().decode('utf-8') # read output
        sys.stdout.write(output) # write output to stdout
        sys.stdout.flush()

except Exception as e:
    #ak je nejaký eror tak ho iba vypíše do "výstupu" tohoto bloku kódu
    sys.stdout.write(e)
    sys.stdout.flush()

except subprocess.STDOUT:
    ser.close()

finally:
    #keď dokončí čo má tak zatvorý seriový port
    ser.close()