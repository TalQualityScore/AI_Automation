# app/src/automation/workflow_dialog/tab_management/button_handler.py
"""Button Handler - Manages all button creation and actions - FIXED STYLING"""

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
    
    def add_confirmation_buttons_overlay(self):
        """Add buttons as overlay with improved styling - FIXED VERSION"""
        print("=" * 50)
        print("DEBUG: add_confirmation_buttons_overlay() called")
        
        # Clean up any existing buttons
        self.cleanup_confirmation_buttons()
        
        # Get window dimensions for dynamic positioning
        window_height = self.tm.dialog.root.winfo_height()
        window_width = self.tm.dialog.root.winfo_width()
        
        # Calculate button position (85px from bottom for better spacing)
        button_y = max(window_height - 85, 765)
        
        # Create button frame with proper styling
        button_frame = tk.Frame(
            self.tm.dialog.root, 
            bg='white',  # White background instead of gray
            relief='flat',
            bd=0,
            width=480, 
            height=60
        )
        button_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Use place to position dynamically
        button_frame.place(x=30, y=button_y, width=480, height=60)
        
        # Create buttons with improved styling
        cancel_btn = tk.Button(
            button_frame,
            text="❌ CANCEL",
            font=('Segoe UI', 10, 'normal'),
            bg='#f3f2f1',  # Light gray background
            fg='#323130',  # Dark gray text
            activebackground='#e1dfdd',  # Hover color
            activeforeground='#323130',
            bd=1,
            relief='solid',
            borderwidth=1,
            cursor='hand2',
            padx=20,
            pady=8,
            command=self.tm.dialog._on_cancel
        )
        cancel_btn.place(x=90, y=15, width=140, height=32)
        
        confirm_btn = tk.Button(
            button_frame,
            text="✅ CONFIRM & RUN",
            font=('Segoe UI', 10, 'bold'),
            bg='#0078d4',  # Microsoft blue
            fg='white',
            activebackground='#106ebe',  # Darker blue on hover
            activeforeground='white',
            bd=0,
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8,
            command=self._on_confirm_with_transitions
        )
        confirm_btn.place(x=250, y=15, width=140, height=32)
        
        # Store reference
        self.tm.confirmation_buttons = button_frame
        
        # Force visibility with proper layering
        button_frame.lift()
        button_frame.tkraise()
        
        # Force updates
        self.tm.dialog.root.update_idletasks()
        self.tm.dialog.root.update()
        
        print(f"DEBUG: Improved overlay buttons added")
        print(f"  Position: x=30, y={button_y}")
        print(f"  Frame size: 480x60")
        print(f"  Frame visible: {button_frame.winfo_viewable()}")
        print(f"  Cancel visible: {cancel_btn.winfo_viewable()}")
        print(f"  Confirm visible: {confirm_btn.winfo_viewable()}")
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
        
        # Get window dimensions for dynamic positioning
        window_height = self.tm.dialog.root.winfo_height()
        button_y = max(window_height - 85, 765)
        
        message_frame = tk.Frame(
            self.tm.dialog.root,
            bg='white',
            relief='flat',
            bd=0,
            width=480,
            height=60
        )
        message_frame.place(x=30, y=button_y, width=480, height=60)
        
        message_label = tk.Label(
            message_frame,
            text=message,
            font=('Segoe UI', 10, 'italic'),
            bg='white',
            fg='#605e5c',  # Medium gray
            wraplength=450,
            justify='center'
        )
        message_label.place(x=15, y=20, width=450, height=20)
        
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
            text="✅ Processing completed successfully! Check the Results tab for details.", 
            style='Body.TLabel',
            font=('Segoe UI', 11, 'italic'),
            foreground='#107c10'  # Green color
        ).pack(pady=(0, 15))
    
    def add_inactive_processing_message(self, parent):
        """Add message for inactive processing tab"""
        info_frame = ttk.Frame(parent, style='White.TFrame')
        info_frame.pack(fill=tk.X, pady=30)
        
        info_container = ttk.Frame(info_frame, style='White.TFrame')
        info_container.pack()
        
        ttk.Label(
            info_container, 
            text="⚠️ Processing has not been started yet. Return to the Confirmation tab to begin.", 
            style='Body.TLabel',
            font=('Segoe UI', 11, 'italic'),
            foreground='#d83b01'  # Orange-red color
        ).pack()