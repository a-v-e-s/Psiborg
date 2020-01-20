import serial, time
import matplotlib.pyplot as plt

# baud rate set by PulseSensor_BPM.ino
BAUD = 115200
# arduino source code sets this for us
for x in range(10):
    DEV = '/dev/ttyACM' + str(x)
    try:
        siri = serial.Serial(DEV, BAUD)
        break
    except serial.serialutil.SerialException:
        pass

# figure out how to plot data and stuff:
# fig, ax = plt.subplots()

try:
    siri.flushInput()
except NameError:
    print('Could not initialize Serial connection on /dev/ttyACM[0-9]')
    exit()

count = 0
start_time = time.time()
while time.time() - start_time < 60:
    bite = siri.read_until(terminator=b'\n')
    try:
        value = int(bite[1:4])
    except ValueError:
        pass
    now = time.time()
    if bite.startswith(b'S'):
        #i need to figure out what the flip this means.
        print('Sensor value:', value)
        # fig.plotstuff(args)
    if bite.startswith(b'B'):
        print('Heart Rate value:', value)
        # fig.plotstuff(args)
    if bite.startswith(b'Q'):
        print('IBI value:', value)
        # fig.plotstuff(args)
    count += 1

pyl.show()

# do cool stuff above here, then:
siri.close()