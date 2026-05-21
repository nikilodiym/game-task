from tkinter import *
from game import attack_monster

root = Tk()
root.title("Monster Guild")
root.geometry("600x400")

hero_hp = Label(root, text="Hero HP: 100", font=("Arial", 14))
hero_hp.pack(pady=10)

monster_hp = Label(root, text="Monster HP: 50", font=("Arial", 14))
monster_hp.pack(pady=10)

result = Label(root, text="Battle started", font=("Arial", 12))
result.pack(pady=20)

attack_btn = Button(
    root,
    text="Attack Monster",
    command=lambda: attack_monster(monster_hp, result)
)

attack_btn.pack()

root.mainloop()