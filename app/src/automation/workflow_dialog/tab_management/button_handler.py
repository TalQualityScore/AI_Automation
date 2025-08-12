# app/src/automation/workflow_dialog/tab_management/button_handler.py
"""Button Handler - Manages all button creation and actions - FIXED WITH OVERLAY"""

import tkinter as tk
from tkinter import ttk

class ButtonHandler:
    """Handles all button-related operations"""
    
    def __init__(self, tab_manager):
        self.tm = tab_manager  # Reference to TabManager
    
    def cleanup_confirmation_buttons(self):
        """Clean up any existing confirmation buttons"""
        if hasattr(self.tm, 'confirmation_buttons') and self.tm.confirmation_buttons:
            try:
                self.tm.confirmation_buttons.destroy()
            except:
                pass
            self.tm.confirmation_buttons = None
    
    def add_confirmation_buttons(self):
        """Add action buttons - PROPERLY POSITIONED"""
        print("=" * 50)
        print("DEBUG: add_confirmation_buttons() called")
        
        # Clean up first
        self.cleanup_confirmation_buttons()
        
        # Create button frame using tk.Frame (more reliable than ttk)
        button_frame = tk.Frame(self.tm.dialog.root, bg='white', height=60)
        
        # Position at y=670 (window is 750px tall, leaves 80px at bottom)
        button_frame.place(x=70, y=670, width=400, height=60)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="❌ CANCEL",
            font=('Segoe UI', 11),
            bg='#f0f0f0',
            command=self.tm.dialog._on_cancel
        )
        cancel_btn.place(x=50, y=15, width=120, height=35)
        
        # Confirm button
        confirm_btn = tk.Button(
            button_frame,
            text="✅ CONFIRM & RUN",
            font=('Segoe UI', 11, 'bold'),
            bg='#0078d4',
            fg='white',
            command=self._on_confirm_with_transitions
        )
        confirm_btn.place(x=230, y=15, width=140, height=35)
        
        # Store reference
        self.tm.confirmation_buttons = button_frame
        
        # Force visibility
        button_frame.lift()
        self.tm.dialog.root.update()
        
        print(f"DEBUG: Buttons positioned at y=670")
        print(f"  Frame visible: {button_frame.winfo_viewable()}")
        print("=" * 50)
    
    def add_confirmation_buttons_overlay(self):
        """Add buttons as a toplevel overlay - FIXED VERSION"""
        print("=" * 50)
        print("DEBUG: add_confirmation_buttons_overlay() called")
        
        # Clean up any existing buttons
        self.cleanup_confirmation_buttons()
        
        # Create button frame with explicit size
        button_frame = tk.Frame(self.tm.dialog.root, bg='#f0f0f0', width=460, height=70)
        button_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Use place to position at bottom (since pack isn't working)
        button_frame.place(x=40, y=650, width=460, height=70)
        
        # Create buttons directly in frame with grid
        cancel_btn = tk.Button(
            button_frame,
            text="❌ CANCEL",
            font=('Segoe UI', 11),
            bg='white',
            fg='black',
            bd=2,
            relief='raised',
            command=self.tm.dialog._on_cancel
        )
        cancel_btn.place(x=80, y=18, width=130, height=35)
        
        confirm_btn = tk.Button(
            button_frame,
            text="✅ CONFIRM & RUN",
            font=('Segoe UI', 11, 'bold'),
            bg='#0078d4',
            fg='white',
            bd=2,
            relief='raised',
            command=self._on_confirm_with_transitions
        )
        confirm_btn.place(x=250, y=18, width=130, height=35)
        
        # Store reference
        self.tm.confirmation_buttons = button_frame
        
        # Force to top
        button_frame.lift()
        button_frame.tkraise()
        
        # Force updates
        button_frame.update()
        self.tm.dialog.root.update_idletasks()
        self.tm.dialog.root.update()
        
        print(f"DEBUG: Overlay buttons added with place()")
        print(f"  Frame exists: {button_frame.winfo_exists()}")
        print(f"  Frame mapped: {button_frame.winfo_ismapped()}")
        print(f"  Frame visible: {button_frame.winfo_viewable()}")
        print(f"  Frame geometry: {button_frame.winfo_geometry()}")
        print(f"  Cancel visible: {cancel_btn.winfo_viewable()}")
        print(f"  Confirm visible: {confirm_btn.winfo_viewable()}")
        
        # Check actual positions
        print("DEBUG: Actual widget positions:")
        print(f"  Button frame: x={button_frame.winfo_x()}, y={button_frame.winfo_y()}")
        print(f"  Cancel btn: x={cancel_btn.winfo_x()}, y={cancel_btn.winfo_y()}")
        print(f"  Confirm btn: x={confirm_btn.winfo_x()}, y={confirm_btn.winfo_y()}")
        
        print("DEBUG: Window children after adding buttons:")
        for child in self.tm.dialog.root.winfo_children():
            try:
                geo = child.winfo_geometry()
                vis = child.winfo_viewable()
                print(f"  - {child.__class__.__name__}: {geo} (visible: {vis})")
            except:
                pass
        print("=" * 50)

    
    def _on_confirm_with_transitions(self):
        """Handle confirm with transition settings"""
        # Get the transition setting from confirmation tab
        use_transitions = True
        if hasattr(self.tm.confirmation_tab, 'get_transition_setting'):
            use_transitions = self.tm.confirmation_tab.get_transition_setting()
        
        # Store the transition setting for processing
        self.tm.dialog.use_transitions = use_transitions
        
        print(f"🎬 Starting processing with transitions: {'ENABLED' if use_transitions else 'DISABLED'}")
        
        # Call the original confirm handler
        self.tm.dialog._on_confirm()
    
    def add_readonly_message(self, message):
        """Add read-only message for completed tabs"""
        # Clean up first
        self.cleanup_confirmation_buttons()
        
        message_frame = ttk.Frame(self.tm.dialog.root, style='White.TFrame')
        message_frame.pack(fill=tk.X, padx=40, pady=(0, 30), side=tk.BOTTOM)
        
        ttk.Label(
            message_frame, 
            text=message, 
            style='Body.TLabel',
            font=('Segoe UI', 11, 'italic'),
            foreground=self.tm.dialog.theme.colors['text_secondary']
        ).pack()
        
        self.tm.confirmation_buttons = message_frame
    
    def add_active_processing_buttons(self, parent):
        """Add cancel button for active processing"""
        cancel_frame = ttk.Frame(parent, style='White.TFrame')
        cancel_frame.pack(fill=tk.X, pady=30)
        
        cancel_container = ttk.Frame(cancel_frame, style='White.TFrame')
        cancel_container.pack()
        
        self.tm.processing_tab.cancel_btn = ttk.Button(
            cancel_container, 
            text="❌ Cancel Processing", 
            style='Secondary.TButton',
            command=self.tm.dialog._on_cancel
        )
        self.tm.processing_tab.cancel_btn.pack()
    
    def add_completed_processing_buttons(self, parent):
        """Add buttons for completed processing tab"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=30)
        
        info_container = ttk.Frame(info_frame, style='White.TFrame')
        info_container.pack()
        
        ttk.Label(
            info_container, 
            text="✅ Processing completed successfully!", 
            style='Body.TLabel', 
            font=('Segoe UI', 12, 'bold'),
            foreground=self.tm.dialog.theme.colors['success']
        ).pack(pady=10)
        
        ttk.Button(
            info_container, 
            text="📊 View Results", 
            style='Accent.TButton',
            command=lambda: self.tm.show_tab(2)
        ).pack()
    
    def add_inactive_processing_message(self, parent):
        """Add message for inactive processing tab"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=30)
        
        info_container = ttk.Frame(info_frame, style='White.TFrame')
        info_container.pack()
        
        ttk.Label(
            info_container, 
            text="⏸️ Processing not currently active", 
            style='Body.TLabel', 
            font=('Segoe UI', 11),
            foreground=self.tm.dialog.theme.colors['text_secondary']
        ).pack(pady=10)
        
        ttk.Label(
            info_container, 
            text="Return to Confirmation tab to start processing", 
            style='Body.TLabel', 
            font=('Segoe UI', 9, 'italic'),
            foreground=self.tm.dialog.theme.colors['text_secondary']
        ).pack()