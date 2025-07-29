# --- File: run_visual_tool_v1.810.py (LAUNCHER) ---
import tkinter as tk
from tkinter import messagebox
import traceback
from datetime import datetime
import os
import sys

# Add the project root to the path, allowing 'app' to be imported as a package
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

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
        try: messagebox.showerror("Fatal Error", f"Application has crashed. Details saved to:\n{log_path}")
        except: print(f"FATAL ERROR: Application crashed. Details saved to {log_path}")