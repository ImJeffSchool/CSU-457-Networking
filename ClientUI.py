# Test GUI right now, for actually functionality we will need to create this as a Class and add to Client.py

import tkinter as tk
from tkinter import messagebox

class ClientUI:
    displayBoard = [
                [100, 100, 100, 100, 100],
                [200, 200, 200, 200, 200],
                [400, 400, 400, 400, 400],
                [800, 800, 800, 800, 800],
                [1600, 1600, 1600, 1600, 1600]
            ]
    def quitButtonOnClick(self):
        #sel.unregister
        #sock.close()
        #IDK if the above happens here i just have this in a function incase we want to handle it here
        root.destroy()

    def makeBoard(self, root, buttonFrame):
        for i in range(len(self.displayBoard)):
            for j in range(len(self.displayBoard)):
                button = tk.Button(buttonFrame, text=self.displayBoard[i][j], font=('Arial', 32))
                button.grid(row=i, column=j+1, padx=10, pady=20)
    
    def startButtonOnClick(self):
        root = tk.Tk()
        root.geometry("1000x1000")
        root.title("Jeopardy")

        label = tk.Label(root, text="Welcome to the Jeopardy game!", font=('Arial', 48))
        label.pack()

        buttonFrame = tk.Frame(root)
        buttonFrame.columnconfigure(0, weight=1)
        buttonFrame.columnconfigure(1, weight=1)
        buttonFrame.pack()

        self.makeBoard(root, buttonFrame)
    
    def helpButtonOnClick(self):
        messagebox.showinfo("Message","HELP I AM TRAPPED IN HERE")
    def __init__(self):
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
        readyBtn = tk.Button(buttonFrame, text="Ready Up", font=('Arial', 16), command=self.startButtonOnClick)
        #readyBtn = tk.Button(buttonFrame, text="Ready Up", font=('Arial', 16), command=None)
        readyBtn.grid(row=0, column=0)
        quitBtn = tk.Button(buttonFrame, text="Quit", font=('Arial', 16), command=self.quitButtonOnClick)
        #quitBtn = tk.Button(buttonFrame, text="Quit", font=('Arial', 16), command=None)
        quitBtn.grid(row=2, column=0)
        helpBtn = tk.Button(buttonFrame, text="Help", font=('Arial', 16), command=self.helpButtonOnClick)
        #helpBtn = tk.Button(buttonFrame, text="Help", font=('Arial', 16), command=None)
        helpBtn.grid(row=1, column=0)

        # Called after all elements have been created and packed
        root.mainloop()





