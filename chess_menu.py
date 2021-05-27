# -*- coding: utf-8 -*-
"""
Created on Wed May 26 18:46:13 2021

@author: Zach
"""

import tkinter as tk
from tkinter import ttk
from random import randrange

from chess_themes import themes


def mainMenu():
    """Initial menu for choosing settings in the chess game."""
    WINDOW_TITLE = "Chess Menu"
    WINDOW_BG = "#5285B4"
    TEXT_COLOR = "#F5F5F5"
    SCREEN_SIZE = "500x300"
    TEXT_KWARGS = dict(
        bg = WINDOW_BG,
        fg = TEXT_COLOR,
        # padx = 0,
    )
    
    root = tk.Tk()
    root.geometry(SCREEN_SIZE)
    root.title(WINDOW_TITLE)
    root.configure(bg=WINDOW_BG)
    tk.Label(
        root, text="Chess", font="Helvetica 20 bold", **TEXT_KWARGS).pack()
    
    # Menu line for choosing to play a human opponent or the computer.
    tk.Label(
        root, text="Play with:", font="Helvetica 14 bold", **TEXT_KWARGS).place(
        x=20, y=52)
    opponentIsAI = tk.BooleanVar()
    rBtn_Friend = tk.Radiobutton(
        root, text="Friend", font="Helvetica 14", variable=opponentIsAI,
        value=False)  # , **TEXT_KWARGS)
    rBtn_Friend.place(x=200, y=50)
    rBtn_Computer = tk.Radiobutton(
        root, text="Computer", font="Helvetica 14", variable=opponentIsAI,
        value=True)  # , **TEXT_KWARGS)
    rBtn_Computer.place(x=300, y=50)
    
    # Menu line for choosing player color.
    tk.Label(
        root, text= "Play as:", font="Helvetica 14 bold", **TEXT_KWARGS).place(
        x=20, y=92)
    playerColor = tk.IntVar()  # 0 = white, 1 = black, 2 = random.
    rBtn_White = tk.Radiobutton(root, text="White", font="Helvetica 14",
        variable=playerColor, value=0)
    rBtn_Black = tk.Radiobutton(root, text="Black", font="Helvetica 14",
        variable=playerColor, value=1)
    rBtn_Random = tk.Radiobutton(root, text="Random", font="Helvetica 14",
        variable=playerColor, value=2)
    rBtn_White.place(x=200, y=90)
    rBtn_Black.place(x=290, y=90)
    rBtn_Random.place(x=380, y=90)
    
    # Theme
    theme_chosen = False
    tk.Label(
        root, text="Theme:", font="Helvetica 14 bold", **TEXT_KWARGS).place(
            x=20, y=132)
    theme_list = [key for key in themes]
    themeMenu = ttk.Combobox(root, values=theme_list, state="READONLY")
    themeMenu.set("Select a theme")
    themeMenu.place(x=200, y=136)
    
    # Start game button
    def getValues():
        global humanWhite, humanBlack, theme
        if not opponentIsAI.get():
            humanWhite, humanBlack = True, True
        else:
            if playerColor.get() == 2:
                color = randrange(2)
            else:
                color = playerColor.get()
            if color == 0:
                humanWhite, humanBlack = True, False
            elif color == 1:
                humanWhite, humanBlack = False, True
        theme = themeMenu.get()
        
        root.destroy()
    
    tk.Button(
        root,
        text="Play Chess!",
        font="Helvetica 15 bold",
        fg="#222",
        bg="#EEE",
        padx=2,
        command=getValues,
        # state = tk.NORMAL if theme_chosen else tk.DISABLED,
    ).place(x=190, y=220)

    root.mainloop()
    return (humanWhite, humanBlack, theme)
