# --- File: app/src/managers/canvas_manager.py ---
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image
import os
from .. import drawing_utils

class CanvasManager:
    def __init__(self, app):
        self.app = app
        self._photo_refs = {}

    def on_resize(self, event=None):
        self.redraw_all_objects()

    def redraw_all_objects(self):
        self.app.canvas.delete("all")
        self._photo_refs.clear()

        if not self.app.original_image:
            self.update_layer_list()
            return

        canvas_w, canvas_h = self.app.canvas.winfo_width(), self.app.canvas.winfo_height()
        if canvas_w < 2 or canvas_h < 2: return

        img = self.app.original_image.copy()
        img.thumbnail((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        bg_photo = drawing_utils.ImageTk.PhotoImage(img)
        self.app.display_image = bg_photo
        self.app.img_w, self.app.img_h = img.width, img.height
        self.app.img_x, self.app.img_y = (canvas_w - img.width) / 2, (canvas_h - img.height) / 2

        self.app.canvas.create_image(self.app.img_x, self.app.img_y, anchor=tk.NW, image=self.app.display_image, tags="background")

        for tag in self.app.state_manager.get_layer_order():
            props = self.app.state_manager.get_properties(tag)
            if not props: continue

            abs_x = props['rel_x'] * self.app.img_w + self.app.img_x
            abs_y = props['rel_y'] * self.app.img_h + self.app.img_y

            ref = None
            if props['type'] == 'text':
                ref = drawing_utils.create_stroked_text(self.app.canvas, abs_x, abs_y, props, self.app.FONT_DIR)
            else:
                ref = drawing_utils.create_shape(self.app.canvas, abs_x, abs_y, props, self.app.SHAPES_DIR, self.app.IMAGES_DIR, self.app.available_shapes)

            if ref: self._photo_refs[tag] = ref

        self.update_layer_list()
        if self.app.selected_item_tag:
            self.select_item(self.app.selected_item_tag, redraw_box=True)

    def select_item(self, tag, from_listbox=False, redraw_box=True):
        if self.app.selection_box: self.app.canvas.delete(self.app.selection_box)
        self.app.selected_item_tag = tag
        if not tag:
            self.update_context_controls(None)
            return
        if redraw_box:
            bbox = self.app.canvas.bbox(tag)
            if bbox: self.app.selection_box = self.app.canvas.create_rectangle(bbox, outline="cyan", width=2, dash=(5, 5))
        self.update_controls_from_selection(tag)
        if not from_listbox: self.update_listbox_selection(tag)

    def update_context_controls(self, props):
        for widget in self.app.context_frame.winfo_children(): widget.destroy()
        if not props: return

        if props['type'] in ['rectangle', 'square', 'circle', 'triangle', 'image']:
            size_frame = ttk.Frame(self.app.context_frame); size_frame.pack(fill=tk.X, pady=5)
            ttk.Label(size_frame, text="Width:").grid(row=0, column=0, sticky='w', padx=5)
            ttk.Entry(size_frame, textvariable=self.app.shape_width_var, width=5).grid(row=0, column=1)
            ttk.Label(size_frame, text="Height:").grid(row=1, column=0, sticky='w', padx=5)
            height_entry = ttk.Entry(size_frame, textvariable=self.app.shape_height_var, width=5)
            height_entry.grid(row=1, column=1)

            ttk.Label(size_frame, text="Scale (%):").grid(row=2, column=0, sticky='w', padx=5)
            ttk.Scale(size_frame, from_=1, to=500, variable=self.app.shape_scale_var, orient=tk.HORIZONTAL, command=self.on_scale_slider_change).grid(row=2, column=1, sticky='ew')

            if props['type'] == 'square': height_entry.config(state=tk.DISABLED)

            if props['type'] != 'image':
                color_frame = ttk.Frame(self.app.context_frame); color_frame.pack(fill=tk.X, pady=5)
                self.app.shape_fill_color_btn = tk.Button(color_frame, text="Fill", command=lambda: self.app.choose_color_clicked('shape_fill'), bg=props.get('color', '#FFFFFF'), width=8); self.app.shape_fill_color_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5,0))
                self.app.shape_stroke_color_btn = tk.Button(color_frame, text="Stroke", command=lambda: self.app.choose_color_clicked('shape_stroke'), bg=props.get('stroke_color', '#000000'), width=8); self.app.shape_stroke_color_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

                stroke_frame = ttk.Frame(self.app.context_frame); stroke_frame.pack(fill=tk.X, pady=5, padx=5)
                ttk.Label(stroke_frame, text="Stroke Width:").pack(side=tk.LEFT)
                ttk.Entry(stroke_frame, textvariable=self.app.shape_stroke_width_var, width=4).pack(side=tk.LEFT)

            ttk.Button(self.app.context_frame, text="Apply Changes", command=self.update_selected_from_controls).pack(pady=10)

    def on_scale_slider_change(self, value):
        tag = self.app.selected_item_tag
        if not tag: return
        props = self.app.state_manager.get_properties(tag)
        if not props or 'original_width' not in props: return

        scale_factor = round(float(value)) / 100.0
        if scale_factor == 0: scale_factor = 0.01

        new_width = int(props['original_width'] * scale_factor)
        self.app.shape_width_var.set(new_width)
        if props['type'] == 'square':
            self.app.shape_height_var.set(new_width)
        else:
            self.app.shape_height_var.set(int(props['original_height'] * scale_factor))

        self.update_selected_from_controls()

    def update_controls_from_selection(self, tag):
        props = self.app.state_manager.get_properties(tag)
        self.update_context_controls(props)
        if not props: return

        if props['type'] == 'text':
            self.app.font_var.set(props['font'].replace('.ttf', ''))
            self.app.font_size_var.set(props['size'])
            self.app.text_fill_color_btn.config(bg=props['color'])
            self.app.text_stroke_color_btn.config(bg=props['stroke_color'])
        elif props['type'] in ['rectangle', 'square', 'circle', 'triangle', 'image']:
            self.app.shape_width_var.set(props['width'])
            self.app.shape_height_var.set(props['height'])
            self.app.shape_stroke_width_var.set(props.get('stroke_width', 2))
            if props.get('original_width'):
                scale = (props['width'] / props['original_width']) * 100
                self.app.shape_scale_var.set(scale)

    def update_listbox_selection(self, tag):
        layer_order = self.app.state_manager.get_layer_order()
        if tag in layer_order:
            idx = layer_order.index(tag)
            self.app.layer_listbox.selection_clear(0, tk.END)
            self.app.layer_listbox.selection_set(idx)

    def update_layer_list(self):
        current_selection = self.app.layer_listbox.curselection()
        self.app.layer_listbox.delete(0, tk.END)
        for tag in self.app.state_manager.get_layer_order():
            props = self.app.state_manager.get_properties(tag)
            if props:
                name = f"{props['type'].capitalize()}: {props.get('text', props.get('file', '...'))[:20]}"
                self.app.layer_listbox.insert(tk.END, name)
        self.app.layer_listbox.insert(tk.END, "[Background Image]")
        last_index = self.app.layer_listbox.size() - 1
        if last_index >= 0: self.app.layer_listbox.itemconfig(last_index, {'fg': 'grey'})
        if current_selection and current_selection[0] < self.app.layer_listbox.size():
            self.app.layer_listbox.selection_set(current_selection[0])

    def on_slider_change(self, value):
        self.update_selected_from_controls()

    def update_selected_from_controls(self):
        tag = self.app.selected_item_tag
        if not tag: return
        props = self.app.state_manager.get_properties(tag)
        if not props: return

        updates = {}
        if props['type'] == 'text':
            updates = {'font': self.app.font_var.get()+'.ttf', 'size': self.app.font_size_var.get(), 'color': self.app.text_fill_color_btn['bg'], 'stroke_color': self.app.text_stroke_color_btn['bg']}
        elif props['type'] in ['rectangle', 'square', 'circle', 'triangle']:
            updates = {'width': self.app.shape_width_var.get(), 'height': self.app.shape_height_var.get(), 'color': self.app.shape_fill_color_btn['bg'], 'stroke_color': self.app.shape_stroke_color_btn['bg'], 'stroke_width': self.app.shape_stroke_width_var.get()}
        elif props['type'] == 'image':
            updates = {'width': self.app.shape_width_var.get(), 'height': self.app.shape_height_var.get()}

        self.app.state_manager.update_properties(tag, updates)
        self.redraw_all_objects()

    def add_text(self):
        props = {'type': 'text', 'text': self.app.text_input.get("1.0", tk.END).strip(), 'font': self.app.font_var.get()+'.ttf', 'size': self.app.font_size_var.get(), 'color': '#FFFFFF', 'stroke_color': '#000000', 'stroke_width': 2, 'rel_x': 0.1, 'rel_y': 0.1}
        if not props['text']: return
        tag = self.app.state_manager.add_object(props)
        self.redraw_all_objects()
        self.select_item(tag)

    def add_shape(self):
        shape_type = self.app.primitive_shape_var.get().lower()
        width, height = (150, 150) if shape_type == 'square' else (200, 100)
        if shape_type == 'circle': width = height = 150

        props = {'type': shape_type, 'color': '#3498db', 'stroke_color': '#2980b9', 'stroke_width': 4, 'width': width, 'height': height, 'rel_x': 0.2, 'rel_y': 0.2, 'original_width': width, 'original_height': height}
        tag = self.app.state_manager.add_object(props)
        self.redraw_all_objects()
        self.select_item(tag)

    def add_image_asset(self):
        asset_name = self.app.asset_var.get()
        if not asset_name: return
        try:
            folder = self.app.SHAPES_DIR if asset_name in self.app.available_shapes else self.app.IMAGES_DIR
            img = Image.open(os.path.join(folder, asset_name))
            props = {'type': 'image', 'file': asset_name, 'width': img.width, 'height': img.height, 'rel_x': 0.2, 'rel_y': 0.2, 'original_width': img.width, 'original_height': img.height}
            tag = self.app.state_manager.add_object(props)
            self.redraw_all_objects()
            self.select_item(tag)
        except Exception as e:
            messagebox.showerror("Asset Error", f"Could not load image file:\n{e}")

    def move_layer(self, direction):
        tag = self.app.selected_item_tag
        if not tag: return
        self.app.state_manager.move_layer(tag, direction)
        self.redraw_all_objects()

    def delete_selected(self):
        tag = self.app.selected_item_tag
        if tag:
            self.app.state_manager.delete_object(tag)
            self.app.selected_item_tag = None
            self.redraw_all_objects()

    def center_selected(self):
        pass