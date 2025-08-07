# app/src/automation/workflow_ui_components/results/success_display.py

import tkinter as tk
from tkinter import ttk
from .action_buttons import ActionButtons
from .breakdown_handler import BreakdownHandler

class SuccessDisplay:
    """Handles success results display"""
    
    def __init__(self, parent_tab, theme):
        self.parent_tab = parent_tab
        self.theme = theme
        self.action_buttons = ActionButtons(theme)
        self.breakdown_handler = BreakdownHandler(theme)
        
    def show_results(self, result, on_open_folder, on_done):
        """Show success results - CLEAN FOCUSED METHOD"""
        
        # Export breakdown file
        self.breakdown_handler.export_breakdown_file(result)
        
        # Clear existing content
        for widget in self.parent_tab.results_content.winfo_children():
            widget.destroy()
        
        # Create main container
        main_container = ttk.Frame(self.parent_tab.results_content, style='White.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header - Single icon, no duplicate
        self._create_header(main_container)
        
        # Summary
        self._create_summary(main_container, result)
        
        # Processing Report section - ONLY BUTTON
        self._create_breakdown_section(main_container)
        
        # Action Buttons
        self.action_buttons.create_success_buttons(main_container, on_open_folder, on_done)
    
    def _create_header(self, parent):
        """Create header with single icon"""
        header_frame = ttk.Frame(parent, style='White.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack(fill=tk.X)
        
        # Single icon only
        icon_label = ttk.Label(title_container, text="✅", font=('Segoe UI', 28),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # No duplicate checkmark in text
        ttk.Label(text_frame, text="Processing Complete!", 
                 style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="Your videos have been processed successfully", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
    
    def _create_summary(self, parent, result):
        """Create summary section"""
        summary_frame = ttk.Frame(parent, style='White.TFrame')
        summary_frame.pack(fill=tk.X, pady=(0, 30))
        
        ttk.Label(summary_frame, text=f"✅ Processing completed in {result.duration}",
                 style='Body.TLabel', font=('Segoe UI', 12, 'bold'),
                 foreground=self.theme.colors['success']).pack(anchor=tk.W)
        
        if result.processed_files:
            count = len(result.processed_files)
            ttk.Label(summary_frame, text=f"📊 {count} video{'s' if count != 1 else ''} processed successfully",
                     style='Body.TLabel', font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(5, 0))
    
    def _create_breakdown_section(self, parent):
        """Create breakdown report section"""
        breakdown_frame = ttk.Frame(parent, style='White.TFrame')
        breakdown_frame.pack(fill=tk.X, pady=(0, 30))
        
        ttk.Label(breakdown_frame, text="📝 Processing Report:", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Smaller breakdown button
        breakdown_btn = ttk.Button(breakdown_frame, text="View Breakdown Report", 
                                 style='Secondary.TButton',
                                 command=self.breakdown_handler.open_breakdown_file)
        breakdown_btn.pack(anchor=tk.W)