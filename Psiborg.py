import pexpect
import tkinter as tk
from getpass import getuser
from threading import Thread
from src import *

class Control_Panel():
    def __init__(self):
        root = tk.Tk()
        root.title('Control Panel')

        self.eeg = tk.IntVar()
        self.ekg = tk.IntVar()
        self.gsr = tk.IntVar()
        tk.Label(root, text='Collect EEG data?').grid(row=1, column=1, columnspan=2)
        self.check_eeg = tk.Checkbutton(root, variable=eeg, offvalue=0, onvalue=1, command=eeg_init)
        self.check_eeg.grid(row=1, column=3)
        tk.Label(root, text='Collect EKG data?').grid(row=2, column=1, columnspan=2)
        self.check_ekg = tk.Checkbutton(root, variable=ekg, offvalue=0, onvalue=1, command=ekg_init)
        self.check_ekg.grid(row=2, column=3)
        tk.Label(root, text='Collect GSR data?').grid(row=3, column=1, columnspan=2)
        self.check_gsr = tk.Checkbutton(root, variable=gsr, offvalue=0, onvluae=1, command=gsr_init)
        self.check_gsr.grid(row=3, column=3)

        self.notes = tk.Text(root, height=5, width=50, wrap='word', bg='white', fg='black')
        self.notes.grid(row=4, column=1, columnspan=3)

        self.alerts = tk.Label(root, text='')
        self.alerts.grid(row=5, column=1, columnspan=2)

        self.start = tk.Button(root, text='Begin Game!', state='disabled', command=self.begin)
        self.start.grid(row=6, column=1)
        self.analyze = tk.Button(root, text='Conduct Analysis', command=self.run_analysis)
        self.analyze.grid(row=6, column=2)
        self.quit = tk.Button(root, text='Quit', command=root.destroy)
        self.quit.grid(row=6, column=3)

        root.mainloop()
    

    def eeg_init(self):
        self.start.config(state='disabled')
        user = getuser()
        command = 'python3 -m muselsl stream'
        child = pexpect.spawn(command)
        try:
            child.expect(user)
        except pexpect.TIMEOUT:
            self.alerts.config(
                'Command timed out.\n'
                'Is bluetooth turned off?\n'
                'Did you already ' + command + '?\n'
                'Are you running this program as root?'
            )
        else:
            try:
                child.sendline(self.pw.get())
            except NameError:
                self.password_getter()
                child.sendline(self.pw.get())
        index = child.expect([
            'Streaming EEG...',
            'No muses found.',
            "Can't init device hci0: Connection timed out (110)"
        ])
        if index == 1:
            self.alerts.config(text='Streaming EEG')
            self.start.config(state='normal')
        elif index == 2:
            self.alerts.config(text='Muse not found.')
        elif index == 3:
            self.alerts.config(text="Can't init hci0. Is bluetooth turned off?")


    def ekg_init(self):
        self.start.config(state='disabled')
        user = getuser()
        command = 'sudo chown ' + user + ":" + user + ' /dev/ttyACM0'
        child = pexpect.spawn(command)
        try:
            child.expect(user)
        except pexpect.TIMEOUT:
            self.alerts.config(
                'Command timed out.\n'
                'Is arduino plugged in?\n'
                'Did you already ' + command + '?\n'
                'Are you running this program as root?'
            )
        else:
            try:
                child.sendline(self.pw.get())
            except NameError:
                self.password_getter()
                child.sendline(self.pw.get())
        self.start.config(state='normal')


    def gsr_init(self):
        #self.start.config(state='disabled')
        # do stuff
        #self.start.config(state='normal')
        pass
        
    
    def pw_getter(self):
        password_getter = tk.Toplevel()
        tk.Label(password_getter, text='Enter password here:').pack()
        self.pw = tk.StringVar()
        tk.Entry(password_getter, textvariable=pw, width=50).pack()
        tk.Button(password_getter, text='Done',
            command=password_getter.destroy)
        ).pack()

        password_getter.mainloop()

    def begin(self):
        pass

    
    def run_analysis(self):
        pass


if __name__ == '__main__':
    Control_Panel()