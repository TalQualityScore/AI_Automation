# app/src/automation/workflow_ui_components/confirmation_tab.py

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ValidationIssue:
    severity: str  # 'error', 'warning', 'info'
    message: str

@dataclass 
class ConfirmationData:
    """Data structure for confirmation display"""
    project_name: str
    account: str
    ad_type: str  # This attribute is required
    test_name: str
    client_videos: List[str]
    templates_to_add: List[str]
    output_location: str
    estimated_time: str
    issues: List[ValidationIssue]
    file_sizes: List[tuple]  # List of (filename, size_mb) tuples

class ConfirmationTab:
    """Handles the confirmation tab UI"""
    
    def __init__(self, parent, data: ConfirmationData, theme):
        self.parent = parent
        self.data = data
        self.theme = theme
        self.frame = None
        self.project_name_display = None
        self.edit_icon = None
        self.output_location_display = None
        
        # Add transition option variable
        self.use_transitions = tk.BooleanVar(value=True)
        self.transition_details_label = None
    
    def create_tab(self):
        """Create and return the confirmation tab"""
        self.frame = ttk.Frame(self.parent, style='White.TFrame')
        
        # Title
        title_frame = ttk.Frame(self.frame, style='White.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="📋 Review & Confirm", 
                 style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(title_frame, text="Please review the information below before processing", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
        
        # Create scrollable content area
        canvas = tk.Canvas(self.frame, bg=self.theme.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='White.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add content sections
        self._add_project_info(scrollable_frame)
        self._add_processing_details(scrollable_frame)
        self._add_processing_options(scrollable_frame)  # NEW SECTION
        self._add_issues_section(scrollable_frame)
        self._add_output_info(scrollable_frame)
        
        return self.frame
    
    def _add_project_info(self, parent):
        """Add project information section with editable project name"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Project name with edit functionality
        project_frame = ttk.Frame(section_frame, style='White.TFrame')
        project_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(project_frame, text="Project:", style='Body.TLabel',
                 font=('Segoe UI', 10)).pack(side=tk.LEFT)
        
        self.project_name_display = tk.Label(project_frame, 
                                           text=self.data.project_name,
                                           font=('Segoe UI', 10, 'bold'),
                                           bg=self.theme.colors['bg'],
                                           cursor="hand2",
                                           relief='flat',
                                           borderwidth=1)
        self.project_name_display.pack(side=tk.LEFT, padx=(10, 5))
        
        self.edit_icon = tk.Label(project_frame, text="✏️", 
                                font=('Segoe UI', 10),
                                bg=self.theme.colors['bg'],
                                cursor="hand2")
        self.edit_icon.pack(side=tk.LEFT, padx=(0, 5))
        self.edit_icon.pack_forget()
        
        self._setup_hover_events()
        
        # Other project details
        other_details = [
            ("Account:", self.data.account),
            ("Platform:", self.data.platform),
            ("Mode:", self.data.processing_mode)
        ]
        
        for label, value in other_details:
            detail_frame = ttk.Frame(section_frame, style='White.TFrame')
            detail_frame.pack(fill=tk.X, pady=3)
            ttk.Label(detail_frame, text=label, style='Body.TLabel',
                     font=('Segoe UI', 10)).pack(side=tk.LEFT)
            ttk.Label(detail_frame, text=value, style='Body.TLabel',
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
    
    def _add_processing_options(self, parent):
        """Add processing options section with transition toggle"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(section_frame, text="Processing Options:", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        # Transition checkbox container
        transition_frame = ttk.Frame(section_frame, style='White.TFrame')
        transition_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Checkbox for transitions
        transition_cb = ttk.Checkbutton(
            transition_frame,
            text="Add smooth transitions between videos",
            variable=self.use_transitions,
            command=self._update_transition_details
        )
        transition_cb.pack(side=tk.LEFT)
        
        # Warning text
        warning_label = ttk.Label(
            transition_frame, 
            text="(may increase processing time by ~30%)",
            style='Body.TLabel',
            font=('Segoe UI', 9, 'italic'),
            foreground='#666666'
        )
        warning_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Details about transitions (shown/hidden based on checkbox)
        self.transition_details_label = ttk.Label(
            section_frame,
            text="",
            style='Body.TLabel',
            font=('Segoe UI', 9),
            foreground=self.theme.colors['success']
        )
        self.transition_details_label.pack(anchor=tk.W, padx=40, pady=(5, 0))
        
        # Initialize the details display
        self._update_transition_details()
    
    def _update_transition_details(self):
        """Update the transition details text based on checkbox state"""
        if self.use_transitions.get():
            # Calculate number of transitions based on templates
            num_transitions = 0
            for template in self.data.templates_to_add:
                if "connector" in template.lower() and "quiz" in template.lower():
                    num_transitions = 2  # Client→Connector + Connector→Quiz
                elif "quiz" in template.lower():
                    num_transitions = 1  # Client→Quiz
            
            if num_transitions > 0:
                transition_text = f"✓ Will add {num_transitions} fade transition{'s' if num_transitions > 1 else ''} (0.25s each)"
                self.transition_details_label.config(text=transition_text)
            else:
                self.transition_details_label.config(text="")
        else:
            self.transition_details_label.config(text="✗ No transitions will be added")
    
    def _add_issues_section(self, parent):
        """Add issues section if there are any"""
        filtered_issues = []
        for issue in self.data.issues:
            if "large file" in issue.message.lower():
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
        
        self.output_location_display = ttk.Label(section_frame, text=f"📁 {self.data.output_location}", 
                                                style='Body.TLabel')
        self.output_location_display.pack(anchor=tk.W, padx=20, pady=(5, 10))
        
        ttk.Label(section_frame, text=f"Processing will complete automatically",
                 style='Body.TLabel', font=('Segoe UI', 9, 'italic')).pack(anchor=tk.W)
    
    def _setup_hover_events(self):
        """Setup hover events for project name editing"""
        def on_enter(event):
            self.project_name_display.config(relief='solid', bg='#f0f0f0')
            self.edit_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        def on_leave(event):
            self.project_name_display.config(relief='flat', bg=self.theme.colors['bg'])
            self.edit_icon.pack_forget()
        
        self.project_name_display.bind("<Enter>", on_enter)
        self.project_name_display.bind("<Leave>", on_leave)
        self.project_name_display.bind("<Button-1>", lambda e: self._show_edit_dialog())
        self.edit_icon.bind("<Button-1>", lambda e: self._show_edit_dialog())
    
    def _show_edit_dialog(self):
        """Show dialog to edit project name"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Project Name")
        dialog.geometry("400x180")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        tk.Label(main_frame, text="Edit Project Name:", font=('Segoe UI', 10, 'bold'),
                bg='white').pack(anchor=tk.W, pady=(0, 10))
        
        # Entry field
        name_entry = tk.Entry(main_frame, font=('Segoe UI', 10), width=40)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        name_entry.insert(0, self.data.project_name)
        name_entry.select_range(0, tk.END)
        name_entry.focus()
        
        # Button frame
        button_frame = tk.Frame(dialog, bg='white', padx=20, pady=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        def save_changes():
            new_name = name_entry.get().strip()
            if new_name and new_name != self.data.project_name:
                old_name = self.data.project_name
                self.data.project_name = new_name
                self.project_name_display.config(text=new_name)
                self._update_output_location_and_display(old_name, new_name)
            dialog.destroy()
        
        def cancel_changes():
            dialog.destroy()
        
        # Buttons
        button_container = tk.Frame(button_frame, bg='white')
        button_container.pack()
        
        cancel_btn = tk.Button(button_container, text="Cancel", 
                              font=('Segoe UI', 10), bg='#f3f3f3', fg='#323130',
                              relief='flat', borderwidth=1, padx=20, pady=8,
                              command=cancel_changes, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        approve_btn = tk.Button(button_container, text="✅ Apply Changes", 
                               font=('Segoe UI', 10, 'bold'), bg='#0078d4', fg='white',
                               relief='flat', borderwidth=0, padx=25, pady=8,
                               command=save_changes, cursor='hand2')
        approve_btn.pack(side=tk.RIGHT)
        
        # Bind keys
        name_entry.bind("<Return>", lambda e: save_changes())
        name_entry.bind("<Escape>", lambda e: cancel_changes())
    
    def _update_output_location_and_display(self, old_name, new_name):
        """Update output location in data AND refresh display"""
        if old_name in self.data.output_location:
            self.data.output_location = self.data.output_location.replace(old_name, new_name)
            if self.output_location_display:
                self.output_location_display.config(text=f"📁 {self.data.output_location}")
    
    def get_updated_data(self):
        """Return the updated confirmation data"""
        return self.data
    
    def get_transition_setting(self):
        """Return the transition toggle setting"""
        return self.use_transitions.get()