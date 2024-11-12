# Test GUI right now, for actually functinality we will need to create this as a Class and add to Client.py

import tkinter as tk

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

# Buttons are placed in the frame and any placement modifiers will be done w/in the buttonFram OBJ
readyBtn = tk.Button(buttonFrame, text="Ready Up", font=('Arial', 16))
readyBtn.grid(row=0, column=0)
quitBtn = tk.Button(buttonFrame, text="Quit", font=('Arial', 16))
quitBtn.grid(row=1, column=0)

# Called after all elements have been created and packed
root.mainloop()