# app/src/automation/workflow_ui_components/confirmation_tab.py - COMPLETE FIXES

import tkinter as tk
from tkinter import ttk, simpledialog
from ..workflow_data_models import ConfirmationData, ValidationIssue

class ConfirmationTab:
    """Handles the confirmation tab content and logic with editable project name"""
    
    def __init__(self, parent, confirmation_data: ConfirmationData, theme):
        self.parent = parent
        self.data = confirmation_data
        self.theme = theme
        self.frame = None
        self.project_name_display = None
        self.output_location_display = None  # Add reference to output location display
        
    def create_tab(self):
        """Create confirmation tab content with editable project name"""
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
        """Add project information section with EDITABLE project name"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Project name with edit functionality
        project_frame = ttk.Frame(section_frame, style='White.TFrame')
        project_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(project_frame, text="Project:", style='Body.TLabel',
                 font=('Segoe UI', 10)).pack(side=tk.LEFT)
        
        # Project name display with hover effect
        self.project_name_display = tk.Label(project_frame, 
                                           text=self.data.project_name,
                                           font=('Segoe UI', 10, 'bold'),
                                           bg=self.theme.colors['bg'],
                                           cursor="hand2",
                                           relief='flat',
                                           borderwidth=1)
        self.project_name_display.pack(side=tk.LEFT, padx=(10, 5))
        
        # Edit icon (pen) that appears on hover
        self.edit_icon = tk.Label(project_frame, text="✏️", 
                                font=('Segoe UI', 10),
                                bg=self.theme.colors['bg'],
                                cursor="hand2")
        self.edit_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        # Initially hide the edit icon
        self.edit_icon.pack_forget()
        
        # Bind hover events
        self._setup_hover_events()
        
        # Other project details
        other_details = [
            ("Account:", self.data.account),
            ("Platform:", self.data.platform),
            # FIXED: Issue 3 - Add "Add" prefix to processing modes
            ("Mode Detected:", self._format_processing_mode(self.data.processing_mode))
        ]
        
        for label, value in other_details:
            row_frame = ttk.Frame(section_frame, style='White.TFrame')
            row_frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(row_frame, text=label, style='Body.TLabel',
                     font=('Segoe UI', 10)).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=value, style='Body.TLabel',
                     font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(10, 0))
    
    def _format_processing_mode(self, processing_mode):
        """FIXED: Issue 3 - Format processing mode with 'Add' prefix where appropriate"""
        mode_upper = processing_mode.replace('_', ' ').upper()
        
        if "SAVE" in mode_upper:
            return mode_upper  # No "Add" for save operations
        elif "QUIZ ONLY" in mode_upper:
            return "Add QUIZ ONLY"
        elif "CONNECTOR" in mode_upper and "QUIZ" in mode_upper:
            return "Add CONNECTORS AND QUIZ"
        elif "SVSL" in mode_upper:
            return "Add SVSL"
        else:
            return f"Add {mode_upper}"  # Default: add "Add" prefix
    
    def _setup_hover_events(self):
        """Setup hover events for project name editing"""
        
        def on_enter(event):
            """Show edit icon and highlight on hover"""
            self.project_name_display.config(relief='solid', borderwidth=1)
            self.edit_icon.pack(side=tk.LEFT, padx=(0, 5))
            
        def on_leave(event):
            """Hide edit icon and remove highlight"""
            self.project_name_display.config(relief='flat', borderwidth=0)
            self.edit_icon.pack_forget()
            
        def on_click(event):
            """Open edit dialog"""
            self._edit_project_name()
        
        # Bind events to both project name and edit icon
        for widget in [self.project_name_display, self.edit_icon]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave) 
            widget.bind("<Button-1>", on_click)
    
    def _edit_project_name(self):
        """Open dialog to edit project name - COMPLETELY FIXED"""
        
        # Create custom dialog
        dialog = tk.Toplevel(self.frame)
        dialog.title("Edit Project Name")
        dialog.geometry("450x180")
        dialog.resizable(False, False)
        dialog.configure(bg=self.theme.colors['bg'])
        
        # Center dialog
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Calculate center position
        x = self.frame.winfo_rootx() + 100
        y = self.frame.winfo_rooty() + 100
        dialog.geometry(f"450x180+{x}+{y}")
        
        # Dialog content
        main_frame = tk.Frame(dialog, bg=self.theme.colors['bg'], padx=25, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Edit Project Name:", 
                              font=('Segoe UI', 12, 'bold'),
                              bg=self.theme.colors['bg'], 
                              fg=self.theme.colors['text_primary'])
        title_label.pack(pady=(0, 15))
        
        # Entry field with current name
        name_var = tk.StringVar(value=self.data.project_name)
        name_entry = tk.Entry(main_frame, textvariable=name_var, width=50, 
                             font=('Segoe UI', 11), relief='solid', bd=1)
        name_entry.pack(fill=tk.X, pady=(0, 20))
        name_entry.focus_set()
        name_entry.select_range(0, tk.END)
        
        # COMPLETELY FIXED: Button frame with proper styling
        button_frame = tk.Frame(main_frame, bg=self.theme.colors['bg'])
        button_frame.pack(fill=tk.X)
        
        def save_changes():
            new_name = name_var.get().strip()
            if new_name and new_name != self.data.project_name:
                # Update the project name in data
                old_name = self.data.project_name
                self.data.project_name = new_name
                
                # FIXED: Update display immediately
                self.project_name_display.config(text=new_name)
                
                # FIXED: Update output location AND refresh display
                self._update_output_location_and_filenames(old_name, new_name)
                
                print(f"✅ Project name changed: '{old_name}' → '{new_name}'")
                print(f"✅ Updated output location: {self.data.output_location}")
            
            dialog.destroy()
        
        def cancel_changes():
            dialog.destroy()
        
        # COMPLETELY FIXED: Create buttons with proper Windows styling
        button_container = tk.Frame(button_frame, bg=self.theme.colors['bg'])
        button_container.pack()
        
        # Cancel button - proper styling
        cancel_btn = tk.Button(button_container, text="Cancel", 
                              font=('Segoe UI', 11), bg='#f3f3f3', fg='#323130',
                              relief='flat', borderwidth=1, padx=20, pady=8,
                              command=cancel_changes, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Approve button - proper accent styling  
        approve_btn = tk.Button(button_container, text="Approve", 
                               font=('Segoe UI', 11, 'bold'), bg='#0078d4', fg='white',
                               relief='flat', borderwidth=0, padx=20, pady=8,
                               command=save_changes, cursor='hand2')
        approve_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key to save
        name_entry.bind("<Return>", lambda e: save_changes())
        name_entry.bind("<Escape>", lambda e: cancel_changes())
    
    def _update_output_location_and_filenames(self, old_name, new_name):
        """FIXED: Update output location AND refresh the display"""
        # Update the output location string
        if old_name in self.data.output_location:
            self.data.output_location = self.data.output_location.replace(old_name, new_name)
            print(f"✅ Output location updated: {self.data.output_location}")
            
            # FIXED: Also update the display if it exists
            if hasattr(self, 'output_location_display') and self.output_location_display:
                self.output_location_display.config(text=f"📁 {self.data.output_location}")
                print(f"✅ Output location display refreshed")
        
        # The actual file naming happens during processing in naming_generator.py
        # The updated project name flows through the processing pipeline via confirmation data
    
    def get_updated_data(self):
        """Return the updated confirmation data with any changes"""
        return self.data
    
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
        """Add output information section - FIXED to store reference"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(section_frame, text="Output Location:", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        
        # FIXED: Store reference to output location display for updates
        self.output_location_display = ttk.Label(section_frame, text=f"📁 {self.data.output_location}", 
                                                style='Body.TLabel')
        self.output_location_display.pack(anchor=tk.W, padx=20, pady=(5, 10))
        
        ttk.Label(section_frame, text=f"Processing will complete automatically",
                 style='Body.TLabel', font=('Segoe UI', 9, 'italic')).pack(anchor=tk.W)