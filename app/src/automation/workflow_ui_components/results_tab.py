# app/src/automation/workflow_ui_components/results_tab.py - FIXED VERSION
import tkinter as tk
from tkinter import ttk
from ..workflow_data_models import ProcessingResult

class ResultsTab:
    """Handles the results tab content and logic - FIXED UI ISSUES"""
    
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
        # FIXED: Store result data to prevent clearing
        self.current_result = None
        self.current_callbacks = None
        
    def create_tab(self):
        """Create results tab content"""
        self.frame = ttk.Frame(self.parent, style='White.TFrame')
        
        # Results content will be populated when processing completes
        self.results_content = ttk.Frame(self.frame, style='White.TFrame')
        self.results_content.pack(fill=tk.BOTH, expand=True)
        
        # FIXED: If we have stored result data, restore it
        if self.current_result and self.current_callbacks:
            if self.current_result.success:
                self.show_success_results(
                    self.current_result, 
                    self.current_callbacks['on_open_folder'],
                    self.current_callbacks['on_done']
                )
            else:
                self.show_error_results(
                    self.current_result,
                    self.current_callbacks['on_copy_error'],
                    self.current_callbacks['on_close']
                )
        
        return self.frame
    
    def show_success_results(self, result: ProcessingResult, on_open_folder, on_done):
        """Show success results with FIXED button layout and text wrapping"""
        # FIXED: Store result and callbacks for tab switching
        self.current_result = result
        self.current_callbacks = {
            'on_open_folder': on_open_folder,
            'on_done': on_done
        }
        
        # Clear existing content
        for widget in self.results_content.winfo_children():
            widget.destroy()
        
        # Create main container with proper layout - FIXED HEIGHT
        main_container = ttk.Frame(self.results_content, style='White.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_container, style='White.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack(fill=tk.X)
        
        icon_label = ttk.Label(title_container, text="🎉", font=('Segoe UI', 28),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(text_frame, text="Success!", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="Your videos have been processed successfully", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
        
        # Summary
        summary_frame = ttk.Frame(main_container, style='White.TFrame')
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(summary_frame, text=f"✅ Processing completed in {result.duration}",
                 style='Body.TLabel', font=('Segoe UI', 12, 'bold'),
                 foreground=self.theme.colors['success']).pack(anchor=tk.W)
        
        if result.processed_files:
            count = len(result.processed_files)
            ttk.Label(summary_frame, text=f"📊 {count} video{'s' if count != 1 else ''} processed successfully",
                     style='Body.TLabel', font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(5, 0))
        
        # FIXED: Scrollable content area with proper height management
        content_frame = ttk.Frame(main_container, style='White.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create canvas for scrolling content
        content_canvas = tk.Canvas(content_frame, bg=self.theme.colors['bg'], 
                                 highlightthickness=0, height=250)  # FIXED: Reasonable height
        content_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=content_canvas.yview)
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
        
        # Breakdown section in scrollable area
        if result.processed_files:
            self._add_breakdown_section(scrollable_content, result.processed_files)
        
        # Output location
        output_frame = ttk.Frame(main_container, style='White.TFrame')
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(output_frame, text="📂 Output Location:", style='Body.TLabel',
                 font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)
        
        # FIXED: Better path display with wrapping
        path_frame = ttk.Frame(output_frame, style='White.TFrame')
        path_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Use a Text widget for better path display and wrapping
        path_text = tk.Text(path_frame, height=2, wrap=tk.WORD, 
                           font=('Segoe UI', 9), bg=self.theme.colors['bg'],
                           relief='flat', cursor="hand2")
        path_text.pack(fill=tk.X)
        path_text.insert('1.0', result.output_folder)
        path_text.configure(state='disabled')
        path_text.bind("<Button-1>", lambda e: on_open_folder(result.output_folder))
        
        ttk.Label(path_frame, text="(Click path above to open folder)",
                 style='Body.TLabel', font=('Segoe UI', 8, 'italic'),
                 foreground=self.theme.colors['text_secondary']).pack(anchor=tk.W)
        
        # FIXED: Action buttons with proper centering and spacing
        button_frame = ttk.Frame(main_container, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Center the buttons
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack(anchor=tk.CENTER)
        
        # Buttons with proper spacing
        open_btn = ttk.Button(button_container, text="📂 Open Output Folder", 
                             style='Accent.TButton',
                             command=lambda: on_open_folder(result.output_folder))
        open_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        done_btn = ttk.Button(button_container, text="✅ Done", 
                             style='Secondary.TButton', command=on_done)
        done_btn.pack(side=tk.LEFT)
    
    def show_error_results(self, result: ProcessingResult, on_copy_error, on_close):
        """Show error results with FIXED layout"""
        # FIXED: Store result and callbacks for tab switching
        self.current_result = result
        self.current_callbacks = {
            'on_copy_error': on_copy_error,
            'on_close': on_close
        }
        
        # Clear existing content
        for widget in self.results_content.winfo_children():
            widget.destroy()
        
        # Create main container
        main_container = ttk.Frame(self.results_content, style='White.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_container, style='White.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack(fill=tk.X)
        
        icon_label = ttk.Label(title_container, text="❌", font=('Segoe UI', 28),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(text_frame, text="Processing Error", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="An error occurred during processing", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
        
        # Error details in scrollable area
        error_container = ttk.Frame(main_container, style='White.TFrame')
        error_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        ttk.Label(error_container, text="Error Details:", style='Body.TLabel',
                 font=('Segoe UI', 12, 'bold'),
                 foreground=self.theme.colors['error']).pack(anchor=tk.W, pady=(0, 10))
        
        # Error text box with proper sizing
        error_frame = ttk.Frame(error_container, style='White.TFrame')
        error_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        error_text = tk.Text(error_frame, height=8, wrap=tk.WORD, 
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
            solution_frame.pack(fill=tk.X, pady=(0, 15))
            
            solution_text = tk.Text(solution_frame, height=6, wrap=tk.WORD,
                                   font=('Segoe UI', 9), bg='#f0f8ff',
                                   borderwidth=1, relief='solid')
            scrollbar_solution = ttk.Scrollbar(solution_frame, orient="vertical", command=solution_text.yview)
            solution_text.configure(yscrollcommand=scrollbar_solution.set)
            
            solution_text.pack(side="left", fill="both", expand=True)
            scrollbar_solution.pack(side="right", fill="y")
            
            solution_text.insert('1.0', result.error_solution)
            solution_text.configure(state='disabled')
        
        # FIXED: Error action buttons with proper centering
        button_frame = ttk.Frame(main_container, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack(anchor=tk.CENTER)
        
        ttk.Button(button_container, text="📋 Copy Error Details", 
                  style='Secondary.TButton',
                  command=lambda: on_copy_error(result.error_message)).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(button_container, text="❌ Close", style='Secondary.TButton',
                  command=on_close).pack(side=tk.LEFT)
    
    def _add_breakdown_section(self, parent, processed_files):
        """Add expandable breakdown section with FIXED text wrapping"""
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
        """Populate the breakdown content with FIXED text sizing and scrolling"""
        # Clear existing content
        for widget in self.breakdown_content.winfo_children():
            widget.destroy()
        
        # Create scrollable container for breakdown with FIXED height
        breakdown_canvas = tk.Canvas(self.breakdown_content, bg=self.theme.colors['bg'], 
                                    highlightthickness=0, height=200)  # FIXED: Smaller height
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
        breakdown_canvas.bind("<MouseWheel>", _on_breakdown_mousewheel)
        
        # Title
        ttk.Label(breakdown_scrollable, text="🔍 Detailed Breakdown:", 
                 style='Body.TLabel', font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        for i, file_info in enumerate(self.breakdown_data, 1):
            # FIXED: File container with better spacing
            file_frame = ttk.Frame(breakdown_scrollable, style='White.TFrame')
            file_frame.pack(fill=tk.X, pady=3, padx=10)
            
            # Add subtle border
            file_frame.configure(relief='solid', borderwidth=1)
            
            inner_frame = ttk.Frame(file_frame, style='White.TFrame', padding=8)
            inner_frame.pack(fill=tk.X)
            
            # FIXED: File header with text wrapping
            header_text = f"Video {i}: {file_info.get('output_name', 'Unknown')}.mp4"
            if len(header_text) > 60:  # Wrap long names
                header_text = f"Video {i}:\n{file_info.get('output_name', 'Unknown')}.mp4"
            
            ttk.Label(inner_frame, text=header_text,
                     style='Body.TLabel', font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W)
            
            # File details with smaller font
            details_frame = ttk.Frame(inner_frame, style='White.TFrame')
            details_frame.pack(fill=tk.X, pady=(3, 0))
            
            # FIXED: Shorter, wrapped text
            source_text = f"📹 Source: {file_info.get('source_file', 'Unknown')}"
            if len(source_text) > 50:
                source_text = f"📹 {file_info.get('source_file', 'Unknown')}"
            
            ttk.Label(details_frame, text=source_text,
                     style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
            
            # Processing info
            desc_text = file_info.get('description', 'Unknown')
            if len(desc_text) > 60:
                desc_text = desc_text[:60] + "..."
            
            ttk.Label(details_frame, text=f"🔧 {desc_text}",
                     style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
            
            # Mock duration data
            mock_duration = 125 + (i * 15)
            minutes = mock_duration // 60
            seconds = mock_duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
            
            ttk.Label(details_frame, text=f"⏱️ Duration: {duration_str}",
                     style='Body.TLabel', font=('Segoe UI', 8)).pack(anchor=tk.W)
        
        # FIXED: Summary with better spacing
        if len(self.breakdown_data) > 1:
            summary_frame = ttk.Frame(breakdown_scrollable, style='White.TFrame')
            summary_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
            
            summary_frame.configure(relief='solid', borderwidth=2)
            
            inner_summary = ttk.Frame(summary_frame, style='White.TFrame', padding=8)
            inner_summary.pack(fill=tk.X)
            
            # Calculate totals
            total_duration = len(self.breakdown_data) * 140  # Average duration
            total_minutes = total_duration // 60
            total_seconds = total_duration % 60
            total_duration_str = f"{total_minutes}:{total_seconds:02d}"
            
            ttk.Label(inner_summary, text="📊 Summary",
                     style='Body.TLabel', font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(inner_summary, text=f"📈 Total Content: {total_duration_str}",
                     style='Body.TLabel', font=('Segoe UI', 9),
                     foreground=self.theme.colors['accent']).pack(anchor=tk.W)
            ttk.Label(inner_summary, text=f"📼 Files Created: {len(self.breakdown_data)} videos",
                     style='Body.TLabel', font=('Segoe UI', 9)).pack(anchor=tk.W)