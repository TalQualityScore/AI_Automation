# app/src/automation/workflow_ui_components.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import platform
from .workflow_data_models import ConfirmationData, ValidationIssue, ProcessingResult

class WorkflowTheme:
    """Handles UI theming and styling"""
    
    def __init__(self, root):
        self.root = root
        self.colors = {
            'bg': '#ffffff',
            'accent': '#0078d4',
            'success': '#107c10',
            'warning': '#ff8c00',
            'error': '#d13438',
            'text_primary': '#323130',
            'text_secondary': '#605e5c',
            'border': '#e1dfdd',
            'tab_active': '#ffffff',
            'tab_inactive': '#f8f8f8'
        }
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply pure white Windows 11 theme"""
        self.root.configure(bg=self.colors['bg'])
        
        style = ttk.Style()
        style.configure('White.TFrame', background=self.colors['bg'])
        style.configure('Header.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 18, 'bold'))
        style.configure('Subheader.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 11))
        style.configure('Body.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        style.configure('Accent.TButton', font=('Segoe UI', 11, 'bold'),
                       padding=(25, 12))
        style.configure('Secondary.TButton', font=('Segoe UI', 11),
                       padding=(25, 12))

class ConfirmationTab:
    """Handles the confirmation tab content and logic"""
    
    def __init__(self, parent, confirmation_data: ConfirmationData, theme: WorkflowTheme):
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

class ProcessingTab:
    """Handles the processing tab content and logic"""
    
    def __init__(self, parent, theme: WorkflowTheme):
        self.parent = parent
        self.theme = theme
        self.frame = None
        self.progress_var = None
        self.progress_label = None
        self.step_label = None
        self.time_label = None
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
        
        # Progress labels
        self.progress_label = ttk.Label(progress_frame, text="Initializing...",
                                       style='Body.TLabel', font=('Segoe UI', 11, 'bold'))
        self.progress_label.pack(pady=(0, 8))
        
        self.step_label = ttk.Label(progress_frame, text="Starting validation process...",
                                   style='Body.TLabel', font=('Segoe UI', 10))
        self.step_label.pack(pady=(0, 8))
        
        self.time_label = ttk.Label(progress_frame, text=f"Estimated duration: {estimated_time}",
                                   style='Body.TLabel', font=('Segoe UI', 9, 'italic'),
                                   foreground=self.theme.colors['text_secondary'])
        self.time_label.pack()
        
        return self.frame
    
    def update_progress(self, progress: float, step_text: str = "", elapsed_time: float = 0):
        """Update progress bar and labels"""
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{int(progress)}%")
        
        if step_text:
            self.step_label.config(text=step_text)
        
        # Calculate time remaining
        if progress > 5 and elapsed_time > 0:
            estimated_total = (elapsed_time / progress) * 100
            remaining = max(0, estimated_total - elapsed_time)
            
            if remaining > 60:
                remaining_str = f"{int(remaining // 60)}m {int(remaining % 60)}s"
            else:
                remaining_str = f"{int(remaining)}s"
                
            self.time_label.config(text=f"Estimated time remaining: {remaining_str}")

class ResultsTab:
    """Handles the results tab content and logic"""
    
    def __init__(self, parent, theme: WorkflowTheme):
        self.parent = parent
        self.theme = theme
        self.frame = None
        self.results_content = None
        
    def create_tab(self):
        """Create results tab content"""
        self.frame = ttk.Frame(self.parent, style='White.TFrame')
        
        # Results content will be populated when processing completes
        self.results_content = ttk.Frame(self.frame, style='White.TFrame')
        self.results_content.pack(fill=tk.BOTH, expand=True)
        
        return self.frame
    
def show_success_results(self, result: ProcessingResult, on_open_folder, on_done):
    """Show success results with fixed button accessibility"""
    # Clear existing content
    for widget in self.results_content.winfo_children():
        widget.destroy()
    
    # Create main container with proper layout
    main_container = ttk.Frame(self.results_content, style='White.TFrame')
    main_container.pack(fill=tk.BOTH, expand=True)
    
    # Scrollable content area (reduced height to leave room for buttons)
    content_canvas = tk.Canvas(main_container, bg=self.theme.colors['bg'], 
                              highlightthickness=0, height=500)  # Fixed height
    content_scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=content_canvas.yview)
    scrollable_content = ttk.Frame(content_canvas, style='White.TFrame')
    
    scrollable_content.bind("<Configure>", 
                           lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all")))
    
    content_canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
    content_canvas.configure(yscrollcommand=content_scrollbar.set)
    
    content_canvas.pack(side="left", fill="both", expand=True)
    content_scrollbar.pack(side="right", fill="y")
    
    # Mouse wheel scrolling
    def _on_results_mousewheel(event):
        content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    content_canvas.bind_all("<MouseWheel>", _on_results_mousewheel)
    
    # Header inside scrollable area
    header_frame = ttk.Frame(scrollable_content, style='White.TFrame')
    header_frame.pack(fill=tk.X, pady=(20, 30))
    
    title_container = ttk.Frame(header_frame, style='White.TFrame')
    title_container.pack()
    
    icon_label = ttk.Label(title_container, text="🎉", font=('Segoe UI', 28),
                          style='Body.TLabel')
    icon_label.pack(side=tk.LEFT, padx=(0, 15))
    
    text_frame = ttk.Frame(title_container, style='White.TFrame')
    text_frame.pack(side=tk.LEFT)
    
    ttk.Label(text_frame, text="Success!", style='Header.TLabel').pack(anchor=tk.W)
    ttk.Label(text_frame, text="Your videos have been processed successfully", 
             style='Subheader.TLabel').pack(anchor=tk.W)
    
    # Summary inside scrollable area
    summary_frame = ttk.Frame(scrollable_content, style='White.TFrame')
    summary_frame.pack(fill=tk.X, pady=(0, 20))
    
    ttk.Label(summary_frame, text=f"✅ Processing completed in {result.duration}",
             style='Body.TLabel', font=('Segoe UI', 12, 'bold'),
             foreground=self.theme.colors['success']).pack(anchor=tk.W)
    
    if result.processed_files:
        count = len(result.processed_files)
        ttk.Label(summary_frame, text=f"📊 {count} video{'s' if count != 1 else ''} processed successfully",
                 style='Body.TLabel', font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(5, 0))
    
    # Breakdown section inside scrollable area
    if result.processed_files:
        self._add_breakdown_section(scrollable_content, result.processed_files)
    
    # Output location inside scrollable area
    output_frame = ttk.Frame(scrollable_content, style='White.TFrame')
    output_frame.pack(fill=tk.X, pady=(0, 30))
    
    ttk.Label(output_frame, text="📂 Output Location:", style='Body.TLabel',
             font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)
    
    path_frame = ttk.Frame(output_frame, style='White.TFrame')
    path_frame.pack(fill=tk.X, padx=20, pady=(5, 0))
    
    path_label = ttk.Label(path_frame, text=result.output_folder, style='Body.TLabel',
                          font=('Segoe UI', 9), foreground=self.theme.colors['accent'],
                          cursor="hand2")
    path_label.pack(anchor=tk.W)
    path_label.bind("<Button-1>", lambda e: on_open_folder(result.output_folder))
    
    # FIXED: Action buttons OUTSIDE scrollable area - always visible
    button_frame = ttk.Frame(main_container, style='White.TFrame')
    button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20, padx=40)
    
    button_container = ttk.Frame(button_frame, style='White.TFrame')
    button_container.pack()
    
    ttk.Button(button_container, text="📂 Open Output Folder", 
              style='Accent.TButton',
              command=lambda: on_open_folder(result.output_folder)).pack(side=tk.LEFT, padx=(0, 15))
    
    ttk.Button(button_container, text="✅ Done", style='Secondary.TButton',
              command=on_done).pack(side=tk.LEFT)
    
    def _add_breakdown_section(self, parent, processed_files):
        """Add expandable breakdown section"""
        breakdown_frame = ttk.Frame(parent, style='White.TFrame')
        breakdown_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Breakdown header with expand/collapse button
        header_frame = ttk.Frame(breakdown_frame, style='White.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.breakdown_expanded = tk.BooleanVar(value=False)
        self.breakdown_btn = ttk.Button(header_frame, text="📋 Show Breakdown", 
                                       style='Secondary.TButton',
                                       command=self._toggle_breakdown)
        self.breakdown_btn.pack(side=tk.LEFT)
        
        # Breakdown content (initially hidden)
        self.breakdown_content = ttk.Frame(breakdown_frame, style='White.TFrame')
        
        # Store data for breakdown
        self.breakdown_data = processed_files
        
    def _toggle_breakdown(self):
        """Toggle breakdown section visibility"""
        if self.breakdown_expanded.get():
            # Hide breakdown
            self.breakdown_content.pack_forget()
            self.breakdown_btn.config(text="📋 Show Breakdown")
            self.breakdown_expanded.set(False)
        else:
            # Show breakdown
            self._populate_breakdown()
            self.breakdown_content.pack(fill=tk.X, pady=(10, 0))
            self.breakdown_btn.config(text="📋 Hide Breakdown")
            self.breakdown_expanded.set(True)

    def show_success_results(self, processing_result):
        """Display final OK message + summary (called by dialog)""" 
        self._render_summary(processing_result) # reuse existing helper
    
def _populate_breakdown(self):
    """Populate the breakdown content with scrollable container"""
    # Clear existing content
    for widget in self.breakdown_content.winfo_children():
        widget.destroy()
    
    # Create scrollable container for breakdown
    breakdown_canvas = tk.Canvas(self.breakdown_content, bg=self.theme.colors['bg'], 
                                highlightthickness=0, height=300)  # Fixed height
    breakdown_scrollbar = ttk.Scrollbar(self.breakdown_content, orient="vertical", 
                                       command=breakdown_canvas.yview)
    breakdown_scrollable = ttk.Frame(breakdown_canvas, style='White.TFrame')
    
    breakdown_scrollable.bind("<Configure>", 
                             lambda e: breakdown_canvas.configure(scrollregion=breakdown_canvas.bbox("all")))
    
    breakdown_canvas.create_window((0, 0), window=breakdown_scrollable, anchor="nw")
    breakdown_canvas.configure(yscrollcommand=breakdown_scrollbar.set)
    
    breakdown_canvas.pack(side="left", fill="both", expand=True)
    breakdown_scrollbar.pack(side="right", fill="y")
    
    # Mouse wheel scrolling for breakdown
    def _on_breakdown_mousewheel(event):
        breakdown_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    breakdown_canvas.bind_all("<MouseWheel>", _on_breakdown_mousewheel)
    
    # Title
    ttk.Label(breakdown_scrollable, text="🔍 Detailed Breakdown:", 
             style='Body.TLabel', font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 10))
    
    total_duration = 0
    
    for i, file_info in enumerate(self.breakdown_data, 1):
        # File container
        file_frame = ttk.Frame(breakdown_scrollable, style='White.TFrame')
        file_frame.pack(fill=tk.X, pady=5, padx=20)
        
        # Add border
        file_frame.configure(relief='solid', borderwidth=1)
        
        inner_frame = ttk.Frame(file_frame, style='White.TFrame', padding=10)
        inner_frame.pack(fill=tk.X)
        
        # File header
        ttk.Label(inner_frame, text=f"Video {i}: {file_info.get('output_name', 'Unknown')}.mp4",
                 style='Body.TLabel', font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        
        # File details
        details_frame = ttk.Frame(inner_frame, style='White.TFrame')
        details_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Source file
        ttk.Label(details_frame, text=f"📹 Source: {file_info.get('source_file', 'Unknown')}",
                 style='Body.TLabel', font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        # Description/Processing info
        ttk.Label(details_frame, text=f"🔧 Processing: {file_info.get('description', 'Unknown')}",
                 style='Body.TLabel', font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        # Mock duration data (in real implementation, this would come from actual video analysis)
        mock_duration = 125 + (i * 15)  # Mock duration in seconds
        minutes = mock_duration // 60
        seconds = mock_duration % 60
        duration_str = f"{minutes}:{seconds:02d}"
        
        ttk.Label(details_frame, text=f"⏱️ Duration: {duration_str} ({mock_duration}s)",
                 style='Body.TLabel', font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        # Video composition (mock data)
        composition_parts = []
        if "connector" in file_info.get('description', '').lower():
            composition_parts = ["Client Video (90s)", "Blake Connector (20s)", "Quiz Outro (15s)"]
        elif "quiz" in file_info.get('description', '').lower():
            composition_parts = ["Client Video (90s)", "Quiz Outro (15s)"]
        else:
            composition_parts = ["Client Video (90s)"]
        
        if composition_parts:
            ttk.Label(details_frame, text=f"🧩 Components: {' → '.join(composition_parts)}",
                     style='Body.TLabel', font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        total_duration += mock_duration
    
    # Total summary
    if len(self.breakdown_data) > 1:
        summary_frame = ttk.Frame(breakdown_scrollable, style='White.TFrame')
        summary_frame.pack(fill=tk.X, pady=(15, 0), padx=20)
        
        summary_frame.configure(relief='solid', borderwidth=2)
        
        inner_summary = ttk.Frame(summary_frame, style='White.TFrame', padding=10)
        inner_summary.pack(fill=tk.X)
        
        total_minutes = total_duration // 60
        total_seconds = total_duration % 60
        total_duration_str = f"{total_minutes}:{total_seconds:02d}"
        
        ttk.Label(inner_summary, text="📊 Summary",
                 style='Body.TLabel', font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        ttk.Label(inner_summary, text=f"📈 Total Content: {total_duration_str} ({total_duration}s)",
                 style='Body.TLabel', font=('Segoe UI', 10),
                 foreground=self.theme.colors['accent']).pack(anchor=tk.W)
        ttk.Label(inner_summary, text=f"📼 Files Created: {len(self.breakdown_data)} videos",
                 style='Body.TLabel', font=('Segoe UI', 10)).pack(anchor=tk.W)
    
    def show_error_results(self, result: ProcessingResult, on_copy_error, on_close):
        """Show error results"""
        # Clear existing content
        for widget in self.results_content.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = ttk.Frame(self.results_content, style='White.TFrame')
        header_frame.pack(fill=tk.X, pady=(20, 30))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack()
        
        icon_label = ttk.Label(title_container, text="❌", font=('Segoe UI', 28),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT)
        
        ttk.Label(text_frame, text="Processing Error", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="An error occurred during processing", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
        
        # Error details
        error_container = ttk.Frame(self.results_content, style='White.TFrame')
        error_container.pack(fill=tk.BOTH, expand=True, pady=20)
        
        ttk.Label(error_container, text="Error Details:", style='Body.TLabel',
                 font=('Segoe UI', 12, 'bold'),
                 foreground=self.theme.colors['error']).pack(anchor=tk.W, pady=(0, 10))
        
        # Error text box
        error_frame = ttk.Frame(error_container, style='White.TFrame')
        error_frame.pack(fill=tk.X, pady=(0, 20))
        
        error_text = tk.Text(error_frame, height=6, wrap=tk.WORD, 
                            font=('Consolas', 9), bg='#fef9f9', 
                            borderwidth=1, relief='solid')
        scrollbar_error = ttk.Scrollbar(error_frame, orient="vertical", command=error_text.yview)
        error_text.configure(yscrollcommand=scrollbar_error.set)
        
        error_text.pack(side="left", fill="both", expand=True)
        scrollbar_error.pack(side="right", fill="y")
        
        error_text.insert('1.0', result.error_message)
        error_text.configure(state='disabled')
        
        # Solution section
        if result.error_solution:
            ttk.Label(error_container, text="💡 Suggested Solution:", style='Body.TLabel',
                     font=('Segoe UI', 12, 'bold'),
                     foreground=self.theme.colors['accent']).pack(anchor=tk.W, pady=(0, 10))
            
            solution_frame = ttk.Frame(error_container, style='White.TFrame')
            solution_frame.pack(fill=tk.X, pady=(0, 20))
            
            solution_text = tk.Text(solution_frame, height=4, wrap=tk.WORD,
                                   font=('Segoe UI', 9), bg='#f0f8ff',
                                   borderwidth=1, relief='solid')
            scrollbar_solution = ttk.Scrollbar(solution_frame, orient="vertical", command=solution_text.yview)
            solution_text.configure(yscrollcommand=scrollbar_solution.set)
            
            solution_text.pack(side="left", fill="both", expand=True)
            scrollbar_solution.pack(side="right", fill="y")
            
            solution_text.insert('1.0', result.error_solution)
            solution_text.configure(state='disabled')
        
        # Error action buttons
        button_frame = ttk.Frame(self.results_content, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=30)
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        ttk.Button(button_container, text="📋 Copy Error Details", 
                  style='Secondary.TButton',
                  command=lambda: on_copy_error(result.error_message)).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(button_container, text="❌ Close", style='Secondary.TButton',
                  command=on_close).pack(side=tk.LEFT)

class NotificationPopup:
    """Handles notification settings popup"""
    
    def __init__(self, parent, current_settings, theme: WorkflowTheme):
        self.parent = parent
        self.current_settings = current_settings
        self.theme = theme
        self.popup = None
        self.email_var = None
        self.slack_var = None
        self.email_entry = None
        self.slack_entry = None
    
    def show_popup(self):
        """Show notification settings popup"""
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Notification Settings")
        self.popup.geometry("400x250")
        self.popup.resizable(False, False)
        self.popup.configure(bg=self.theme.colors['bg'])
        
        # Center popup
        self.popup.transient(self.parent)
        self.popup.grab_set()
        
        x = self.parent.winfo_x() + 100
        y = self.parent.winfo_y() + 100
        self.popup.geometry(f"400x250+{x}+{y}")
        
        main_frame = ttk.Frame(self.popup, style='White.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="📧 Notification Settings", style='Body.TLabel',
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Email notification
        email_frame = ttk.Frame(main_frame, style='White.TFrame')
        email_frame.pack(fill=tk.X, pady=10)
        
        self.email_var = tk.BooleanVar(value=self.current_settings['email']['enabled'])
        email_check = ttk.Checkbutton(email_frame, text="Email notification", 
                                     variable=self.email_var)
        email_check.pack(anchor=tk.W)
        
        self.email_entry = ttk.Entry(email_frame, width=35)
        self.email_entry.pack(fill=tk.X, pady=(5, 0))
        self.email_entry.insert(0, self.current_settings['email']['address'] or "your.email@domain.com")
        
        # Slack notification  
        slack_frame = ttk.Frame(main_frame, style='White.TFrame')
        slack_frame.pack(fill=tk.X, pady=10)
        
        self.slack_var = tk.BooleanVar(value=self.current_settings['slack']['enabled'])
        slack_check = ttk.Checkbutton(slack_frame, text="Slack notification",
                                     variable=self.slack_var)
        slack_check.pack(anchor=tk.W)
        
        self.slack_entry = ttk.Entry(slack_frame, width=35)
        self.slack_entry.pack(fill=tk.X, pady=(5, 0))
        self.slack_entry.insert(0, self.current_settings['slack']['webhook'] or "slack-webhook-url")
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.popup.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save", command=self._save_settings).pack(side=tk.RIGHT)
    
    def _save_settings(self):
        """Save notification settings and close popup"""
        self.current_settings['email']['enabled'] = self.email_var.get()
        self.current_settings['email']['address'] = self.email_entry.get()
        self.current_settings['slack']['enabled'] = self.slack_var.get()  
        self.current_settings['slack']['webhook'] = self.slack_entry.get()
        self.popup.destroy()

def open_folder(folder_path: str):
    """Open output folder in file explorer"""
    try:
        if platform.system() == "Windows":
            os.startfile(folder_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", folder_path])
        else:  # Linux
            subprocess.run(["xdg-open", folder_path])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open folder:\n{e}")

def copy_to_clipboard(root, text: str):
    """Copy text to clipboard"""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        messagebox.showinfo("Copied", "Error details copied to clipboard!")
    except Exception as e:
        messagebox.showerror("Error", f"Could not copy to clipboard:\n{e}")

def generate_error_solution(error_message: str) -> str:
    """Generate helpful error solutions based on error message content"""
    error_lower = error_message.lower()
    
    if "google drive" in error_lower and "404" in error_lower:
        return """1. Check if the Google Drive folder link is correct and accessible
