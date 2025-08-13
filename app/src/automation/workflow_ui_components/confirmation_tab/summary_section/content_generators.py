# app/src/automation/workflow_ui_components/confirmation_tab/summary_section/content_generators.py
"""
Content Generators - Summary Content Creation Logic
Handles generating all summary content with proper formatting
"""

import tkinter as tk
from tkinter import ttk

class ContentGenerators:
    """Handles generation of all summary content"""
    
    def __init__(self, summary_section):
        self.ss = summary_section  # Reference to main SummarySection
    
    def generate_all_content(self):
        """Generate all summary content in the correct order"""
        print("📋 Generating summary content...")
        
        # DEBUG: Show data inspection
        self._debug_data_inspection()
        
        # Generate each content section
        self._generate_video_count_content()
        self._generate_mode_content()
        self._generate_transitions_content()
        self._generate_output_content()
        self._generate_time_content()
        
        print("✅ All summary content generated")
    
    def _debug_data_inspection(self):
        """Debug data inspection"""
        print("=" * 50)
        print("DEBUG: Summary Section - Inspecting data")
        print(f"DEBUG: data type = {type(self.ss.data)}")
        
        if hasattr(self.ss.data, 'client_videos'):
            print(f"DEBUG: client_videos type = {type(self.ss.data.client_videos)}")
            if isinstance(self.ss.data.client_videos, list):
                print(f"DEBUG: client_videos length = {len(self.ss.data.client_videos)}")
                for i, video in enumerate(self.ss.data.client_videos):
                    print(f"DEBUG:   Video {i+1}: {video}")
            else:
                print(f"DEBUG: client_videos value = {self.ss.data.client_videos}")
        print("=" * 50)
    
    def _generate_video_count_content(self):
        """Generate video count display"""
        video_count = self.ss.mode_analyzers.get_video_count()
        
        video_text = f"• {video_count} client video{'s' if video_count != 1 else ''} will be processed"
        self.ss.video_label = ttk.Label(
            self.ss.summary_frame,
            text=video_text,
            style='Body.TLabel',
            font=('Segoe UI', 8)
        )
        self.ss.video_label.pack(anchor=tk.W)
        
        print(f"✅ Video count content: {video_count} videos")
    
    def _generate_mode_content(self):
        """Generate processing mode content"""
        selected_modes = self.ss.mode_analyzers.get_selected_modes()
        
        if len(selected_modes) == 1:
            self._generate_single_mode_content(selected_modes[0])
        else:
            self._generate_multi_mode_content(selected_modes)
    
    def _generate_single_mode_content(self, mode):
        """Generate content for single mode"""
        mode_display = self.ss.mode_analyzers.get_mode_display_name(mode)
        endpoint = self.ss.mode_analyzers.get_endpoint_from_mode(mode)
        
        # Mode display
        self.ss.mode_label = ttk.Label(
            self.ss.summary_frame,
            text=f"• Processing type: {mode_display}",
            style='Body.TLabel',
            font=('Segoe UI', 8)
        )
        self.ss.mode_label.pack(anchor=tk.W)
        
        # Endpoint display (only if not save_only)
        if mode != 'save_only':
            endpoint_label = ttk.Label(
                self.ss.summary_frame,
                text=f"• Videos will be connected to: {endpoint}",
                style='Body.TLabel',
                font=('Segoe UI', 8)
            )
            endpoint_label.pack(anchor=tk.W)
        
        print(f"✅ Single mode content: {mode_display}")
    
    def _generate_multi_mode_content(self, selected_modes):
        """Generate content for multiple modes"""
        # Mode count display
        self.ss.mode_label = ttk.Label(
            self.ss.summary_frame,
            text=f"• Processing modes: {len(selected_modes)} selected",
            style='Body.TLabel',
            font=('Segoe UI', 8)
        )
        self.ss.mode_label.pack(anchor=tk.W)
        
        # Detailed mode list
        details_text = self._build_mode_details_text(selected_modes)
        if details_text:
            self.ss.mode_details = ttk.Label(
                self.ss.summary_frame,
                text=details_text,
                style='Body.TLabel',
                font=('Segoe UI', 8)
            )
            self.ss.mode_details.pack(anchor=tk.W)
        
        print(f"✅ Multi-mode content: {len(selected_modes)} modes")
    
    def _build_mode_details_text(self, selected_modes):
        """Build detailed mode list text"""
        details_lines = []
        for i, mode in enumerate(selected_modes, 1):
            mode_display = self.ss.mode_analyzers.get_mode_display_name(mode)
            details_lines.append(f"  {i}. {mode_display}")
        
        return "\n".join(details_lines) if details_lines else ""
    
    def _generate_transitions_content(self):
        """Generate transitions setting content"""
        self.ss.refresh_handlers.update_transitions_display()
    
    def _generate_output_content(self):
        """Generate output folder content"""
        selected_modes = self.ss.mode_analyzers.get_selected_modes()
        
        if len(selected_modes) > 1:
            output_text = f"• Output: {len(selected_modes)} separate folders will be created"
        else:
            output_text = "• Output: 1 folder will be created"
        
        self.ss.output_label = ttk.Label(
            self.ss.summary_frame,
            text=output_text,
            style='Body.TLabel',
            font=('Segoe UI', 8)
        )
        self.ss.output_label.pack(anchor=tk.W)
        
        print(f"✅ Output content: {len(selected_modes)} folders")
    
    def _generate_time_content(self):
        """Generate estimated time content"""
        video_count = self.ss.mode_analyzers.get_video_count()
        selected_modes = self.ss.mode_analyzers.get_selected_modes()
        
        estimated_time = self.ss.time_calculators.calculate_estimated_time(video_count, selected_modes)
        
        self.ss.time_label = ttk.Label(
            self.ss.summary_frame,
            text=f"• Estimated processing time: {estimated_time}",
            style='Body.TLabel',
            font=('Segoe UI', 8)
        )
        self.ss.time_label.pack(anchor=tk.W)
        
        print(f"✅ Time content: {estimated_time}")
    
    def update_video_count(self, new_count):
        """Update video count display"""
        if self.ss.video_label:
            video_text = f"• {new_count} client video{'s' if new_count != 1 else ''} will be processed"
            self.ss.video_label.config(text=video_text)
    
    def update_mode_display(self, selected_modes):
        """Update mode display"""
        if len(selected_modes) == 1:
            mode_display = self.ss.mode_analyzers.get_mode_display_name(selected_modes[0])
            if self.ss.mode_label:
                self.ss.mode_label.config(text=f"• Processing type: {mode_display}")
            if self.ss.mode_details:
                self.ss.mode_details.config(text="")
        else:
            if self.ss.mode_label:
                self.ss.mode_label.config(text=f"• Processing modes: {len(selected_modes)} selected")
            
            if self.ss.mode_details:
                details_text = self._build_mode_details_text(selected_modes)
                self.ss.mode_details.config(text=details_text)
    
    def update_output_count(self, selected_modes):
        """Update output folder count"""
        if self.ss.output_label:
            if len(selected_modes) > 1:
                output_text = f"• Output: {len(selected_modes)} separate folders will be created"
            else:
                output_text = "• Output: 1 folder will be created"
            self.ss.output_label.config(text=output_text)
    
    def update_estimated_time(self, video_count, selected_modes):
        """Update estimated time display"""
        if self.ss.time_label:
            estimated_time = self.ss.time_calculators.calculate_estimated_time(video_count, selected_modes)
            self.ss.time_label.config(text=f"• Estimated processing time: {estimated_time}")
    
    def create_label(self, text, font_size=8):
        """Helper method to create consistently styled labels"""
        return ttk.Label(
            self.ss.summary_frame,
            text=text,
            style='Body.TLabel',
            font=('Segoe UI', font_size)
        )