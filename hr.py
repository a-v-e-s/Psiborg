import serial, time
import matplotlib.pyplot as plt


def hr_monitor(name, start_time, heart_child=None, heart_lock=None):
    if heart_lock:
        heart_lock.acquire()
    
    charge_times = []
    charge_values = []
    pulse_times = []
    pulse_values = []
    ibi_times = []
    ibi_values = []

    # baud rate set by PulseSensor_BPM.ino
    BAUD = 115200
    # arduino library sets tty device node for us
    for x in range(10):
        DEV = '/dev/ttyACM' + str(x)
        try:
            siri = serial.Serial(DEV, BAUD)
            break
        except serial.serialutil.SerialException:
            pass

    try:
        siri.flushInput()
    except NameError:
        if heart_child:
            heart_child.send('Fail')
            heart_lock.release()
        raise RuntimeError('Failed to find ECG stream.')
    else:
        if heart_child:
            heart_child.send('Begin!')
            heart_lock.release()
    #
    # here we go!
    while True:
        if heart_child:
            if heart_child.poll():
                if heart_child.recv('Done!'):
                    print('Parent says Done!')
                    break
        
        bite = siri.read_until(terminator=b'\n')
        try:
            value = int(bite[1:4])
        except ValueError:
            pass
        now = time.time()
        if bite.startswith(b'S'):
            charge_times.append(now)
            charge_values.append(value)
        elif bite.startswith(b'B'):
            pulse_times.append(now)
            pulse_values.append(value)
        elif bite.startswith(b'Q'):
            if value < (ibi_values[-1] * 0.67):
                pulse_times.pop()
                pulse_values.pop()
                continue
            elif value > (ibi_values[-1] * 1.5):
                continue
            ibi_times.append(now)
            ibi_values.append(value)
        else:
            print('Received byte of unknown type.')

    siri.close()

    directory = 'EEGs/' + name.get() + '/zener/'
    plt.plot(charge_times, charge_values)
    plt.suptitle('Charge')
    plt.savefig(directory + start_time + '_ecg')
    plt.plot(pulse_times, pulse_values)
    plt.suptitle('Pulse Rate')
    plt.savefig(directory + start_time + '_pulses')
    plt.plot(ibi_times, ibi_values)
    plt.suptitle('Inter-Beat Interval')
    plt.savefig(directory + start_time + '_IBIs')


if __name__ == '__main__':
    from tkinter import StringVar
    name = StringVar()
    name.set('Jon David')
    from datetime import datetime
    hr_monitor(name, str(datetime.now()).replace(' ', '_'))