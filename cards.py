import tkinter as tk
import functools, random

global cpu_choice, successes, attempts
successes, attempts = 0, 0
options = []

def human_choice(img, mode, ratio, wins, tries):
    global cpu_choice, successes, attempts
    attempts += 1
    if mode.get() == 1:
        cpu_choice = random.choice(options)
    if img == cpu_choice:
        successes += 1
        print('Psychic!')
    else:
        print('Dunce!')
    ratio.configure(text=str(successes / attempts))
    wins.configure(text=str(successes))
    tries.configure(text=str(attempts))
    if mode.get() == 2:
        cpu_first()

def cpu_first():
    global cpu_choice
    cpu_choice = random.choice(options)

root = tk.Tk()
ratio = tk.Label(root, text="?")
wins = tk.Label(root, text="?")
tries = tk.Label(root, text="?")

mode = tk.IntVar()
tk.Label(root, text="precognition/remote influence").grid(row=1, column=1)
pre = tk.Radiobutton(root, variable=mode, value=1)
pre.grid(row=1, column=2)
tk.Label(root, text="clairvoyance").grid(row=1, column=3)
post = tk.Radiobutton(root, variable=mode, value=2, command=cpu_first)
post.grid(row=1, column=4)
pre.select()

img_circle = tk.PhotoImage(file="images/circle.gif")
options.append(img_circle)
circle = tk.Canvas(root, width=141, height=169)
circle.create_image(70, 84, image=img_circle)
circle.grid(row=2, column=1)
choose_circle = tk.Button(root, text="Choose", command=functools.partial(human_choice, img_circle, mode, ratio, wins, tries))
choose_circle.grid(row=3, column=1)

img_cross = tk.PhotoImage(file="images/cross.gif")
options.append(img_cross)
cross = tk.Canvas(root, width=141, height=169)
cross.create_image(70, 84, image=img_cross)
cross.grid(row=2, column=2)
choose_cross = tk.Button(root, text="Choose", command=functools.partial(human_choice, img_cross, mode, ratio, wins, tries))
choose_cross.grid(row=3, column=2)

img_waves = tk.PhotoImage(file="images/waves.gif")
options.append(img_waves)
waves = tk.Canvas(root, width=141, height=169)
waves.create_image(70, 84, image=img_waves)
waves.grid(row=2, column=3)
choose_waves = tk.Button(root, text="Choose", command=functools.partial(human_choice, img_waves, mode, ratio, wins, tries))
choose_waves.grid(row=3, column=3)

img_square = tk.PhotoImage(file="images/square.gif")
options.append(img_square)
square = tk.Canvas(root, width=141, height=169)
square.create_image(70, 84, image=img_square)
square.grid(row=2, column=4)
choose_square = tk.Button(root, text="Choose", command=functools.partial(human_choice, img_square, mode, ratio, wins, tries))
choose_square.grid(row=3, column=4)

img_star = tk.PhotoImage(file="images/star.gif")
options.append(img_star)
star = tk.Canvas(root, width=141, height=169)
star.create_image(70, 84, image=img_star)
star.grid(row=2, column=5)
choose_star = tk.Button(root, text="Choose", command=functools.partial(human_choice, img_star, mode, ratio, wins, tries))
choose_star.grid(row=3, column=5)

tk.Label(root, text="Success Ratio:").grid(row=4, column=1)
tk.Label(root, text="Successes:").grid(row=4, column=2)
tk.Label(root, text="Attempts:").grid(row=4, column=3)
ratio.grid(row=5, column=1)
wins.grid(row=5, column=2)
tries.grid(row=5, column=3)

root.mainloop()