2. Verify the folder is shared with your service account email  
3. Ensure the folder contains video files (.mp4 or .mov)
4. Try opening the Google Drive link in your browser to confirm access"""
    
    elif "google drive" in error_lower and "403" in error_lower:
        return """1. Check if your service account has permission to access the folder
2. Re-share the Google Drive folder with your service account email
3. Verify the service account credentials are correct
4. Make sure the folder is not restricted by organization policies"""
    
    elif "trello" in error_lower:
        return """1. Verify your Trello API key and token are correct
2. Check if the Trello card ID exists and is accessible
3. Ensure the Trello card has a proper description with Google Drive link
4. Try refreshing your Trello API credentials"""
    
    elif "ffmpeg" in error_lower:
        return """1. Ensure FFmpeg is installed and available in your system PATH
2. Check if input video files are not corrupted
3. Verify you have enough disk space for processing
4. Try processing with smaller video files first"""
    
    elif "timeout" in error_lower or "stuck" in error_lower:
        return """1. Check your internet connection stability
2. Try with smaller video files to test connectivity
3. Ensure Google Drive links are accessible
4. Restart the application and try again"""
    
    elif "permission" in error_lower or "access" in error_lower:
        return """1. Run the application as administrator if needed
2. Check file and folder permissions
3. Ensure output directory is writable
4. Verify service account credentials have proper access"""
    
    else:
        return """1. Check your internet connection
2. Verify all API credentials are correct
3. Ensure input files and links are accessible
4. Try restarting the application
5. Check the error log for more details"""