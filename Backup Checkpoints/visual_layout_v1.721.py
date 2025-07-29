# --- File: visual_layout_v1.721.py (LAUNCHER) ---
# This is the main file you run.
# It imports the application logic and starts the GUI.

import tkinter as tk
from tkinter import ttk, messagebox
import traceback
from datetime import datetime
import os

# Import the main application class from our other file
from app_logic import VisualLayoutTool

ERROR_LOG_FILENAME = "gui_error_log.txt"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    try:
        root = tk.Tk()
        # Add a style for the accent button, can be customized
        style = ttk.Style(root)
        style.configure('Accent.TButton', foreground='white', background='#0078D7') # A nice blue
        
        # Create and run the application
        app = VisualLayoutTool(root)
        root.mainloop()

    except Exception as e:
        # Global error catcher to prevent the app from just disappearing
        error_message = traceback.format_exc()
        log_path = os.path.join(SCRIPT_DIR, ERROR_LOG_FILENAME)
        
        with open(log_path, "a") as f:
            f.write(f"--- FATAL ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(error_message)
            f.write("--------------------------------------------------\n\n")
        
        # Try to show a GUI message box, fall back to console print
        try:
            messagebox.showerror("Fatal Error", f"Application has crashed. Details have been saved to:\n{log_path}")
        except tk.TclError:
            print(f"FATAL ERROR: Application crashed. Details saved to {log_path}")