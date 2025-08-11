# app/src/automation/api_clients/account_mapper/dialog_modules/dialog_builder.py
"""
Dialog Builder Module
Builds UI components for the dialog
"""

import tkinter as tk
from tkinter import ttk
from .dialog_constants import DialogConstants

class DialogBuilder:
    """Builds dialog UI components"""
    
    def __init__(self, parent):
        self.parent = parent
        self.constants = DialogConstants
    
    def create_header(self, parent_frame):
        """Create the header section"""
        header_label = tk.Label(
            parent_frame, 
            text=self.constants.WINDOW_TITLE,
            font=self.constants.HEADER_FONT, 
            bg=self.constants.BG_COLOR, 
            fg=self.constants.HEADER_COLOR
        )
        header_label.pack(pady=(0, 15))
        
        instruction_label = tk.Label(
            parent_frame,
            text="Please verify the account and platform detection:",
            font=self.constants.INSTRUCTION_FONT, 
            bg=self.constants.BG_COLOR, 
            fg=self.constants.TEXT_COLOR
        )
        instruction_label.pack(pady=(0, 20))
        
        return header_label, instruction_label
    
    def create_context_label(self, parent_frame, card_url, card_title):
        """Create context label showing card info"""
        if card_url:
            context_text = card_url
            context_prefix = "Card URL: "
        else:
            context_text = card_title[:50] + "..." if len(card_title) > 50 else card_title
            context_prefix = "Card: "
        
        context_label = tk.Label(
            parent_frame,
            text=f"{context_prefix}{context_text}",
            font=self.constants.CONTEXT_FONT, 
            bg=self.constants.BG_COLOR, 
            fg=self.constants.SUBTITLE_COLOR,
            wraplength=440
        )
        context_label.pack(pady=(0, 25))
        
        return context_label
    
    def create_dropdown(self, parent_frame, label_text, options, default_value):
        """Create a dropdown with label"""
        frame = tk.Frame(parent_frame, bg=self.constants.BG_COLOR)
        frame.pack(fill=tk.X, pady=(0, 15))
        
        label = tk.Label(
            frame, 
            text=label_text,
            font=self.constants.LABEL_FONT,
            bg=self.constants.BG_COLOR, 
            fg=self.constants.TEXT_COLOR
        )
        label.pack(anchor=tk.W)
        
        var = tk.StringVar()
        combo = ttk.Combobox(
            frame, 
            textvariable=var,
            font=self.constants.COMBO_FONT, 
            width=40, 
            state='readonly'
        )
        combo['values'] = options
        combo.set(default_value)
        combo.pack(fill=tk.X, pady=(5, 0))
        
        return var, combo
    
    def create_separator(self, parent_frame):
        """Create a horizontal separator"""
        separator = tk.Frame(parent_frame, height=1, bg='#ddd')
        separator.pack(fill=tk.X, pady=(15, 20))
        return separator
    
    def create_apply_button(self, parent_frame, command):
        """Create the Apply button"""
        button_frame = tk.Frame(parent_frame, bg=self.constants.BG_COLOR)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(30, 0))
        
        apply_btn = tk.Button(
            button_frame, 
            text="Apply",
            bg=self.constants.BUTTON_SUCCESS_COLOR, 
            fg='white', 
            font=self.constants.BUTTON_FONT,
            padx=40, 
            pady=15, 
            command=command, 
            cursor='hand2',
            relief='flat', 
            borderwidth=0
        )
        apply_btn.pack(anchor=tk.CENTER)
        
        return apply_btn