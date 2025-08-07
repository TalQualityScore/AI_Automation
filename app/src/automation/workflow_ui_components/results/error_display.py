# app/src/automation/workflow_ui_components/results/error_display.py

import tkinter as tk
from tkinter import ttk
from .action_buttons import ActionButtons

class ErrorDisplay:
    """Handles error results display"""
    
    def __init__(self, parent_tab, theme):
        self.parent_tab = parent_tab
        self.theme = theme
        self.action_buttons = ActionButtons(theme)
        
    def show_results(self, result, on_copy_error, on_close):
        """Show error results - CLEAN METHOD"""
        
        # Clear existing content
        for widget in self.parent_tab.results_content.winfo_children():
            widget.destroy()
        
        # Create main container
        main_container = ttk.Frame(self.parent_tab.results_content, style='White.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self._create_error_header(main_container)
        
        # Error details
        self._create_error_details(main_container, result)
        
        # Action buttons
        self.action_buttons.create_error_buttons(main_container, on_copy_error, on_close)
    
    def _create_error_header(self, parent):
        """Create error header"""
        header_frame = ttk.Frame(parent, style='White.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack(fill=tk.X)
        
        icon_label = ttk.Label(title_container, text="❌", font=('Segoe UI', 28),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(text_frame, text="Processing Failed", 
                 style='Header.TLabel', foreground=self.theme.colors['error']).pack(anchor=tk.W)
        ttk.Label(text_frame, text="An error occurred during processing", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
    
    def _create_error_details(self, parent, result):
        """Create error details section"""
        error_frame = ttk.LabelFrame(parent, text="Error Details", 
                                   style='White.TLabelframe')
        error_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Error message with scrollbar
        text_container = ttk.Frame(error_frame, style='White.TFrame')
        text_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        error_text = tk.Text(text_container, wrap=tk.WORD, height=8, width=60,
                           font=('Consolas', 10), relief='flat', 
                           bg='#f8f8f8', fg='#d13212')
        scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=error_text.yview)
        error_text.configure(yscrollcommand=scrollbar.set)
        
        error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert error details
        error_details = f"Error: {result.error_message}\n"
        if hasattr(result, 'error_details') and result.error_details:
            error_details += f"\nDetails:\n{result.error_details}"
        error_text.insert('1.0', error_details)
        error_text.config(state='disabled')