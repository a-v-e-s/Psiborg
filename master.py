import tkinter as tk
from functools import partial
from zener import Game
from threading import Thread

class Master():
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
        l_confirm = tk.Label(root, text='Confirm good EEG connection:')
        l_confirm.grid(row=6, column=1, columnspan=2)
        confirm = tk.Checkbutton(root, variable=eeg, offvalue=0, onvalue=1, fg='black')
        confirm.grid(row=6, column=3, columnspan=2)

        start = tk.Button(root, text='Start Test!', command=partial(self.validate, mode, eeg, name, mood))
        start.grid(row=7, column=2)
        stop = tk.Button(root, text='Quit', command=root.destroy)
        stop.grid(row=7, column=3)

        name.focus_set()
        root.mainloop()
    
    def validate(self, mode, eeg, name, mood):
        if eeg.get() != 1:
            raise ValueError('You must confirm a good EEG connection')
        if mode.get() == 0:
            raise ValueError('You must choose a game mode')
        if name.get() == '':
            raise ValueError('You must enter a name')
        if mood.get('1.0', 'end') == '' or mood.get('1.0', 'end') == 'Please briefly describe your state of mind:':
            raise ValueError('You must describe your state of mind')
        t = Thread(target=Game, args=(mode, name, mood))
        t.start()


if __name__ == '__main__':
    Master()