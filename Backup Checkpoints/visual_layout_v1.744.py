# --- File: visual_layout_v1.744.py (LAUNCHER) ---
# FIX: Correctly modifies the system path to find the 'app' and 'src' modules.

import tkinter as tk
from tkinter import messagebox
import traceback
from datetime import datetime
import os
import sys

# --- THIS IS THE CRITICAL FIX ---
# We add the project root directory to the path.
# This allows Python to find the 'app' package and everything inside it.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Now, we can import from 'app.src' as a proper package
from app.src.app_logic import VisualLayoutTool

ERROR_LOG_FILENAME = "gui_error_log.txt"

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = VisualLayoutTool(root)
        root.mainloop()
    except Exception as e:
        error_message = traceback.format_exc()
        log_path = os.path.join(SCRIPT_DIR, ERROR_LOG_FILENAME)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"--- FATAL ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n{error_message}\n")
        try: 
            messagebox.showerror("Fatal Error", f"Application has crashed. Details saved to:\n{log_path}")
        except: 
            print(f"FATAL ERROR: Application crashed. Details saved to {log_path}")