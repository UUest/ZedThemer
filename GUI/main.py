import tkinter as tk
from zhemer import *

def main():
    root = tk.Tk()  # Create the main application window
    app = Zhemer(root)  # Instantiate the app class
    root.mainloop()  # Start the Tkinter event loop

if __name__ == "__main__":
    main()
