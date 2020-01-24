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
        h1 = tk.Radiobutton(root, variable=mode, value=1, fg='black', padx=5, pady=y)
        h1.grid(row=3, column=2)
        l_c1 = tk.Label(root, text='Computer Chooses First:')
        l_c1.grid(row=3, column=3)
        c1 = tk.Radiobutton(root, variable=mode, value=2, fg='black', padx=5, pady=y)
        c1.grid(row=3, column=4)

        l_mood = tk.Label(root, text='Please briefly describe your state of mind:')
        l_mood.grid(row=4, column=1, columnspan=4)
        mood = tk.Text(root, height=5, width=50, wrap='word', bg='white', fg='black')
        mood.grid(row=5, column=1, columnspan=4)

        eeg = tk.IntVar()
        record = tk.IntVar()
        ekg = tk.IntVar()
        game_length = tk.StringVar()
        l_confirm = tk.Label(root, text='Confirm good EEG connection:')
        l_confirm.grid(row=6, column=1, columnspan=2)
        confirm = tk.Checkbutton(root, variable=eeg, offvalue=0, onvalue=1, fg='black')
        confirm.grid(row=6, column=3, columnspan=2, padx=5, pady=y)
        l_confirm2 = tk.Label(root, text='Confirm recording via muselsl+record and/or neurofeedback.py:')
        l_confirm2.grid(row=7, column=1, columnspan=2)
        confirm2 = tk.Checkbutton(root, variable=record, offvalue=0, onvalue=1, fg='black')
        confirm2.grid(row=7, column=3, columnspan=2, padx=5, pady=y)
        l_confirm3 = tk.Label(root, text='EKG connected?')
        l_confirm3.grid(row=8, column=1, columnspan=2)
        confirm3 = tk.Checkbutton(root, variable=ekg, offvalue=0, onvalue=1, fg='black')
        confirm3.grid(row=8, column=3, columnspan=2, padx=5, pady=y)
        l_length = tk.Label(root, text='Game Length:')
        l_length.grid(row=9, column=1, columnspan=2)
        length = tk.Spinbox(root, textvariable=game_length, width=5, from_=25, to=250, increment=25)
        length.grid(row=9, column=3, columnspan=2, padx=5, pady=y)

        start = tk.Button(root, text='Start Test!', command=partial(self.validate, mode, game_length eeg, record, ekg, name, mood))
        start.grid(row=9, column=2)
        stop = tk.Button(root, text='Quit', command=root.destroy)
        stop.grid(row=9, column=3)

        name.focus_set()
        root.mainloop()
    
    def validate(self, mode, game_length, eeg, record, ekg, name, mood):
        if eeg.get() != 1:
            raise ValueError('You must confirm a good EEG connection!')
        if record.get() != 1:
            raise ValueError('You must confirm that EEG data is recording!')
        if mode.get() == 0:
            raise ValueError('You must choose a game mode!')
        if name.get() == '':
            raise ValueError('You must enter a name!')
        if mood.get('1.0', 'end') == '' or mood.get('1.0', 'end') == '':
            raise ValueError('You must describe your state of mind')

        self.begin(mode, game_length, name, mood, ekg)
    
    def begin(self, mode, game_length, name, mood, ekg):
        if name.get().replace(' ', '_') not in os.listdir('Biofeedback'):
            os.mkdir('Biofeedback/' + name.get().replace(' ', '_'))
            os.mkdir('Biofeedback/' + name.get().replace(' ', '_') + '/zener/')
        elif 'zener' not in os.listdir('Biofeedback/' + name.get().replace(' ', '_')):
            os.mkdir('Biofeedback/' + name.get().replace(' ', '_') + '/zener/')
        start_time = str(datetime.now()).replace(' ', '_')[:-7]
        os.mkdir('Biofeedback/' + name.get().replace(' ', '_') + '/zener/' + start_time)

        brain_parent, brain_child = Pipe()
        brain_lock = Lock()

        print('starting neurofeedback')
        p1 = Process(target=feedback, args=(name, start_time, brain_child, brain_lock))
        p1.start()
        brain_parent.poll(60)
        if brain_parent.recv() == False:
            raise RuntimeError('Failed to find EEG stream.')
        else:
            print('Found EEG stream, continuing...')
        
        if ekg.get() == 1:
            heart_parent, heart_child = Pipe()
            heart_lock = Lock()
            print('starting ekg feedback')
            p2 = Process(target=hr_monitor, args=(name, start_time, heart_child, heart_lock))
            p2.start()
            heart_parent.poll(60)
            if heart_parent.recv() == False:
                raise RuntimeError('Failed to find EKG stream.')
            else:
                print('Found EKG stream, continuing...')

            t1 = Thread(target=Game, args=(mode, game_length, name, mood, start_time, brain_parent, heart_parent))
        else:
            t1 = Thread(target=Game, args=(mode, game_length, name, mood, start_time, brain_parent))
        
        t1.start()


if __name__ == '__main__':
    Games()