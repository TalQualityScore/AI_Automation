# --- File: app/src/main_menu.py ---
import tkinter as tk
from tkinter import ttk, messagebox

class MainMenu:
    def __init__(self, root, launch_stitcher_callback, launch_layout_callback, launch_image_gen_callback):
        self.root = root
        self.frame = ttk.Frame(root, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # --- Title ---
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(pady=(20, 40))

        qs_label = ttk.Label(title_frame, text="Quality Score", style="Highlight.TLabel")
        qs_label.pack()

        suite_label = ttk.Label(title_frame, text="AI Automation Suite", style="Header.TLabel")
        suite_label.pack()

        # --- Button Frame ---
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(expand=True)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # --- Stitcher Tool Button ---
        stitcher_btn = ttk.Button(button_frame, text="Video Stitcher", command=launch_stitcher_callback, width=25)
        stitcher_btn.grid(row=0, column=0, padx=10, pady=10)

        # --- Layout Tool Button (WIP) ---
        self.layout_btn = ttk.Button(button_frame, text="Visual Layout Tool", command=launch_layout_callback, width=25, state=tk.DISABLED)
        self.layout_btn.grid(row=0, column=1, padx=10, pady=10)

        wip_label_layout = ttk.Label(button_frame, text="(Work in Progress)", style="WIP.TLabel", cursor="hand2")
        wip_label_layout.grid(row=1, column=1, pady=(0, 10))

        # --- Image Generator Button ---
        image_gen_btn = ttk.Button(button_frame, text="Image Generator", command=launch_image_gen_callback, width=25, state=tk.DISABLED)
        image_gen_btn.grid(row=0, column=2, padx=10, pady=10)

        wip_label_img = ttk.Label(button_frame, text="(Work in Progress)", style="WIP.TLabel")
        wip_label_img.grid(row=1, column=2, pady=(0, 10))

        # --- FIX: Easter Egg is now a triple-click on the WIP label ---
        wip_label_layout.bind("<Triple-1>", self.easter_egg_click)

    def easter_egg_click(self, event):
        self.layout_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Secret Unlocked!", "The Visual Layout Tool has been enabled.")