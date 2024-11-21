# Test GUI right now, for actually functionality we will need to create this as a Class and add to Client.py

import tkinter as tk
from tkinter import messagebox

displayBoard = [
            [100, 100, 100, 100, 100],
            [200, 200, 200, 200, 200],
            [400, 400, 400, 400, 400],
            [800, 800, 800, 800, 800],
            [1600, 1600, 1600, 1600, 1600]
        ]

def helpButtonOnClick():
    messagebox.showinfo("Message","HELP I AM TRAPPED IN HERE")

def quitButtonOnClick():
    #sel.unregister
    #sock.close()
    #IDK if the above happens here i just have this in a function incase we want to handle it here
    root.destroy()

def startButtonOnClick():
    root = tk.Tk()
    root.geometry("1000x1000")
    root.title("Jeopardy")

    label = tk.Label(root, text="Welcome to the Jeopardy game!", font=('Arial', 48))
    label.pack()

    buttonFrame = tk.Frame(root)
    buttonFrame.columnconfigure(0, weight=1)
    buttonFrame.columnconfigure(1, weight=1)
    buttonFrame.pack()

    makeBoard(root, buttonFrame)

def makeBoard(root, buttonFrame):
    for i in range(len(displayBoard)):
        for j in range(len(displayBoard)):
            button = tk.Button(buttonFrame, text=displayBoard[i][j], font=('Arial', 32))
            button.grid(row=i, column=j+1, padx=10, pady=20)

#root window for UI
root = tk.Tk()
root.geometry("800x500")
root.title("Jeo-Jeopardy")

# Text displayed at the top of the window --- .pack() used to 'pack' it into the window?
label = tk.Label(root, text="Welcome to Jeo-Jeopardy", font=('Arial', 18))
label.pack()

# Frame to hold the buttons. Pack buttons into frame and then modify frame placement
buttonFrame = tk.Frame(root)
buttonFrame.columnconfigure(0, weight=1)
buttonFrame.columnconfigure(1, weight=1)
buttonFrame.pack()

# Buttons are placed in the frame and any placement modifiers will be done w/in the buttonFrame OBJ
readyBtn = tk.Button(buttonFrame, text="Ready Up", font=('Arial', 16), command=startButtonOnClick)
readyBtn.grid(row=0, column=0)
quitBtn = tk.Button(buttonFrame, text="Quit", font=('Arial', 16), command=quitButtonOnClick)
quitBtn.grid(row=2, column=0)
helpBtn = tk.Button(buttonFrame, text="Help", font=('Arial', 16), command=helpButtonOnClick)
helpBtn.grid(row=1, column=0)

# Called after all elements have been created and packed
root.mainloop()
