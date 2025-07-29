# --- Version 1.710: Interactive Layout Tool ---
# Goal: An interactive GUI to place draggable text elements on a video frame
#       and save the layout to a config.yml file.

import tkinter as tk
from tkinter import filedialog, simpledialog, colorchooser
from PIL import Image, ImageTk
import subprocess
import os
import yaml

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_FRAME_FILENAME = "_temp_frame.png"
OUTPUT_CONFIG_FILENAME = "config.yml"

class DraggableObject:
    """A class to make canvas items draggable."""
    def __init__(self, item, properties):
        self.item = item
        self.properties = properties
        self.item.bind("<ButtonPress-1>", self.on_press)
        self.item.bind("<B1-Motion>", self.on_motion)

    def on_press(self, event):
        self.x = event.x
        self.y = event.y

    def on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        self.item.move(deltax, deltay)
        self.x = event.x
        self.y = event.y
        # Update properties with new coordinates
        coords = self.item.winfo_geometry().split('+')
        self.properties['x'] = int(coords[1])
        self.properties['y'] = int(coords[2])

class VisualLayoutTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Layout Tool v1.710")

        self.canvas_objects = [] # To store all our layout elements
        self.original_image = None # To store the full-res screenshot

        # --- Main Layout Frames ---
        self.control_frame = tk.Frame(root, width=250)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Control Panel Widgets ---
        tk.Button(self.control_frame, text="Load Video", command=self.load_video).pack(fill=tk.X)
        tk.Button(self.control_frame, text="Save Layout to config.yml", command=self.save_layout).pack(fill=tk.X, pady=(10,0))
        
        # --- Text Controls ---
        text_frame = tk.LabelFrame(self.control_frame, text="Add Text Element")
        text_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(text_frame, text="Text:").pack()
        self.text_entry = tk.Entry(text_frame)
        self.text_entry.pack(fill=tk.X, padx=5)
        self.text_entry.insert(0, "Your Text Here")

        tk.Label(text_frame, text="Font Size:").pack()
        self.font_size_entry = tk.Entry(text_frame)
        self.font_size_entry.pack(fill=tk.X, padx=5)
        self.font_size_entry.insert(0, "80")
        
        tk.Label(text_frame, text="Font Color:").pack()
        self.font_color_button = tk.Button(text_frame, text="Choose Color", command=self.choose_color)
        self.font_color_button.pack(pady=5)
        self.font_color = "#FFFFFF" # Default to white

        tk.Button(text_frame, text="Add Text to Canvas", command=self.add_text).pack(pady=10)

        # --- Canvas ---
        self.canvas = tk.Canvas(self.canvas_frame, background="dark grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose color")
        if color_code:
            self.font_color = color_code[1] # Get the hex code

    def add_text(self):
        text_content = self.text_entry.get()
        font_size = int(self.font_size_entry.get())
        
        properties = {
            'type': 'text',
            'text': text_content,
            'font': 'arial.ttf',
            'size': font_size,
            'color': self.font_color,
            'x': 100, # Initial position
            'y': 100,
            'start_time': 'start',
            'end_time': 'end'
        }

        # Create the text on canvas
        text_item = self.canvas.create_text(
            100, 100,
            text=text_content,
            font=("Arial", font_size),
            fill=self.font_color,
            anchor=tk.NW
        )
        
        # Make it draggable and add to our list
        draggable_item = DraggableObject(self.canvas.create_window(100, 100, window=tk.Label(self.canvas, text=text_content, font=("Arial", font_size), fg=self.font_color, bg='black'), anchor=tk.NW), properties)
        self.canvas_objects.append(draggable_item)

    def load_video(self):
        filepath = filedialog.askopenfilename(initialdir=os.path.join(SCRIPT_DIR, "Videos"))
        if not filepath: return

        output_frame_path = os.path.join(SCRIPT_DIR, TEMP_FRAME_FILENAME)
        command = ['ffmpeg', '-y', '-i', filepath, '-vframes', '1', output_frame_path]
        
        try:
            subprocess.run(command, check=True, capture_output=True)
            self.original_image = Image.open(output_frame_path)
            self.display_image()
        except Exception as e:
            print(f"Error loading video frame: {e}")
    
    def display_image(self):
        if not self.original_image: return
        # For simplicity in v1.710, we'll just display it at its original size.
        # Rescaling logic is complex and will be added next.
        self.photo_image = ImageTk.PhotoImage(self.original_image)
        self.canvas.config(width=self.original_image.width, height=self.original_image.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

    def save_layout(self):
        layout_data = {'text_overlays': []}
        
        for obj in self.canvas_objects:
            if obj.properties['type'] == 'text':
                # Update final coordinates before saving
                final_x = obj.item.winfo_x()
                final_y = obj.item.winfo_y()
                obj.properties['x'] = final_x
                obj.properties['y'] = final_y
                layout_data['text_overlays'].append(obj.properties)

        output_path = os.path.join(SCRIPT_DIR, OUTPUT_CONFIG_FILENAME)
        with open(output_path, 'w') as f:
            yaml.dump(layout_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Layout saved successfully to {output_path}")
        simpledialog.messagebox.showinfo("Success", f"Layout saved to {output_path}")

# --- Main execution block ---
if __name__ == "__main__":
    root = tk.Tk()
    app = VisualLayoutTool(root)
    root.mainloop()