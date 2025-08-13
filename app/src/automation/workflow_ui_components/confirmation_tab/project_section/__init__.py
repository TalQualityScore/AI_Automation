# app/src/automation/workflow_ui_components/confirmation_tab/project_section/__init__.py
"""
Project Section - Main Module Entry Point
Coordinates all project section components with proper label width (10)
"""

import tkinter as tk
from tkinter import ttk

from .field_creators import FieldCreators
from .dropdown_handlers import DropdownHandlers  
from .mode_selector import ModeSelector
from .data_helpers import DataHelpers
from .event_handlers import EventHandlers

class ProjectSection:
    """Project information section with multi-select processing modes - MODULAR VERSION"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        
        # Initialize modular components
        self.field_creators = FieldCreators(self)
        self.dropdown_handlers = DropdownHandlers(self)
        self.mode_selector = ModeSelector(self)
        self.data_helpers = DataHelpers(self)
        self.event_handlers = EventHandlers(self)
        
        # Multi-select processing mode variables
        self.mode_vars = {}
        self._init_mode_vars()
        
        self.create_section()
    
    def _init_mode_vars(self):
        """Initialize checkbox variables for multi-select"""
        self.mode_vars = self.mode_selector.init_mode_vars()
        print(f"✅ Mode variables initialized: {list(self.mode_vars.keys())}")
    
    def create_section(self):
        """Create project info section - MODULAR APPROACH"""
        section_frame = ttk.Frame(self.parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 10))
        
        print("📄 Creating project section with modular components...")
        
        # FIXED: All labels now use width=10 for consistency
        # Project name field
        self.field_creators.create_project_field(section_frame)
        
        # Account dropdown
        self.field_creators.create_account_dropdown(section_frame)
        
        # Platform dropdown  
        self.field_creators.create_platform_dropdown(section_frame)
        
        # Multi-select processing mode section
        self.field_creators.create_processing_mode_multiselect(section_frame)
        
        # Info note
        self.field_creators.create_info_note(section_frame)
        
        print("✅ Project section created with all components")
    
    # Delegate methods to appropriate modules
    def get_selected_processing_modes(self):
        """Get list of currently selected processing modes"""
        return self.mode_selector.get_selected_processing_modes()
    
    def set_selected_processing_modes(self, modes):
        """Set selected processing modes programmatically"""
        return self.mode_selector.set_selected_processing_modes(modes)
    
    def refresh_data(self, new_data):
        """Refresh section with new data"""
        self.data = new_data
        print(f"DEBUG: Project section refreshed with new data")

# Export for backward compatibility
__all__ = ['ProjectSection']