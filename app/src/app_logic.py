# --- File: app/src/app_logic.py ---
import tkinter as tk
from tkinter import ttk, colorchooser
import os

from .managers.canvas_manager import CanvasManager
from .managers.event_handler import EventHandler
from .managers.file_manager import FileManager
from .managers.state_manager import StateManager
from .ui_controls import create_controls

class VisualLayoutTool:
    def __init__(self, parent_window):
        self.root = parent_window
        self.VERSION = "1.9.9.2" # Bugfix release
        if isinstance(parent_window, tk.Toplevel):
            self.root.title(f"Visual Layout Tool v{self.VERSION}")
        
        self.root.geometry("1280x720")

        # --- PATHS ---
        self.PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.TEMP_DIR = os.path.join(self.PROJECT_ROOT, "app", "_temp"); os.makedirs(self.TEMP_DIR, exist_ok=True)
        self.ASSETS_DIR = os.path.join(self.PROJECT_ROOT, "Assets"); self.ICONS_DIR = os.path.join(self.ASSETS_DIR, "Icons")
        self.SHAPES_DIR = os.path.join(self.ASSETS_DIR, "Shapes"); self.IMAGES_DIR = os.path.join(self.ASSETS_DIR, "Images")
        self.VIDEOS_DIR = os.path.join(self.ASSETS_DIR, "Videos")
        self.TEMP_FRAME_FILENAME = os.path.join(self.TEMP_DIR, "frame.png")
        self.OUTPUT_CONFIG_FILENAME = os.path.join(self.PROJECT_ROOT, "config.yml")
        self.FONT_DIR = "C:/Windows/Fonts/"

        # --- APP STATE ---
        self.selected_item_tag = None
        self.original_image = None
        self.display_image = None
        self.selection_box = None
        self._drag_data = {"x": 0, "y": 0}

        # --- MANAGERS ---
        self.state_manager = StateManager()
        self.file_manager = FileManager(self)
        self.canvas_manager = CanvasManager(self)
        self.event_handler = EventHandler(self)
        
        # --- UI SETUP ---
        self.pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL); self.pane.pack(fill=tk.BOTH, expand=True)
        self.control_frame = ttk.Frame(self.pane, width=320); self.pane.add(self.control_frame, weight=0)
        self.canvas = tk.Canvas(self.pane, background="dark grey", highlightthickness=0); self.pane.add(self.canvas, weight=1)
        
        self.available_fonts = ["Arial", "Arial Black", "Bahnschrift", "Calibri", "Comic Sans MS", "Consolas", "Courier New", "Georgia", "Impact", "Lucida Console", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"]
        self.available_shapes = self.file_manager.load_assets(self.SHAPES_DIR, '.png')
        self.available_images = self.file_manager.load_assets(self.IMAGES_DIR, '.png')
        self.available_assets = self.available_shapes + self.available_images
        self.trash_icon_path = os.path.join(self.ICONS_DIR, "trash.png")
        
        create_controls(self, self.control_frame)
        self.toggle_controls(tk.DISABLED)
        
        # --- BINDINGS ---
        if isinstance(self.root, tk.Toplevel):
            self.root.protocol("WM_DELETE_WINDOW", self.file_manager.on_close_toplevel)
        else:
            self.root.protocol("WM_DELETE_WINDOW", self.file_manager.on_close)

        self.root.bind("<Configure>", self.canvas_manager.on_resize)
        self.canvas.bind("<Button-1>", self.event_handler.on_canvas_click)

    def toggle_controls(self, state):
        for child in self.main_controls_frame.winfo_children():
            if not isinstance(child, ttk.Button) or "Load Video" not in child.cget("text"):
                self._toggle_widget_state(child, state)

    def _toggle_widget_state(self, widget, state):
        try:
            widget.configure(state=state)
        except tk.Toplevel: pass
        for child in widget.winfo_children():
            self._toggle_widget_state(child, state)
    
    def choose_color_clicked(self, target):
        btn = None
        if target == 'text_fill': btn = self.text_fill_color_btn
        elif target == 'text_stroke': btn = self.text_stroke_color_btn
        elif target == 'shape_fill': btn = self.shape_fill_color_btn
        elif target == 'shape_stroke': btn = self.shape_stroke_color_btn
        
        if btn:
            color = colorchooser.askcolor(title=f"Choose color for {target.replace('_', ' ')}", initialcolor=btn['bg'])[1]
            if color:
                btn.config(bg=color); r,g,b = self.root.winfo_rgb(color); text_color = 'white' if (r/65535*0.299 + g/65535*0.587 + b/65535*0.114) < 0.6 else 'black'
                btn.config(fg=text_color)
                self.canvas_manager.update_selected_from_controls()

    def update_selected_from_controls(self, event=None): self.canvas_manager.update_selected_from_controls()
    def on_layer_select(self, event): self.event_handler.on_layer_select(event)
    def on_slider_change(self, value): self.canvas_manager.on_slider_change(value)
