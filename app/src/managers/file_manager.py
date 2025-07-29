# --- File: app/src/managers/file_manager.py ---
import os
import yaml
import subprocess
from tkinter import filedialog, messagebox
from PIL import Image
import tkinter as tk

class FileManager:
    def __init__(self, app):
        self.app = app

    def load_assets(self, path, extension):
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            return sorted([f for f in os.listdir(path) if f.lower().endswith(extension)])
        except:
            return []

    def load_video(self):
        filepath = filedialog.askopenfilename(initialdir=self.app.VIDEOS_DIR, title="Select a Video File")
        if not filepath:
            return
            
        command = ['ffmpeg', '-y', '-i', filepath, '-vframes', '1', self.app.TEMP_FRAME_FILENAME]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.app.original_image = Image.open(self.app.TEMP_FRAME_FILENAME)
            self.app.canvas_manager.on_resize()
            self.app.toggle_controls(tk.NORMAL)
        except Exception as e:
            messagebox.showerror("FFmpeg Error", f"Could not extract frame from video.\n\nError:\n{e}")

    def save_layout(self):
        config = {'image_overlays': [], 'text_overlays': []}
        
        # Get data from StateManager
        layer_order = self.app.state_manager.get_layer_order()
        
        for tag in layer_order:
            props = self.app.state_manager.get_properties(tag)
            if not props: continue

            # Exclude runtime-only properties from the saved config
            final_props = {k: v for k, v in props.items() if k not in ['tag', 'photo_ref']}

            if props.get('type') == 'text':
                config['text_overlays'].append(final_props)
            elif props.get('type') in ['image', 'rectangle']:
                config['image_overlays'].append(final_props)

        with open(self.app.OUTPUT_CONFIG_FILENAME, 'w') as f:
            yaml.dump(config, f, sort_keys=False, indent=2)
        
        messagebox.showinfo("Success", f"Layout saved to {os.path.basename(self.app.OUTPUT_CONFIG_FILENAME)}")

    def on_close(self):
        if os.path.exists(self.app.TEMP_FRAME_FILENAME):
            try:
                os.remove(self.app.TEMP_FRAME_FILENAME)
            except:
                pass
        self.app.root.destroy()