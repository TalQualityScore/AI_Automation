# --- Version 1.712: Resilient GUI with Global Error Logging ---
# Fixes crash on empty 'Shapes' folder and adds a robust error handler.

import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import yaml
import traceback # --- NEW in v1.712: For detailed error logging

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "Assets")
SHAPES_DIR = os.path.join(ASSETS_DIR, "Shapes")
TEMP_FRAME_FILENAME = "_temp_frame.png"
OUTPUT_CONFIG_FILENAME = "config.yml"
ERROR_LOG_FILENAME = "gui_error_log.txt"
FONT_DIR = "C:/Windows/Fonts/"

class VisualLayoutTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Layout Tool v1.712")
        self.root.geometry("1280x720")

        self.canvas_objects = {}
        self.original_image = None
        self.display_image = None
        self.selected_item = None

        self.available_fonts = self._load_assets(FONT_DIR, '.ttf')
        self.available_shapes = self._load_assets(SHAPES_DIR, '.png')

        self.pane = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.pane.pack(fill=tk.BOTH, expand=True)
        self.control_frame = ttk.Frame(self.pane, width=350)
        self.pane.add(self.control_frame, weight=1)
        self.canvas = tk.Canvas(self.pane, background="dark grey")
        self.pane.add(self.canvas, weight=4)

        self._create_controls()

        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.root.bind("<Configure>", self._on_resize)

    def _load_assets(self, path, extension):
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            return sorted([f for f in os.listdir(path) if f.lower().endswith(extension)])
        except Exception:
            return []

    def _create_controls(self):
        # File Operations
        file_frame = ttk.LabelFrame(self.control_frame, text="File")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(file_frame, text="Load Video", command=self._load_video).pack(fill=tk.X)
        ttk.Button(file_frame, text="Save Layout to config.yml", command=self._save_layout).pack(fill=tk.X, pady=5)

        # Text Element Controls
        text_frame = ttk.LabelFrame(self.control_frame, text="Text Element")
        text_frame.pack(fill=tk.X, padx=10, pady=10)
        self.text_input = tk.Text(text_frame, height=4)
        self.text_input.pack(fill=tk.X)
        self.text_input.insert("1.0", "Your Text")

        self.font_var = tk.StringVar(value=self.available_fonts[0] if self.available_fonts else "arial.ttf")
        ttk.Label(text_frame, text="Font:").pack(anchor=tk.W)
        ttk.Combobox(text_frame, textvariable=self.font_var, values=self.available_fonts, state="readonly").pack(fill=tk.X)

        self.font_size_var = tk.IntVar(value=80)
        ttk.Label(text_frame, text="Font Size:").pack(anchor=tk.W)
        ttk.Scale(text_frame, from_=1, to=200, variable=self.font_size_var, orient=tk.HORIZONTAL).pack(fill=tk.X)

        color_frame = ttk.Frame(text_frame)
        color_frame.pack(fill=tk.X, pady=5)
        self.fill_color = "#FFFFFF"
        self.stroke_color = "#000000"
        ttk.Button(color_frame, text="Fill Color", command=lambda: self._choose_color('fill')).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(color_frame, text="Stroke Color", command=lambda: self._choose_color('stroke')).pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        ttk.Button(text_frame, text="Add Text to Canvas", command=self._add_text).pack(pady=10)

        # Shape Element Controls
        shape_frame = ttk.LabelFrame(self.control_frame, text="Shape Element")
        shape_frame.pack(fill=tk.X, padx=10, pady=10)
        # --- FIX in v1.712: Gracefully handle empty shape list ---
        self.shape_var = tk.StringVar(value=self.available_shapes[0] if self.available_shapes else "")
        ttk.Label(shape_frame, text="Shape:").pack(anchor=tk.W)
        ttk.Combobox(shape_frame, textvariable=self.shape_var, values=self.available_shapes, state="readonly").pack(fill=tk.X)
        ttk.Button(shape_frame, text="Add Shape to Canvas", command=self._add_shape).pack(pady=10)

    def _choose_color(self, target):
        color = colorchooser.askcolor(title=f"Choose {target} color")[1]
        if color:
            if target == 'fill': self.fill_color = color
            else: self.stroke_color = color

    def _load_video(self):
        filepath = filedialog.askopenfilename(initialdir=os.path.join(SCRIPT_DIR, "Videos"))
        if not filepath: return
        output_frame_path = os.path.join(SCRIPT_DIR, TEMP_FRAME_FILENAME)
        command = ['ffmpeg', '-y', '-i', filepath, '-vframes', '1', output_frame_path]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.original_image = Image.open(output_frame_path)
            self._on_resize()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load video frame: {e}")

    def _on_resize(self, event=None):
        if not self.original_image: return
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width < 2 or canvas_height < 2: return
        
        img_copy = self.original_image.copy()
        img_copy.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        self.display_image = ImageTk.PhotoImage(img_copy)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width / 2, canvas_height / 2, anchor=tk.CENTER, image=self.display_image)
        # Note: Redrawing objects on resize is complex and deferred for simplicity.

    def _add_text(self):
        # (This function is unchanged)
        text_content = self.text_input.get("1.0", tk.END).strip()
        font_size = self.font_size_var.get()
        font_name = self.font_var.get()
        font_family = os.path.splitext(font_name)[0]
        
        item_id = self.canvas.create_text(
            100, 100, text=text_content, fill=self.fill_color,
            font=(font_family, font_size) # Using font family name
        )
        self.canvas_objects[item_id] = {
            'type': 'text', 'text': text_content, 'font': font_name, 'size': font_size,
            'color': self.fill_color, 'stroke_color': self.stroke_color, 'stroke_width': 2
        }

    def _add_shape(self):
        # (This function is unchanged)
        shape_file = self.shape_var.get()
        if not shape_file: return
        shape_path = os.path.join(SHAPES_DIR, shape_file)
        try:
            img = Image.open(shape_path)
            photo = ImageTk.PhotoImage(img)
            item_id = self.canvas.create_image(150, 150, image=photo, anchor=tk.NW)
            self.canvas_objects[item_id] = {'type': 'image', 'file': shape_file}
            self.canvas.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Could not load shape: {e}")

    def _on_canvas_click(self, event):
        # (This function is unchanged, but we'll improve it later)
        item_ids = self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
        if item_ids:
            self.selected_item = item_ids[-1]
            self.canvas.tag_raise(self.selected_item)
            self.canvas.bind("<B1-Motion>", self._on_drag)
        else:
            self.selected_item = None
            self.canvas.unbind("<B1-Motion>")

    def _on_drag(self, event):
        # (This function is unchanged, but we'll improve it later)
        if self.selected_item:
            self.canvas.moveto(self.selected_item, event.x - 10, event.y - 10)

    def _save_layout(self):
        # (This function is unchanged)
        config_data = {'image_overlays': [], 'text_overlays': []}
        for item_id, props in self.canvas_objects.items():
            coords = self.canvas.coords(item_id)
            props['x'] = int(coords[0])
            props['y'] = int(coords[1])
            if props['type'] == 'text':
                config_data['text_overlays'].append(props)
            elif props['type'] == 'image':
                config_data['image_overlays'].append(props)
        output_path = os.path.join(SCRIPT_DIR, OUTPUT_CONFIG_FILENAME)
        with open(output_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        messagebox.showinfo("Success", f"Layout saved to {output_path}")

# --- NEW in v1.712: Main execution block with global error handling ---
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = VisualLayoutTool(root)
        root.mainloop()
    except Exception as e:
        # If any error happens during app startup or runtime, log it and show a message
        error_message = traceback.format_exc()
        with open(ERROR_LOG_FILENAME, "a") as f:
            f.write(f"--- ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(error_message)
            f.write("--------------------------------------------------\n\n")
        
        # Create a simple, failsafe message box to inform the user
        error_popup = tk.Tk()
        error_popup.withdraw() # Hide the main window
        messagebox.showerror(
            "Fatal Error",
            f"The application has crashed.\n\nA detailed error report has been saved to:\n{os.path.abspath(ERROR_LOG_FILENAME)}"
        )