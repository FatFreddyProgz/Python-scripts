#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from tkinter import * 
from tkinter.messagebox import *
import random

fenetre = Tk()
rnd = random.randint(1,20)
a = 1

def recupere():
    user_input = entree.get()
    global a
    if user_input.isdigit() == True:
        jeu(int(user_input))
        a = a + 1
    else:
        showinfo("Alerte","Veuillez Entrer un nombre !!")
        a = a -1

def jeu(inp):
    if inp < rnd:
        showinfo("Alerte", 'Trop Bas !')
    elif inp > rnd:
        showinfo("Alerte", 'Trop Haut !')
    else:
        showinfo("Alerte", "Youhou Trop Fort ! En " + str(a) + " coups !")

value = StringVar() 
label = Label(fenetre, text="Devine a quelle nombre je pense !")
label.pack()
entree = Entry(fenetre, textvariable=value, width=30)
entree.pack()

bouton = Button(fenetre, text="Valider", command=recupere)
bouton.pack()



fenetre.mainloop()
