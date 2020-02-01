import pexpect, os, shutil, time
import tkinter as tk
from getpass import getuser
from threading import Thread
from multiprocessing import Process, Pipe, Lock
from subprocess import Popen, PIPE
from sys import exc_info
import muselsl.stream as stream
from muselsl.stream import find_muse
from src import *


class Control_Panel():
    def __init__(self):
        if os.getuid() != 0:
            raise PermissionError('You must execute this as root!')

        root = tk.Tk()
        root.title('Control Panel')

        self.eeg = tk.IntVar()
        self.ekg = tk.IntVar()
        self.gsr = tk.IntVar()
        self.pw = tk.StringVar(value='')
        tk.Label(root, text='Collect EEG data?').grid(row=1, column=1, columnspan=2)
        self.check_eeg = tk.Checkbutton(root, variable=self.eeg, offvalue=0, onvalue=1, command=self.eeg_init)
        self.check_eeg.grid(row=1, column=3)
        tk.Label(root, text='Collect EKG data?').grid(row=2, column=1, columnspan=2)
        self.check_ekg = tk.Checkbutton(root, variable=self.ekg, offvalue=0, onvalue=1, command=self.ekg_init)
        self.check_ekg.grid(row=2, column=3)
        tk.Label(root, text='Collect GSR data?').grid(row=3, column=1, columnspan=2)
        self.check_gsr = tk.Checkbutton(root, variable=self.gsr, offvalue=0, onvalue=1, command=self.gsr_init)
        self.check_gsr.grid(row=3, column=3)

        tk.Label(root, text='Recording Notes:').grid(row=4, column=1, columnspan=4)
        self.notes = tk.Text(root, height=5, width=50, wrap='word', bg='white', fg='black')
        self.notes.grid(row=5, column=1, columnspan=4)

        self.alerts = tk.Label(root, text='', fg='red')
        self.alerts.grid(row=6, column=1, columnspan=4)

        self.start_recording = tk.Button(root, text='Begin Recording', state='disabled', command=self.begin_recording)
        self.start_recording.grid(row=7, column=1)
        self.start_game = tk.Button(root, text='Begin Game!', state='disabled', command=self.begin_game)
        self.start_game.grid(row=7, column=2)
        self.analyze = tk.Button(root, text='Conduct Analysis', state='disabled', command=self.run_analysis)
        self.analyze.grid(row=7, column=3)
        self.quit = tk.Button(root, text='Quit', command=root.destroy)
        self.quit.grid(row=7, column=4)

        root.mainloop()
    

    def eeg_init(self):
        if self.eeg.get() == 1:
            print('Attempting...')
            self.alerts.config(text='Looking for Muse...') # why does this not work??
            Popen(['python3', '-m', 'muselsl', 'stream'])
            time.sleep(15)
            try:
                self.alerts.config(text='Looking for EEG stream...')
                Popen(['python3', '-m', 'muselsl', 'view', '-b', 'Qt5Agg'])
            except RuntimeError:
                self.alerts.config(text="Can't find EEG stream.\nPlease deselect eeg checkbox.")
                #self.check_eeg.deselect() doesn't work. checkbox selected after function exits.
            else:
                self.start_game.config(state='normal')
                self.start_recording.config(state='normal')
        elif self.eeg.get() == 0 and self.ekg.get() == 0 and self.gsr.get() == 0:
                self.start_game.config(state='disabled')
                self.start_recording.config(state='disabled')


    def ekg_init(self):
        if self.ekg.get() == 1:
            user = getuser()
            command = 'sudo chown ' + user + ":" + user + ' /dev/ttyACM0'
            self.alerts.config(text='Running "' + command + '"\nPlease wait...')
            try:
                shutil.chown('/dev/ttyACM0', user=user, group=user)
            except Exception:
                print(exc_info())
            else:
                self.start_game.config(state='normal')
                self.start_recording.config(state='normal')
        elif self.eeg.get() == 0 and self.ekg.get() == 0 and self.gsr.get() == 0:
                self.start_game.config(state='disabled')
                self.start_recording.config(state='disabled')


    def gsr_init(self):
        #self.start_game.config(state='disabled')
        #self.start_recording.config(state='disabled')
        # do stuff
        #
        #if None:
        #    self.begin_game.config(state='normal')
        #    self.begin_recording.config(state='normal')
        pass
        
    
    """
    def password_getter(self):
        password_getter = tk.Toplevel()
        pw = tk.StringVar()
        tk.Label(password_getter, text='Enter password here:').pack()
        tk.Entry(password_getter, textvariable=pw, width=50).pack()
        tk.Button(password_getter, text='Done',
            command=[self.pw.set(pw), password_getter.destroy]
        ).pack()

        password_getter.mainloop()
    """


    def begin_game(self):
        #if self.eeg.get() == 1 and self.ekg.get() == 1 and self.gsr.get() == 1:
        #    raise RuntimeError('You must collect at least some Biofeedback data!')
        pass


    def begin_recording(self):
        #if self.eeg.get() == 1 and self.ekg.get() == 1 and self.gsr.get() == 1:
        #    raise RuntimeError('You must collect at least some Biofeedback data!')
        pass

    
    def run_analysis(self):
        pass


if __name__ == '__main__':
    Control_Panel()