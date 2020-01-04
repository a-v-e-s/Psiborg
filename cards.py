import tkinter as tk
import functools, random

def choice(img):
    cpu_choice = random.choice(options)
    if img == cpu_choice:
        print('Psychic!')
    else:
        print('Dunce!')

root = tk.Tk()
options = []

img_circle = tk.PhotoImage(file="images/circle.gif")
options.append(img_circle)
circle = tk.Canvas(root, width=141, height=169)
circle.create_image(75, 75, image=img_circle)
circle.grid(row=1, column=1)
choose_circle = tk.Button(root, text="Choose", command=functools.partial(choice, img_circle))
choose_circle.grid(row=2, column=1)

img_cross = tk.PhotoImage(file="images/cross.gif")
options.append(img_cross)
cross = tk.Canvas(root, width=141, height=169)
cross.create_image(75, 75, image=img_cross)
cross.grid(row=1, column=2)
choose_cross = tk.Button(root, text="Choose", command=functools.partial(choice, img_cross))
choose_cross.grid(row=2, column=2)

img_waves = tk.PhotoImage(file="images/waves.gif")
options.append(img_waves)
waves = tk.Canvas(root, width=141, height=169)
waves.create_image(75, 75, image=img_waves)
waves.grid(row=1, column=3)
choose_waves = tk.Button(root, text="Choose", command=functools.partial(choice, img_waves))
choose_waves.grid(row=2, column=3)

img_square = tk.PhotoImage(file="images/square.gif")
options.append(img_square)
square = tk.Canvas(root, width=141, height=169)
square.create_image(75, 75, image=img_square)
square.grid(row=1, column=4)
choose_square = tk.Button(root, text="Choose", command=functools.partial(choice, img_square))
choose_square.grid(row=2, column=4)

img_star = tk.PhotoImage(file="images/star.gif")
options.append(img_star)
star = tk.Canvas(root, width=141, height=169)
star.create_image(75, 75, image=img_star)
star.grid(row=1, column=5)
choose_star = tk.Button(root, text="Choose", command=functools.partial(choice, img_star))
choose_star.grid(row=2, column=5)

root.mainloop()