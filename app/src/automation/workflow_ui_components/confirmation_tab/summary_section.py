# app/src/automation/workflow_ui_components/confirmation_tab/summary_section.py
"""
UPDATED Processing Summary Section
Add multi-mode display support to existing file
MINIMAL CHANGES to existing structure
"""

import tkinter as tk
from tkinter import ttk

class SummarySection:
    """Processing summary section with multi-mode support"""
    
    def __init__(self, parent, data, theme, main_tab):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.main_tab = main_tab
        self.section_frame = None
        self.create_section()
    
    def create_section(self):
        """Create processing summary section - UNCHANGED"""
        self.section_frame = ttk.Frame(self.parent, style='White.TFrame')
        self.section_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.section_frame, text="📋 Processing Summary", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        self.summary_frame = ttk.Frame(self.section_frame, style='White.TFrame')
        self.summary_frame.pack(fill=tk.X, padx=(15, 0), pady=2)
        
        self._update_summary_content()
    
    def _update_summary_content(self):
        """UPDATED: Update summary content with multi-mode support"""
        # Clear existing content
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        # DEBUG: Let's see what's actually in the data
        print("=" * 50)
        print("DEBUG: Summary Section - Inspecting data")
        print(f"DEBUG: data type = {type(self.data)}")
        
        if hasattr(self.data, 'client_videos'):
            print(f"DEBUG: client_videos type = {type(self.data.client_videos)}")
            if isinstance(self.data.client_videos, list):
                print(f"DEBUG: client_videos length = {len(self.data.client_videos)}")
                for i, video in enumerate(self.data.client_videos):
                    print(f"DEBUG:   Video {i+1}: {video}")
            else:
                print(f"DEBUG: client_videos value = {self.data.client_videos}")
        print("=" * 50)
        
        # Get REAL video count from the actual data
        video_count = self._get_video_count()
        
        ttk.Label(self.summary_frame, 
                text=f"• {video_count} client video{'s' if video_count != 1 else ''} will be processed",
                style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
        
        # Get selected processing modes
        selected_modes = self._get_selected_modes()
        
        if len(selected_modes) == 1:
            # Single mode display
            mode_display = self._get_mode_display(selected_modes[0])
            endpoint = self._get_endpoint_from_mode(selected_modes[0])
            
            ttk.Label(self.summary_frame, 
                    text=f"• Videos will be connected to: {endpoint}",
                    style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
        else:
            # Multi-mode display
            ttk.Label(self.summary_frame, 
                    text=f"• Processing modes: {len(selected_modes)} selected",
                    style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
            
            for i, mode in enumerate(selected_modes, 1):
                mode_display = self._get_mode_display(mode)
                ttk.Label(self.summary_frame, 
                        text=f"    {i}. {mode_display}",
                        style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
            
            ttk.Label(self.summary_frame, 
                    text=f"• Output: {len(selected_modes)} separate folders will be created",
                    style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
        
        # Transition setting
        if self.main_tab.use_transitions.get():
            ttk.Label(self.summary_frame, 
                    text="• Processing type: with smooth transitions",
                    style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
        else:
            ttk.Label(self.summary_frame, 
                    text="• Processing type: without transitions",
                    style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
        
        # Estimated time
        estimated_time = self._calculate_estimated_time(video_count, selected_modes)
        ttk.Label(self.summary_frame, 
                text=f"• Estimated processing time: {estimated_time}",
                style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
    
    def _get_video_count(self):
        """Get actual video count from data"""
        video_count = 0
        
        if hasattr(self.data, 'client_videos') and self.data.client_videos:
            if isinstance(self.data.client_videos, list):
                # Count only non-empty entries
                actual_videos = [v for v in self.data.client_videos if v]
                video_count = len(actual_videos)
            else:
                video_count = 1
        
        # If we still have 0, default to 1
        if video_count == 0:
            video_count = 1
        
        return video_count
    
    def _get_selected_modes(self):
        """Get currently selected processing modes"""
        if hasattr(self.main_tab, 'get_selected_processing_modes'):
            return self.main_tab.get_selected_processing_modes()
        
        # Fallback to single mode
        current_mode = self.main_tab.processing_mode_var.get() if hasattr(self.main_tab, 'processing_mode_var') else getattr(self.data, 'processing_mode', 'Add Quiz Outro')
        
        # Convert display name to code
        mode_map = {
            "Save As Is": "save_only",
            "Add Quiz Outro": "quiz_only",
            "Add Connector + Quiz": "connector_quiz",
            "Add SVSL": "svsl_only",
            "Add Connector + SVSL": "connector_svsl",
            "Add VSL": "vsl_only",
            "Add Connector + VSL": "connector_vsl"
        }
        
        mode_code = mode_map.get(current_mode, "quiz_only")
        return [mode_code]
    
    def _get_mode_display(self, mode):
        """Get display name for processing mode"""
        mode_displays = {
            "save_only": "Save As Is",
            "quiz_only": "Add Quiz Outro",
            "connector_quiz": "Add Connector + Quiz",
            "svsl_only": "Add SVSL",
            "connector_svsl": "Add Connector + SVSL",
            "vsl_only": "Add VSL",
            "connector_vsl": "Add Connector + VSL"
        }
        return mode_displays.get(mode, mode.replace('_', ' ').title())
    
    def _get_endpoint_from_mode(self, mode):
        """Get endpoint description from processing mode"""
        if 'quiz' in mode:
            return "Quiz Outro"
        elif 'svsl' in mode:
            return "SVSL"
        elif 'vsl' in mode:
            return "VSL"
        elif 'save' in mode:
            return "No processing (Save As Is)"
        else:
            return "Quiz Outro"
    
    def _calculate_estimated_time(self, video_count, selected_modes):
        """Calculate estimated processing time for multiple modes"""
        if not selected_modes or video_count == 0:
            return "0 minutes"
        
        # Base time per video per mode
        time_per_video_per_mode = {
            "save_only": 0.5,
            "quiz_only": 2,
            "vsl_only": 2.5,
            "svsl_only": 2.5,
            "connector_quiz": 3,
            "connector_vsl": 3.5,
            "connector_svsl": 3.5
        }
        
        # Calculate total time
        total_minutes = 0
        for mode in selected_modes:
            mode_time = time_per_video_per_mode.get(mode, 2)
            total_minutes += video_count * mode_time
        
        # Add overhead for multiple modes
        if len(selected_modes) > 1:
            total_minutes += len(selected_modes) * 1  # 1 minute overhead per mode
        
        # Format time
        if total_minutes < 1:
            return "< 1 minute"
        elif total_minutes < 60:
            return f"{int(total_minutes)} minute{'s' if total_minutes != 1 else ''}"
        else:
            hours = int(total_minutes // 60)
            minutes = int(total_minutes % 60)
            if minutes == 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{hours}h {minutes}m"
    
    def refresh(self):
        """Refresh summary when settings change - UNCHANGED for backward compatibility"""
        self._update_summary_content()
    
    def refresh_with_modes(self, selected_modes):
        """Refresh summary when modes change"""
        # Update the display based on selected modes
        if hasattr(self, 'mode_label'):
            if len(selected_modes) > 1:
                self.mode_label.config(text=f"• Processing modes: {len(selected_modes)} selected")
                # Update any other multi-mode specific displays
                mode_names = []
                for mode in selected_modes:
                    mode_name = {
                        'quiz_only': 'Add Quiz Outro',
                        'vsl_only': 'Add VSL',
                        'svsl_only': 'Add SVSL',
                        'connector_quiz': 'Add Connector + Quiz',
                        'connector_vsl': 'Add Connector + VSL',
                        'connector_svsl': 'Add Connector + SVSL',
                        'save_only': 'Save As Is'
                    }.get(mode, mode)
                    mode_names.append(mode_name)
                
                # Update the detailed mode list if you have one
                if hasattr(self, 'mode_details'):
                    self.mode_details.config(text=f"  1. {mode_names[0]}\n  2. {mode_names[1]}")
            else:
                mode_name = {
                    'quiz_only': 'Add Quiz Outro',
                    'vsl_only': 'Add VSL',
                    'svsl_only': 'Add SVSL',
                    'connector_quiz': 'Add Connector + Quiz',
                    'connector_vsl': 'Add Connector + VSL',
                    'connector_svsl': 'Add Connector + SVSL',
                    'save_only': 'Save As Is'
                }.get(selected_modes[0], selected_modes[0])
                self.mode_label.config(text=f"• Processing type: {mode_name}")