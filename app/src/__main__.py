# --- File: app/src/__main__.py ---
import tkinter as tk
from tkinter import ttk, messagebox
import traceback
from datetime import datetime
import os
import sys

from .app_logic import VisualLayoutTool
from .main_menu import MainMenu
from .stitcher_tool import StitcherTool 

# --- NEW: Function to handle bundled file paths ---
def get_base_path():
    """ Get the base path for the app, whether it's frozen or not. """
    if getattr(sys, 'frozen', False):
        # The application is frozen (packaged by PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # The application is running in a normal Python environment
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AppController:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Automation Suite")
        self.base_path = get_base_path() # Store the base path
        
        self.setup_style()
        self.center_window(800, 400)
        
        self.current_frame = None
        self.show_main_menu()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

    def setup_style(self):
        azure_path = os.path.join(self.base_path, "azure.tcl")
        self.root.tk.call("source", azure_path)
        ttk.Style().theme_use("azure-dark")
        
        style = ttk.Style()
        darker_bg = "#1c1c1c"
        disabled_fg = "#5c5c5c"
        
        self.root.configure(bg=darker_bg)
        style.configure("TFrame", background=darker_bg)
        style.configure("TLabel", background=darker_bg)
        style.configure("Highlight.TLabel", foreground="#00E0FF", background=darker_bg, font=("Arial", 28, "bold"))
        style.configure("Header.TLabel", foreground="white", background=darker_bg, font=("Arial", 22))
        style.configure("WIP.TLabel", foreground="white", background=darker_bg)
        
        style.configure("TButton", font=("Arial", 12), padding=10, anchor=tk.CENTER)
        style.map("TButton", foreground=[('disabled', disabled_fg)])
        
        style.configure("TLabelframe", background=darker_bg, padding=10)
        style.configure("TLabelframe.Label", foreground="white", background=darker_bg)
        
        style.configure("Step.TLabelframe", relief="solid", borderwidth=1)
        style.configure("Step.TLabelframe.Label", font=("Arial", 14, "bold"), anchor=tk.CENTER, padding=(0, 5))
        style.configure("Arrow.TLabel", foreground="white", font=("Arial", 14, "bold"))
        style.configure("Placeholder.TLabel", foreground="white")

    def clear_window(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_main_menu(self):
        self.clear_window()
        self.center_window(800, 400)
        self.root.title("AI Automation Suite - Main Menu")
        menu = MainMenu(self.root, self.launch_stitcher, self.launch_layout_tool, self.launch_image_generator)
        self.current_frame = menu.frame

    def launch_stitcher(self):
        self.clear_window()
        self.center_window(1000, 800)
        self.root.title("AI Automation Suite - Video Stitcher")
        stitcher = StitcherTool(self.root, self.show_main_menu)
        self.current_frame = stitcher.frame

    def launch_layout_tool(self):
        layout_window = tk.Toplevel(self.root)
        layout_window.title("Visual Layout Tool (WIP)")
        app = VisualLayoutTool(layout_window)

    def launch_image_generator(self):
        messagebox.showwarning("Work in Progress", "The Image Generator is currently under development.")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AppController(root)
        root.mainloop()
    except Exception as e:
        error_message = traceback.format_exc()
        project_root = get_base_path()
        log_path = os.path.join(project_root, "gui_error_log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"--- FATAL ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n{error_message}\n")
        messagebox.showerror("Fatal Error", f"Application has crashed. Details saved to:\n{log_path}")
