# app/src/automation/workflow_ui_components/processing_tab.py - FIXED VERSION
import tkinter as tk
from tkinter import ttk

class ProcessingTab:
    """Handles the processing tab content and logic - FIXED without time estimation"""
    
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.frame = None
        self.progress_var = None
        self.progress_label = None
        self.step_label = None
        self.cancel_btn = None
        
    def create_tab(self, estimated_time: str):
        """Create processing tab content"""
        self.frame = ttk.Frame(self.parent, style='White.TFrame')
        
        # Processing header
        header_frame = ttk.Frame(self.frame, style='White.TFrame')
        header_frame.pack(fill=tk.X, pady=(40, 30))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack()
        
        icon_label = ttk.Label(title_container, text="⚙️", font=('Segoe UI', 24),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT)
        
        ttk.Label(text_frame, text="Processing Videos", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="Please wait while we process your videos...", 
                 style='Body.TLabel', font=('Segoe UI', 11),
                 foreground=self.theme.colors['text_secondary']).pack(anchor=tk.W)
        
        # Progress section
        progress_frame = ttk.Frame(self.frame, style='White.TFrame')
        progress_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.progress_var,
                                           length=500)
        self.progress_bar.pack(pady=(0, 15))
        
        # Progress percentage
        self.progress_label = ttk.Label(progress_frame, text="Initializing...",
                                       style='Body.TLabel', font=('Segoe UI', 11, 'bold'))
        self.progress_label.pack(pady=(0, 8))
        
        # Current step
        self.step_label = ttk.Label(progress_frame, text="Starting validation process...",
                                   style='Body.TLabel', font=('Segoe UI', 10))
        self.step_label.pack(pady=(0, 15))
        
        # REMOVED: Time estimation (unreliable)
        # Show estimated duration only initially
        ttk.Label(progress_frame, text=f"Estimated duration: {estimated_time}",
                 style='Body.TLabel', font=('Segoe UI', 9, 'italic'),
                 foreground=self.theme.colors['text_secondary']).pack()
        
        return self.frame
    
    def update_progress(self, progress: float, step_text: str = "", elapsed_time: float = 0):
        """Update progress bar and labels - SIMPLIFIED without time calculation"""
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{int(progress)}%")
        
        if step_text:
            self.step_label.config(text=step_text)
        
        # REMOVED: Time remaining calculation - too unreliable