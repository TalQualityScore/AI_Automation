# app/src/automation/workflow_ui_components/results_tab.py
import tkinter as tk
from tkinter import ttk
from ..workflow_data_models import ProcessingResult

class ResultsTab:
    """Handles the results tab content and logic"""
    
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.frame = None
        self.results_content = None
        # Breakdown-related attributes
        self.breakdown_expanded = None
        self.breakdown_btn = None
        self.breakdown_content = None
        self.breakdown_data = None
        
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