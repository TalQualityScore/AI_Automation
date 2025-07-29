# --- File: app/src/drawing_utils.py ---
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

def create_stroked_text(canvas, x, y, props, font_dir):
    tag = props['tag']
    font_path = os.path.join(font_dir, props['font'])
    try:
        font = ImageFont.truetype(font_path, props['size'])
    except IOError:
        font = ImageFont.load_default()

    stroke_width = props.get('stroke_width', 0)

    temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    bbox = temp_draw.textbbox((0, 0), props['text'], font=font, stroke_width=stroke_width)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if stroke_width > 0 and props.get('stroke_color'):
        draw.text((-bbox[0], -bbox[1]), props['text'], font=font, fill=props['stroke_color'], stroke_width=stroke_width, stroke_fill=props['stroke_color'])
    draw.text((-bbox[0], -bbox[1]), props['text'], font=font, fill=props['color'])

    photo_ref = ImageTk.PhotoImage(img)
    canvas.create_image(x, y, image=photo_ref, anchor=tk.NW, tags=tag)
    return photo_ref

def create_shape(canvas, x, y, props, shapes_dir, images_dir, available_shapes):
    tag = props['tag']
    shape_type = props['type']

    if shape_type in ['rectangle', 'square', 'circle', 'triangle']:
        width = props.get('width', 100)
        height = props.get('height', 100)
        fill = props.get('color', 'blue')
        stroke = props.get('stroke_color', 'black')
        stroke_width = props.get('stroke_width', 2)

        # --- FIX: Draw all shapes with fill and outline to make them clickable ---
        if shape_type == 'rectangle' or shape_type == 'square':
            canvas.create_rectangle(x, y, x + width, y + height, fill=fill, outline=stroke, width=stroke_width, tags=tag)
        elif shape_type == 'circle':
            canvas.create_oval(x, y, x + width, y + height, fill=fill, outline=stroke, width=stroke_width, tags=tag)
        elif shape_type == 'triangle':
            points = [x + width / 2, y, x, y + height, x + width, y + height]
            canvas.create_polygon(points, fill=fill, outline=stroke, width=stroke_width, tags=tag)
        return None

    elif shape_type == 'image':
        try:
            folder = shapes_dir if props['file'] in available_shapes else images_dir
            img = Image.open(os.path.join(folder, props['file'])).resize((props['width'], props['height']), Image.Resampling.LANCZOS)
            photo_ref = ImageTk.PhotoImage(img)
            canvas.create_image(x, y, image=photo_ref, anchor=tk.NW, tags=tag)
            return photo_ref
        except Exception as e:
            print(f"Error drawing image {props.get('file')}: {e}")
            return None