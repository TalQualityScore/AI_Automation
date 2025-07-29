# --- File: app/src/ui_controls.py ---
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def create_controls(app, parent_frame):
    app.main_controls_frame = ttk.Frame(parent_frame)
    app.main_controls_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    ttk.Button(app.main_controls_frame, text="Load Video", command=app.file_manager.load_video).pack(fill=tk.X, pady=(0, 10))

    # --- Text Element Controls ---
    app.text_frame = ttk.LabelFrame(app.main_controls_frame, text="Text Element")
    app.text_frame.pack(fill=tk.X, pady=5)
    app.text_input = tk.Text(app.text_frame, height=3); app.text_input.pack(fill=tk.X, padx=5, pady=5); app.text_input.insert("1.0", "Your Text")
    font_control_frame = ttk.Frame(app.text_frame); font_control_frame.pack(fill=tk.X, padx=5)
    app.font_var = tk.StringVar(value="Arial"); app.font_combobox = ttk.Combobox(font_control_frame, textvariable=app.font_var, values=app.available_fonts, state="readonly", width=15); app.font_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True); app.font_combobox.bind('<<ComboboxSelected>>', app.update_selected_from_controls)
    app.font_size_var = tk.IntVar(value=80); app.font_size_slider = ttk.Scale(font_control_frame, from_=1, to=300, variable=app.font_size_var, orient=tk.HORIZONTAL, command=app.on_slider_change); app.font_size_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    app.font_size_entry = ttk.Entry(font_control_frame, textvariable=app.font_size_var, width=4); app.font_size_entry.pack(side=tk.LEFT); app.font_size_entry.bind("<KeyRelease>", app.update_selected_from_controls)

    text_color_frame = ttk.Frame(app.text_frame); text_color_frame.pack(fill=tk.X, padx=5, pady=5)
    app.text_fill_color_btn = tk.Button(text_color_frame, text="Fill", command=lambda: app.choose_color_clicked('text_fill'), bg="#FFFFFF", width=8); app.text_fill_color_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
    app.text_stroke_color_btn = tk.Button(text_color_frame, text="Stroke", command=lambda: app.choose_color_clicked('text_stroke'), bg="#000000", fg="white", width=8); app.text_stroke_color_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    ttk.Button(app.text_frame, text="Add Text", command=app.canvas_manager.add_text).pack(pady=5)

    # --- Shape Drawing Controls ---
    app.draw_shape_frame = ttk.LabelFrame(app.main_controls_frame, text="Draw Shape")
    app.draw_shape_frame.pack(fill=tk.X, pady=10)
    app.primitive_shape_var = tk.StringVar(value="Rectangle")
    shape_options = ["Rectangle", "Square", "Circle", "Triangle"]
    ttk.Combobox(app.draw_shape_frame, textvariable=app.primitive_shape_var, values=shape_options, state="readonly").pack(fill=tk.X, padx=5, pady=(0,5))
    ttk.Button(app.draw_shape_frame, text="Add Shape", command=app.canvas_manager.add_shape).pack(pady=5)

    # --- Asset Library Controls ---
    app.asset_frame = ttk.LabelFrame(app.main_controls_frame, text="Asset Library")
    app.asset_frame.pack(fill=tk.X, pady=5)
    app.asset_var = tk.StringVar(value=app.available_assets[0] if app.available_assets else "")
    ttk.Combobox(app.asset_frame, textvariable=app.asset_var, values=app.available_assets, state="readonly").pack(fill=tk.X, padx=5, pady=(0,5))
    ttk.Button(app.asset_frame, text="Add Asset", command=app.canvas_manager.add_image_asset).pack(pady=5)

    # --- Contextual Properties Frame ---
    app.context_frame = ttk.LabelFrame(app.main_controls_frame, text="Selected Element Properties")
    app.context_frame.pack(fill=tk.X, padx=5, pady=10)

    # Define variables for contextual controls
    app.shape_width_var = tk.IntVar(value=200)
    app.shape_height_var = tk.IntVar(value=100)
    app.shape_scale_var = tk.DoubleVar(value=100.0)
    app.shape_stroke_width_var = tk.IntVar(value=2)

    # --- Layers Frame ---
    app.layer_frame = ttk.LabelFrame(app.main_controls_frame, text="Layers")
    app.layer_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    app.layer_listbox = tk.Listbox(app.layer_frame, selectmode=tk.SINGLE)
    app.layer_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    app.layer_listbox.bind('<<ListboxSelect>>', app.on_layer_select)

    layer_btn_frame = ttk.Frame(app.layer_frame)
    layer_btn_frame.pack(side=tk.LEFT, fill=tk.Y)
    ttk.Button(layer_btn_frame, text="▲", command=lambda: app.canvas_manager.move_layer(1), width=3).pack()
    ttk.Button(layer_btn_frame, text="▼", command=lambda: app.canvas_manager.move_layer(-1), width=3).pack()
    ttk.Button(layer_btn_frame, text="C", command=app.canvas_manager.center_selected, width=3).pack(pady=(10, 0))
    try:
        image = Image.open(app.trash_icon_path)
        image.thumbnail((14, 14), Image.Resampling.LANCZOS)
        app.trash_icon = ImageTk.PhotoImage(image)
        ttk.Button(layer_btn_frame, image=app.trash_icon, command=app.canvas_manager.delete_selected).pack(pady=(5, 0))
    except FileNotFoundError:
        ttk.Button(layer_btn_frame, text="DEL", command=app.canvas_manager.delete_selected).pack(pady=(5, 0))

    # --- FIX: Completed the last line ---
    ttk.Button(app.main_controls_frame, text="Save Layout", command=app.file_manager.save_layout).pack(side=tk.BOTTOM, pady=10)