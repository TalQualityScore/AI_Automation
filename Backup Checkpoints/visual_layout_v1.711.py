# --- Version 1.711 Advanced Interactive Layout Tool ---
# Major UI Overhaul, Dynamic Resizing, Shape Library, and Selection

import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import yaml

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, Assets)
SHAPES_DIR = os.path.join(ASSETS_DIR, Shapes)
TEMP_FRAME_FILENAME = _temp_frame.png
OUTPUT_CONFIG_FILENAME = config.yml
FONT_DIR = CWindowsFonts

class VisualLayoutTool
    def __init__(self, root)
        self.root = root
        self.root.title(Visual Layout Tool v1.711)
        self.root.geometry(1280x720) # Set a default window size

        # Data storage
        self.canvas_objects = {} # {canvas_id properties_dict}
        self.original_image = None
        self.display_image = None
        self.selected_item = None

        # --- Asset Loading ---
        self.available_fonts = self._load_fonts()
        self.available_shapes = self._load_shapes()

        # --- Main Layout ---
        self.pane = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.pane.pack(fill=tk.BOTH, expand=True)

        self.control_frame = ttk.Frame(self.pane, width=350, style='TFrame')
        self.pane.add(self.control_frame, weight=1)

        self.canvas = tk.Canvas(self.pane, background=dark grey)
        self.pane.add(self.canvas, weight=4)

        # --- Populate Control Panel ---
        self._create_controls()

        # --- Bind Events ---
        self.canvas.bind(Button-1, self._on_canvas_click)
        self.root.bind(Configure, self._on_resize)

    def _load_fonts(self)
        try
            return sorted([f for f in os.listdir(FONT_DIR) if f.lower().endswith('.ttf')])
        except FileNotFoundError
            return [arial.ttf] # Fallback

    def _load_shapes(self)
        if not os.path.exists(SHAPES_DIR)
            os.makedirs(SHAPES_DIR)
        return sorted([f for f in os.listdir(SHAPES_DIR) if f.lower().endswith('.png')])

    def _create_controls(self)
        # File Operations
        file_frame = ttk.LabelFrame(self.control_frame, text=File)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(file_frame, text=Load Video, command=self._load_video).pack(fill=tk.X)
        ttk.Button(file_frame, text=Save Layout to config.yml, command=self._save_layout).pack(fill=tk.X, pady=5)

        # Text Element Controls
        text_frame = ttk.LabelFrame(self.control_frame, text=Text Element)
        text_frame.pack(fill=tk.X, padx=10, pady=10)
        self.text_input = tk.Text(text_frame, height=4) # Larger text box
        self.text_input.pack(fill=tk.X)
        self.text_input.insert(1.0, Your Text)

        self.font_var = tk.StringVar(value=self.available_fonts[0])
        ttk.Label(text_frame, text=Font).pack(anchor=tk.W)
        ttk.Combobox(text_frame, textvariable=self.font_var, values=self.available_fonts).pack(fill=tk.X)

        self.font_size_var = tk.IntVar(value=80)
        ttk.Label(text_frame, text=Font Size).pack(anchor=tk.W)
        ttk.Scale(text_frame, from_=1, to=120, variable=self.font_size_var, orient=tk.HORIZONTAL).pack(fill=tk.X)

        color_frame = ttk.Frame(text_frame)
        color_frame.pack(fill=tk.X, pady=5)
        self.fill_color = #FFFFFF
        self.stroke_color = #000000
        ttk.Button(color_frame, text=Fill, command=lambda self._choose_color('fill')).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(color_frame, text=Stroke, command=lambda self._choose_color('stroke')).pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        ttk.Button(text_frame, text=Add Text to Canvas, command=self._add_text).pack(pady=10)

        # Shape Element Controls
        shape_frame = ttk.LabelFrame(self.control_frame, text=Shape Element)
        shape_frame.pack(fill=tk.X, padx=10, pady=10)
        self.shape_var = tk.StringVar(value=self.available_shapes[0] if self.available_shapes else )
        ttk.Label(shape_frame, text=Shape).pack(anchor=tk.W)
        ttk.Combobox(shape_frame, textvariable=self.shape_var, values=self.available_shapes).pack(fill=tk.X)
        ttk.Button(shape_frame, text=Add Shape to Canvas, command=self._add_shape).pack(pady=10)

    def _choose_color(self, target)
        color = colorchooser.askcolor()[1]
        if color
            if target == 'fill' self.fill_color = color
            else self.stroke_color = color

    def _load_video(self)
        filepath = filedialog.askopenfilename(initialdir=os.path.join(SCRIPT_DIR, Videos))
        if not filepath return
        output_frame_path = os.path.join(SCRIPT_DIR, TEMP_FRAME_FILENAME)
        command = ['ffmpeg', '-y', '-i', filepath, '-vframes', '1', output_frame_path]
        try
            subprocess.run(command, check=True, capture_output=True)
            self.original_image = Image.open(output_frame_path)
            self._on_resize() # Trigger initial resize and display
        except Exception as e
            messagebox.showerror(Error, fCould not load video frame {e})

    def _on_resize(self, event=None)
        if not self.original_image return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width  2 or canvas_height  2 return # Avoid error on startup

        # Rescale image to fit canvas while maintaining aspect ratio
        img_copy = self.original_image.copy()
        img_copy.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        self.display_image = ImageTk.PhotoImage(img_copy)
        self.canvas.delete(all)
        self.canvas.create_image(
            canvas_width  2, canvas_height  2,
            anchor=tk.CENTER, image=self.display_image
        )
        # Redraw all existing objects
        for item_id, props in self.canvas_objects.items()
            # This part is complex, for now we just clear on resize.
            # A full redraw would require scaling object positions too.
            pass # We'll re-implement object drawing on resize later if needed.

    def _add_text(self)
        text_content = self.text_input.get(1.0, tk.END).strip()
        font_size = self.font_size_var.get()
        font_name = self.font_var.get()
        
        item_id = self.canvas.create_text(
            100, 100, text=text_content, fill=self.fill_color,
            font=(font_name.replace('.ttf', ''), font_size),
            stroke=self.stroke_color, width=self.canvas.winfo_width() - 200
        )
        self.canvas_objects[item_id] = {
            'type' 'text', 'text' text_content, 'font' font_name, 'size' font_size,
            'color' self.fill_color, 'stroke_color' self.stroke_color, 'stroke_width' 2
        }

    def _add_shape(self)
        shape_file = self.shape_var.get()
        if not shape_file return
        
        shape_path = os.path.join(SHAPES_DIR, shape_file)
        try
            img = Image.open(shape_path)
            photo = ImageTk.PhotoImage(img)
            
            item_id = self.canvas.create_image(150, 150, image=photo, anchor=tk.NW)
            self.canvas_objects[item_id] = {'type' 'image', 'file' shape_file}
            
            # Store reference to avoid garbage collection
            self.canvas.image = photo 
        except Exception as e
            messagebox.showerror(Error, fCould not load shape {e})

    def _on_canvas_click(self, event)
        item_ids = self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
        if item_ids
            self.selected_item = item_ids[-1] # Select the top-most item
            self.canvas.tag_raise(self.selected_item)
            self.canvas.bind(B1-Motion, self._on_drag)
        else
            self.selected_item = None
            self.canvas.unbind(B1-Motion)

    def _on_drag(self, event)
        if self.selected_item
            self.canvas.moveto(self.selected_item, event.x - 10, event.y - 10) # Simple drag

    def _save_layout(self)
        config_data = {'image_overlays' [], 'text_overlays' []}
        for item_id, props in self.canvas_objects.items()
            coords = self.canvas.coords(item_id)
            props['x'] = int(coords[0])
            props['y'] = int(coords[1])
            
            if props['type'] == 'text'
                config_data['text_overlays'].append(props)
            elif props['type'] == 'image'
                config_data['image_overlays'].append(props)
        
        output_path = os.path.join(SCRIPT_DIR, OUTPUT_CONFIG_FILENAME)
        with open(output_path, 'w') as f
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        messagebox.showinfo(Success, fLayout saved to {output_path})

# --- Main execution block ---
if __name__ == __main__
    root = tk.Tk()
    app = VisualLayoutTool(root)
    root.mainloop()