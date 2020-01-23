import os
import tkinter as tk
from functools import partial
from zener import Game
from threading import Thread
from multiprocessing import Process, Pipe, Lock
from neurofeedback import feedback
from hr import hr_monitor
from datetime import datetime

class Games():
    def __init__(self):
        root = tk.Tk()
        root.title('Control Panel')

        l_name = tk.Label(root, text='Name: ')
        l_name.grid(row=1, column=1)
        name = tk.Entry(root, width=50, bg='white', fg='black')
        name.grid(row=1, column=2, columnspan=3)

        mode = tk.IntVar()
        l_type = tk.Label(root, text='Game Options:')
        l_type.grid(row=2, column=1, columnspan=4)
        l_h1 = tk.Label(root, text='Human Chooses First:')
        l_h1.grid(row=3, column=1)
        h1 = tk.Radiobutton(root, variable=mode, value=1, fg='black')
        h1.grid(row=3, column=2)
        l_c1 = tk.Label(root, text='Computer Chooses First:')
        l_c1.grid(row=3, column=3)
        c1 = tk.Radiobutton(root, variable=mode, value=2, fg='black')
        c1.grid(row=3, column=4)

        l_mood = tk.Label(root, text='Please briefly describe your state of mind:')
        l_mood.grid(row=4, column=1, columnspan=4)
        mood = tk.Text(root, height=5, width=50, wrap='word', bg='white', fg='black')
        mood.grid(row=5, column=1, columnspan=4)

        eeg = tk.IntVar()
        record = tk.IntVar()
        ecg = tk.IntVar()
        l_confirm = tk.Label(root, text='Confirm good EEG connection:')
        l_confirm.grid(row=6, column=1, columnspan=2)
        confirm = tk.Checkbutton(root, variable=eeg, offvalue=0, onvalue=1, fg='black')
        confirm.grid(row=6, column=3, columnspan=2)
        l_confirm2 = tk.Label(root, text='Confirm recording via muselsl+record and/or neurofeedback.py:')
        l_confirm2.grid(row=7, column=1, columnspan=2)
        confirm2 = tk.Checkbutton(root, variable=record, offvalue=0, onvalue=1, fg='black')
        confirm2.grid(row=7, column=3, columnspan=2)
        l_confirm3 = tk.Label(root, text='ECG connected or skipped?')
        l_confirm3.gri(row=8, column=1, columnspan=2)
        confirm3 = tk.Checkbutton(root, variable=ecg, offvalue=0, onvalue=1, fg='black')
        confirm3.grid(row=8, column=3, columnspan=2)

        start = tk.Button(root, text='Start Test!', command=partial(self.validate, mode, eeg, record, ecg, name, mood))
        start.grid(row=9, column=2)
        stop = tk.Button(root, text='Quit', command=root.destroy)
        stop.grid(row=9, column=3)

        name.focus_set()
        root.mainloop()
    
    def validate(self, mode, eeg, record, ecg, name, mood):
        if eeg.get() != 1:
            raise ValueError('You must confirm a good EEG connection!')
        if record.get() != 1:
            raise ValueError('You must confirm that EEG data is recording!')
        if ecg.get() != 1:
            raise ValueError('You must confirm that ECG is connected or is being skipped!')
        if mode.get() == 0:
            raise ValueError('You must choose a game mode!')
        if name.get() == '':
            raise ValueError('You must enter a name!')
        if mood.get('1.0', 'end') == '' or mood.get('1.0', 'end') == '':
            raise ValueError('You must describe your state of mind')

        self.begin(mode, name, mood)
    
    def begin(self, mode, name, mood):
        if name.get().replace(' ', '_') not in os.listdir('EEGs'):
            os.mkdir('EEGs/' + name.get().replace(' ', '_'))
            os.mkdir('EEGs/' + name.get().replace(' ', '_') + '/zener/')
        elif 'zener' not in os.listdir('EEGs/' + name.get().replace(' ', '_')):
            os.mkdir('EEGs/' + name.get().replace(' ', '_') + '/zener/')
        start_time = str(datetime.now()).replace(' ', '_')

        brain_parent, brain_child = Pipe()
        heart_parent, heart_child = Pipe()
        brain_lock = Lock()
        heart_lock = Lock()

        print('starting neurofeedback')
        p1 = Process(target=feedback, args=(name, start_time, brain_child, brain_lock))
        p1.start()
        if brain_parent.recv() == 'Fail':
            raise RuntimeError('Failed to find EEG stream.')
        else:
            print('Found EEG stream, continuing...')
        
        print('starting ecg feedback')
        p2 = Process(target=hr_monitor, args=(name, start_time, heart_child, heart_lock))
        p2.start()
        if heart_parent.recv() == 'Fail':
            raise RuntimeError('Failed to find ECG stream.')
        else:
            print('Found ECG stream, continuing...')

        t1 = Thread(target=Game, args=(mode, name, mood, start_time, brain_parent, heart_parent))
        t1.start()


if __name__ == '__main__':
    Games()