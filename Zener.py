import threading, multiprocessing
import tkinter as tk
from functools import partial
from random import choice
import time, sqlite3
#from cards import game

options = []
data = {}
global cpu_choice, attempts
attempts = 0

def human_choice(img, mode, att, root):
    timestamp = time.time()
    global cpu_choice, attempts
    attempts += 1
    if mode.get() == 1:
        cpu_choice = choice(options)
    if img == cpu_choice:
        success = 1
        print('Psychic!')
    else:
        success = 0
        print('Dunce!')
    data[str(attempts)] = [str(success), str(timestamp)]
    att.configure(text=str(attempts)+'/25')
    if attempts == 25:
        record_data()
        root.destroy()
    if mode.get() == 2:
        cpu_first()


def cpu_first():
    global cpu_choice
    cpu_choice = choice(options)


def test(mode, eeg, name, mood):
    if eeg.get() != 1:
        raise ValueError('You must confirm a good EEG connection')
    if mode.get() == 0:
        raise ValueError('You must choose a game mode')
    if name.get() == '':
        raise ValueError('You must enter a name')
    if mood.get('1.0', 'end') == '' or mood.get('1.0', 'end') == 'Please briefly describe your state of mind:':
        raise ValueError('You must describe your state of mind')
    if mode.get() == 2:
        cpu_first()
    p = threading.Thread(target=game, args=(mode,))
    p.start()


def record_data():
    db = sqlite3.Connection('db.sqlite')
    curs = db.cursor()
    if mode.get() == 1:
        _type = 'zener_precognition'
    elif mode.get() == 2:
        _type = 'zener_clairvoyance'
    filepath = 'i dunno yet'
    tests_insert = 'insert into Tests (Name, Mood, Type, CSV_filepath) Values ("' + name.get() + '", "' + mood.get() + '", "' + _type + '", "' + filepath + '");'
    print(tests_insert)
    #curs.execute(tests_insert)
    try:
        test_num = str(curs.execute('select max(Number) from Tests').fetchall()[0][0] + 1)
    except TypeError:
        test_num = '1'
    table_name = 'test' + test_num
    create_test = """
    CREATE TABLE """ + table_name + """(
    Number INTEGER NOT NULL,
    Guess INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Correct INTEGER NOT NULL,
    Timestamp REAL NOT NULL
    );"""
    print(create_test)
    #curs.execute(create_test)
    created_insert = 'insert into ' + table_name + ' (Number, Guess, Correct, Timestamp) Values (' + test_num + ', ')
    print(created_insert)
    #curs.execute(created_insert)

    curs.close()
    db.close()



def game(mode):
    root = tk.Tk()
    root.title('Game')
    att = tk.Label(root, text=str(attempts)+'/25')

    img_circle = tk.PhotoImage(master=root, file="images/circle.gif")
    options.append(img_circle)
    circle = tk.Canvas(root, width=141, height=169)
    circle.create_image(70, 84, image=img_circle)
    circle.grid(row=1, column=1)
    choose_circle = tk.Button(root, text="Choose", command=partial(human_choice, img_circle, mode, att, root))
    choose_circle.grid(row=2, column=1)

    img_cross = tk.PhotoImage(master=root, file="images/cross.gif")
    options.append(img_cross)
    cross = tk.Canvas(root, width=141, height=169)
    cross.create_image(70, 84, image=img_cross)
    cross.grid(row=1, column=2)
    choose_cross = tk.Button(root, text="Choose", command=partial(human_choice, img_cross, mode, att, root))
    choose_cross.grid(row=2, column=2)

    img_waves = tk.PhotoImage(master=root, file="images/waves.gif")
    options.append(img_waves)
    waves = tk.Canvas(root, width=141, height=169)
    waves.create_image(70, 84, image=img_waves)
    waves.grid(row=1, column=3)
    choose_waves = tk.Button(root, text="Choose", command=partial(human_choice, img_waves, mode, att, root))
    choose_waves.grid(row=2, column=3)

    img_square = tk.PhotoImage(master=root, file="images/square.gif")
    options.append(img_square)
    square = tk.Canvas(root, width=141, height=169)
    square.create_image(70, 84, image=img_square)
    square.grid(row=1, column=4)
    choose_square = tk.Button(root, text="Choose", command=partial(human_choice, img_square, mode, att, root))
    choose_square.grid(row=2, column=4)

    img_star = tk.PhotoImage(master=root, file="images/star.gif")
    options.append(img_star)
    star = tk.Canvas(root, width=141, height=169)
    star.create_image(70, 84, image=img_star)
    star.grid(row=1, column=5)
    choose_star = tk.Button(root, text="Choose", command=partial(human_choice, img_star, mode, att, root))
    choose_star.grid(row=2, column=5)

    att.grid(row=3, column=1, columnspan=5)

    root.mainloop()


def master():
    root = tk.Tk()
    root.title('Control Panel')

    l_name = tk.Label(root, text='Name: ')
    l_name.grid(row=1, column=1)
    name = tk.Entry(root, bg='white', width=50)
    name.grid(row=1, column=2, columnspan=3)

    mode = tk.IntVar()
    l_type = tk.Label(root, text='Game Options:')
    l_type.grid(row=2, column=1, columnspan=4)
    l_h1 = tk.Label(root, text='Human Chooses First:')
    l_h1.grid(row=3, column=1)
    h1 = tk.Radiobutton(root, variable=mode, value=1)
    h1.grid(row=3, column=2)
    l_c1 = tk.Label(root, text='Computer Chooses First:')
    l_c1.grid(row=3, column=3)
    c1 = tk.Radiobutton(root, variable=mode, value=2)
    c1.grid(row=3, column=4)

    l_mood = tk.Label(root, text='Please briefly describe your state of mind:')
    l_mood.grid(row=4, column=1, columnspan=4)
    mood = tk.Text(root, height=5, width=50, bg='white', wrap='word')
    mood.grid(row=5, column=1, columnspan=4)

    eeg = tk.IntVar()
    l_confirm = tk.Label(root, text='Confirm good EEG connection:')
    l_confirm.grid(row=6, column=1, columnspan=2)
    confirm = tk.Checkbutton(root, variable=eeg, offvalue=0, onvalue=1)
    confirm.grid(row=6, column=3, columnspan=2)

    start = tk.Button(root, text='Start Test!', command=partial(test, mode, eeg, name, mood))
    start.grid(row=7, column=2)
    stop = tk.Button(root, text='Quit', command=root.destroy)
    stop.grid(row=7, column=3)

    name.focus_set()
    root.mainloop()


if __name__ == '__main__':
    master()