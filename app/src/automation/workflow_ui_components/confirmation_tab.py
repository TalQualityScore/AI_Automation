# app/src/automation/workflow_ui_components/confirmation_tab.py
import tkinter as tk
from tkinter import ttk
from ..workflow_data_models import ConfirmationData, ValidationIssue

class ConfirmationTab:
    """Handles the confirmation tab content and logic"""
    
    def __init__(self, parent, confirmation_data: ConfirmationData, theme):
        self.parent = parent
        self.data = confirmation_data
        self.theme = theme
        self.frame = None
        
    def create_tab(self):
        """Create confirmation tab content"""
        self.frame = ttk.Frame(self.parent, style='White.TFrame')
        
        # Scrollable content with reduced height to leave room for buttons
        canvas = tk.Canvas(self.frame, bg=self.theme.colors['bg'], highlightthickness=0, height=400)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='White.TFrame')
        
        scrollable_frame.bind("<Configure>", 
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add content sections
        self._add_project_info(scrollable_frame)
        self._add_processing_details(scrollable_frame)
        self._add_issues_section(scrollable_frame)
        self._add_output_info(scrollable_frame)
        
        return self.frame
    
    def _add_project_info(self, parent):
        """Add project information section"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        details = [
            ("Project:", self.data.project_name),
            ("Account:", self.data.account),
            ("Platform:", self.data.platform),
            ("Mode Detected:", self.data.processing_mode.replace('_', ' ').upper())
        ]
        
        for label, value in details:
            row_frame = ttk.Frame(section_frame, style='White.TFrame')
            row_frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(row_frame, text=label, style='Body.TLabel',
                     font=('Segoe UI', 10)).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=value, style='Body.TLabel',
                     font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(10, 0))
    
    def _add_processing_details(self, parent):
        """Add processing details section"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(section_frame, text="Will Process:", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        if self.data.client_videos:
            ttk.Label(section_frame, 
                     text=f"✓ {len(self.data.client_videos)} client video(s) from Google Drive",
                     style='Body.TLabel', foreground=self.theme.colors['success']).pack(anchor=tk.W, padx=20)
        
        for template in self.data.templates_to_add:
            ttk.Label(section_frame, text=f"✓ {template}", style='Body.TLabel',
                     foreground=self.theme.colors['success']).pack(anchor=tk.W, padx=20)
    
    def _add_issues_section(self, parent):
        """Add issues section if there are any"""
        # Filter large file warnings (only show for files > 1GB)
        filtered_issues = []
        for issue in self.data.issues:
            if "large file" in issue.message.lower():
                # Check if any file is actually > 1GB (1000MB)
                for filename, size_mb in self.data.file_sizes:
                    if size_mb > 1000:
                        filtered_issues.append(ValidationIssue("warning", 
                            f"Large file detected: {filename} ({size_mb}MB)"))
                        break
            else:
                filtered_issues.append(issue)
        
        if not filtered_issues:
            return
            
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(section_frame, text="⚠️ Issues Found:", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold'), 
                 foreground=self.theme.colors['warning']).pack(anchor=tk.W, pady=(0, 8))
        
        for issue in filtered_issues:
            color = self.theme.colors.get(issue.severity, self.theme.colors['text_primary'])
            ttk.Label(section_frame, text=f"• {issue.message}", style='Body.TLabel',
                     foreground=color).pack(anchor=tk.W, padx=20)
    
    def _add_output_info(self, parent):
        """Add output information section"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(section_frame, text="Output Location:", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        ttk.Label(section_frame, text=f"📁 {self.data.output_location}", 
                 style='Body.TLabel').pack(anchor=tk.W, padx=20, pady=(5, 10))
        
        ttk.Label(section_frame, text=f"Processing Time Estimate: {self.data.estimated_time}",
                 style='Body.TLabel', font=('Segoe UI', 9, 'italic')).pack(anchor=tk.W)