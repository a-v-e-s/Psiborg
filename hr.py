import serial, time, pickle, time
import matplotlib.pyplot as plt

def heart_poll():
    pass

def timer():
    pass
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
            heart_child.send(False)
            heart_lock.release()
        raise RuntimeError('Failed to find EKG stream.')
    else:
        if heart_child:
            heart_child.send(True)
            heart_lock.release()
        else: start = time.time()
    #
    # here we go!
    data = {}
    while True:
        if heart_child:
            if heart_child.poll():
                if heart_child.recv() == 'Done!':
                    print('Parent says Done!')
                    break
        else:
            now = time.time()
            if now - start > 60:
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
            data[now] = bite[:4]
        elif bite.startswith(b'B'):
            pulse_times.append(now)
            pulse_values.append(value)
            data[now] = bite[:4]
        elif bite.startswith(b'Q'):
            try: # try to get rid of crap input:
                if value < (ibi_values[-1] * 0.67):
                    pulse_times.pop()
                    pulse_values.pop()
                    continue
                elif value > (ibi_values[-1] * 1.5):
                    continue
            except IndexError:
                pass
            ibi_times.append(now)
            ibi_values.append(value)
            data[now] = bite[:4]
        else:
            print('Received byte of unknown type.')

    # could this line be the reason my laptop was freezing??
    siri.close()

    if heart_child:
        directory = 'Biofeedback/' + name.get().replace(' ', '_') + '/zener/' + start_time + '/'
    else:
        directory = 'Biofeedback/' + name.get().replace(' ', '_') + '/' + start_time + '/'
    
    print('length of charge_times:', len(charge_times), sep='\n')
    print('length of charge_values:', len(charge_values), sep='\n')
    print('length of pulse_times:', len(pulse_times), sep='\n')
    print('length of pulse_values:', len(pulse_values), sep='\n')
    print('length of ibi_times:', len(ibi_times), sep='\n')
    print('length of ibi_values:', len(ibi_values), sep='\n')
    """
    This might be too much data to handle all at once like this:
    plt.plot(charge_times, charge_values)
    plt.suptitle('Charge')
    plt.savefig(directory + '_ekg')
    plt.plot(pulse_times, pulse_values)
    plt.suptitle('Pulse Rate')
    plt.savefig(directory + '_pulses')
    plt.plot(ibi_times, ibi_values)
    plt.suptitle('Inter-Beat Interval')
    plt.savefig(directory + '_IBIs')
    """

    pkl_name = directory + 'ekg.pkl'
    with open(pkl_name, 'wb') as f:
        pickle.dump(data, f)


if __name__ == '__main__':
    import tkinter, os
    from datetime import datetime
    root = tkinter.Tk()
    name_ = tkinter.StringVar(root)
    name = input('Enter your name:\n').replace(' ', '_')
    name_.set(name)
    start_time = str(datetime.now()).replace(' ', '_')[:-7]
    
    if name not in os.listdir('Biofeedback'):
        os.mkdir('Biofeedback/' + name)
    os.mkdir('Biofeedback/' + name + '/' + start_time)

    hr_monitor(name_, start_time)