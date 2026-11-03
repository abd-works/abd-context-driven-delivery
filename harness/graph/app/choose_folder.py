"""Open a folder dialog on this machine and print the folder a person chose, or nothing when they cancel.

The explorer's server runs this for its Browse buttons; it reads no graph and calls no tool."""

import sys
import tkinter
from tkinter import filedialog

window = tkinter.Tk()
window.withdraw()
window.attributes("-topmost", True)
print(filedialog.askdirectory(title=sys.argv[1] if len(sys.argv) > 1 else "Select a folder") or "")
window.destroy()
