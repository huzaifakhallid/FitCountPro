# src/main.py
from ui.app import FitCountProApp
import os

if __name__ == "__main__":
    app = FitCountProApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()