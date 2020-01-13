import tkinter as tk
from functools import partial
from random import choice
from time import time
from sqlite3 import Connection

class Game():
    def __init__(self, mode, name, mood, start_time):
        self.attempts = 0
        self.options = []
        self.data = {}

        root = tk.Tk()
        root.title('Game')
        att = tk.Label(root, text=str(self.attempts)+'/25')

        img_circle = tk.PhotoImage(master=root, file="images/circle.gif")
        self.options.append(img_circle)
        circle = tk.Canvas(root, width=141, height=169)
        circle.create_image(70, 84, image=img_circle)
        circle.grid(row=1, column=1)
        choose_circle = tk.Button(root, text="Choose", command=partial(self.human_choice, img_circle, mode, att, name, mood, root))
        choose_circle.grid(row=2, column=1)

        img_cross = tk.PhotoImage(master=root, file="images/cross.gif")
        self.options.append(img_cross)
        cross = tk.Canvas(root, width=141, height=169)
        cross.create_image(70, 84, image=img_cross)
        cross.grid(row=1, column=2)
        choose_cross = tk.Button(root, text="Choose", command=partial(self.human_choice, img_cross, mode, att, name, mood, root))
        choose_cross.grid(row=2, column=2)

        img_waves = tk.PhotoImage(master=root, file="images/waves.gif")
        self.options.append(img_waves)
        waves = tk.Canvas(root, width=141, height=169)
        waves.create_image(70, 84, image=img_waves)
        waves.grid(row=1, column=3)
        choose_waves = tk.Button(root, text="Choose", command=partial(self.human_choice, img_waves, mode, att, name, mood, root))
        choose_waves.grid(row=2, column=3)

        img_square = tk.PhotoImage(master=root, file="images/square.gif")
        self.options.append(img_square)
        square = tk.Canvas(root, width=141, height=169)
        square.create_image(70, 84, image=img_square)
        square.grid(row=1, column=4)
        choose_square = tk.Button(root, text="Choose", command=partial(self.human_choice, img_square, mode, att, name, mood, root))
        choose_square.grid(row=2, column=4)

        img_star = tk.PhotoImage(master=root, file="images/star.gif")
        self.options.append(img_star)
        star = tk.Canvas(root, width=141, height=169)
        star.create_image(70, 84, image=img_star)
        star.grid(row=1, column=5)
        choose_star = tk.Button(root, text="Choose", command=partial(self.human_choice, img_star, mode, att, name, mood, root))
        choose_star.grid(row=2, column=5)

        att.grid(row=3, column=1, columnspan=5)
        
        if mode.get() == 2:
            self.cpu_choice = choice(self.options)

        root.mainloop()


    def human_choice(self, img, mode, att, name, mood, root):
        timestamp = time()
        self.attempts += 1
        if mode.get() == 1:
            self.cpu_choice = choice(self.options)
        if img == self.cpu_choice:
            success = 1
            print('Psychic!')
        else:
            success = 0
            print('Dunce!')
        self.data[self.attempts] = [str(success), str(timestamp)]
        att.configure(text=str(self.attempts)+'/25')
        if self.attempts == 25:
            self.record_data(mode, name, mood)
            root.destroy()
        if mode.get() == 2:
            self.cpu_choice = choice(self.options)


    def record_data(self, mode, name, mood):
        for x in self.data.keys():
            print('Attempt #:', str(x))
            print(self.data[x][1] + ': ' + self.data[x][0])
        db = Connection('db.sqlite')
        curs = db.cursor()
        if mode.get() == 1:
            _type = 'zener_precognition'
        elif mode.get() == 2:
            _type = 'zener_clairvoyance'
        filepath = 'EEGs/' + name.get().replace(' ', '_') + '/zener/' +
        tests_insert = (
            'insert into Tests (Name, Mood, Type, CSV_filepath) ' +
            'Values ("'+name.get()+'", "'+mood.get('1.0', 'end')+'", "'+_type+'", "'+filepath+'");'
        )
        print(tests_insert)
        ##curs.execute(tests_insert)
        try:
            test_num = str(curs.execute('select max(Number) from Tests;').fetchall()[0][0] + 1)
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
        ##curs.execute(create_test)
        for x in self.data.keys():
            created_insert = (
                'INSERT INTO '+table_name+' (Number, Guess, Correct, Timestamp) ' +
                'Values ('+test_num+', '+str(x)+', '+self.data[x][0]+', '+self.data[x][1]+');'
            )
            print(created_insert)
        ##curs.execute(created_insert)

        curs.close()
        db.close()
