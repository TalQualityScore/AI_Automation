# app/src/automation/workflow_ui_components/confirmation_tab/summary_section/__init__.py
"""
Processing Summary Section - Main Module Entry Point
MODULAR VERSION with enhanced multi-mode support and transitions fix
"""

import tkinter as tk
from tkinter import ttk

from .content_generators import ContentGenerators
from .mode_analyzers import ModeAnalyzers
from .time_calculators import TimeCalculators
from .display_formatters import DisplayFormatters
from .refresh_handlers import RefreshHandlers

class SummarySection:
    """Processing summary section with multi-mode support and transitions fix - MODULAR VERSION"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        self.section_frame = None
        
        # Initialize modular components
        self.content_generators = ContentGenerators(self)
        self.mode_analyzers = ModeAnalyzers(self)
        self.time_calculators = TimeCalculators(self)
        self.display_formatters = DisplayFormatters(self)
        self.refresh_handlers = RefreshHandlers(self)
        
        # Store references to labels for dynamic updates
        self.video_label = None
        self.mode_label = None
        self.mode_details = None
        self.transitions_label = None
        self.output_label = None
        self.time_label = None
        
        self.create_section()
    
    def create_section(self):
        """Create processing summary section - MODULAR APPROACH"""
        self.section_frame = ttk.Frame(self.parent, style='White.TFrame')
        self.section_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create title
        ttk.Label(self.section_frame, text="📋 Processing Summary", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        # Create content frame
        self.summary_frame = ttk.Frame(self.section_frame, style='White.TFrame')
        self.summary_frame.pack(fill=tk.X, padx=(15, 0), pady=2)
        
        # Generate initial content
        self._update_summary_content()
        
        print("✅ Summary section created with modular components")
    
    def _update_summary_content(self):
        """MODULAR: Update summary content using specialized components"""
        # Clear existing content
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        # Reset label references
        self._reset_label_references()
        
        # Generate content using modular components
        self.content_generators.generate_all_content()
    
    def _reset_label_references(self):
        """Reset all label references"""
        self.video_label = None
        self.mode_label = None
        self.mode_details = None
        self.transitions_label = None
        self.output_label = None
        self.time_label = None
    
    # Delegate methods to appropriate modules
    def refresh(self):
        """ENHANCED: Refresh summary when settings change"""
        print("DEBUG: Summary refresh() called")
        self.refresh_handlers.handle_general_refresh()
    
    def refresh_with_modes(self, selected_modes):
        """ENHANCED: Refresh summary when modes change"""
        print(f"DEBUG: Summary refresh_with_modes({selected_modes}) called")
        self.refresh_handlers.handle_mode_refresh(selected_modes)
    
    def refresh_data(self, new_data):
        """Refresh section with new data"""
        self.data = new_data
        self.refresh()
        print(f"DEBUG: Summary section refreshed with new data")

# Export for backward compatibility
__all__ = ['SummarySection']