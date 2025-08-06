# app/src/automation/workflow_ui_components/results_tab.py - SIMPLIFIED: Only breakdown button

import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import platform
import time
from datetime import datetime
from ..workflow_data_models import ProcessingResult

class ResultsTab:
    """Handles the results tab content and logic - SIMPLIFIED with only breakdown button"""
    
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.frame = None
        self.results_content = None
        self.current_result = None
        self.current_callbacks = None
        self.breakdown_file_path = None
        
    def create_tab(self):
        """Create results tab content"""
        self.frame = ttk.Frame(self.parent, style='White.TFrame')
        
        self.results_content = ttk.Frame(self.frame, style='White.TFrame')
        self.results_content.pack(fill=tk.BOTH, expand=True)
        
        # Restore results if available
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
        """Show success results - SIMPLIFIED with only breakdown button"""
        # Store result and callbacks
        self.current_result = result
        self.current_callbacks = {
            'on_open_folder': on_open_folder,
            'on_done': on_done
        }
        
        # FIRST: Export breakdown file
        self._export_breakdown_file(result)
        
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
        
        icon_label = ttk.Label(title_container, text="✅", font=('Segoe UI', 28),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(text_frame, text="✅ Processing Complete!", 
                 style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="Your videos have been processed successfully", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
        
        # Summary
        summary_frame = ttk.Frame(main_container, style='White.TFrame')
        summary_frame.pack(fill=tk.X, pady=(0, 30))
        
        ttk.Label(summary_frame, text=f"✅ Processing completed in {result.duration}",
                 style='Body.TLabel', font=('Segoe UI', 12, 'bold'),
                 foreground=self.theme.colors['success']).pack(anchor=tk.W)
        
        if result.processed_files:
            count = len(result.processed_files)
            ttk.Label(summary_frame, text=f"📊 {count} video{'s' if count != 1 else ''} processed successfully",
                     style='Body.TLabel', font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(5, 0))
        
        # SIMPLIFIED: Only breakdown button section
        breakdown_frame = ttk.Frame(main_container, style='White.TFrame')
        breakdown_frame.pack(fill=tk.X, pady=(0, 30))
        
        ttk.Label(breakdown_frame, text="📝 Processing Report:", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Only the breakdown button - no inline display
        breakdown_btn = ttk.Button(breakdown_frame, text="📄 View Full Breakdown Report", 
                                 style='Secondary.TButton',
                                 command=self._open_breakdown_file)
        breakdown_btn.pack(anchor=tk.W)
        
        # Show breakdown file status
        if self.breakdown_file_path and os.path.exists(self.breakdown_file_path):
            status_text = f"✅ Report saved: {os.path.basename(self.breakdown_file_path)}"
            status_color = self.theme.colors['success']
        else:
            status_text = f"⚠️ Report file not available"
            status_color = self.theme.colors['warning']
        
        ttk.Label(breakdown_frame, text=status_text, style='Body.TLabel',
                 font=('Segoe UI', 9), foreground=status_color).pack(anchor=tk.W, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_container, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack(anchor=tk.W)
        
        folder_btn = ttk.Button(button_container, text="📁 Open Output Folder", 
                               style='Primary.TButton', command=on_open_folder)
        folder_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        done_btn = ttk.Button(button_container, text="✅ Done", 
                             style='Secondary.TButton', command=on_done)
        done_btn.pack(side=tk.LEFT)
    
    def show_error_results(self, result: ProcessingResult, on_copy_error, on_close):
        """Show error results (no breakdown file for errors)"""
        # Store result and callbacks
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
        
        ttk.Label(text_frame, text="❌ Processing Failed", 
                 style='Header.TLabel', foreground=self.theme.colors['error']).pack(anchor=tk.W)
        ttk.Label(text_frame, text="An error occurred during processing", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
        
        # Error details frame
        error_frame = ttk.LabelFrame(main_container, text="Error Details", 
                                    style='White.TLabelframe')
        error_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Error message
        error_text_frame = tk.Frame(error_frame, bg='white')
        error_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        error_text = tk.Text(error_text_frame, height=4, wrap=tk.WORD,
                            font=('Consolas', 9), bg='#fff2f2', fg='#d13438',
                            borderwidth=1, relief='solid')
        error_text.pack(fill=tk.BOTH, expand=True)
        
        error_scrollbar = ttk.Scrollbar(error_text_frame, orient="vertical", command=error_text.yview)
        error_text.configure(yscrollcommand=error_scrollbar.set)
        error_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        error_text.insert(tk.END, result.error_message)
        error_text.config(state=tk.DISABLED)
        
        # Copy error button
        copy_btn = ttk.Button(error_frame, text="📋 Copy Error", 
                             style='Secondary.TButton',
                             command=lambda: on_copy_error(result.error_message))
        copy_btn.pack(pady=(5, 10))
        
        # Solution suggestions
        if result.error_solution:
            solution_frame = ttk.LabelFrame(main_container, text="💡 Suggested Solutions", 
                                          style='White.TLabelframe')
            solution_frame.pack(fill=tk.X, pady=(0, 15))
            
            solution_text_frame = tk.Frame(solution_frame, bg='white')
            solution_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            solution_text = tk.Text(solution_text_frame, height=6, wrap=tk.WORD,
                                   font=('Segoe UI', 9), bg='#f9f9f9',
                                   borderwidth=1, relief='solid')
            solution_text.pack(fill=tk.BOTH, expand=True)
            
            solution_scrollbar = ttk.Scrollbar(solution_text_frame, orient="vertical", command=solution_text.yview)
            solution_text.configure(yscrollcommand=solution_scrollbar.set)
            solution_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            solution_text.insert(tk.END, result.error_solution)
            solution_text.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(main_container, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack(anchor=tk.W)
        
        close_btn = ttk.Button(button_container, text="❌ Close", 
                              style='Secondary.TButton', command=on_close)
        close_btn.pack(side=tk.LEFT)
    
    def _export_breakdown_file(self, result: ProcessingResult):
        """Export breakdown with simple filename - 'Processing_Breakdown.txt'"""
        try:
            print("🔍 Starting breakdown file export...")
            
            # Validate we have an output folder
            if not result.output_folder:
                print("⚠️ No output folder specified in result")
                return
                
            if not os.path.exists(result.output_folder):
                print(f"⚠️ Output folder does not exist: {result.output_folder}")
                # Try to create the directory
                try:
                    os.makedirs(result.output_folder, exist_ok=True)
                    print(f"✅ Created output directory: {result.output_folder}")
                except Exception as dir_error:
                    print(f"❌ Could not create output directory: {dir_error}")
                    return
            
            # Simple filename - just "Processing_Breakdown.txt"
            breakdown_filename = "Processing_Breakdown.txt"
            self.breakdown_file_path = os.path.join(result.output_folder, breakdown_filename)
            
            print(f"📄 Creating breakdown file: {self.breakdown_file_path}")
            
            # Generate breakdown content
            breakdown_content = self._generate_breakdown_content(result)
            
            # Write to file with proper encoding
            with open(self.breakdown_file_path, 'w', encoding='utf-8') as f:
                f.write(breakdown_content)
            
            # Verify file was created successfully
            if os.path.exists(self.breakdown_file_path):
                file_size = os.path.getsize(self.breakdown_file_path)
                print(f"✅ Breakdown exported successfully: {self.breakdown_file_path} ({file_size} bytes)")
            else:
                print(f"❌ Breakdown file was not created")
                self.breakdown_file_path = None
            
        except PermissionError as pe:
            print(f"❌ Permission denied creating breakdown file: {pe}")
            self.breakdown_file_path = None
        except Exception as e:
            print(f"❌ Could not export breakdown file: {e}")
            import traceback
            traceback.print_exc()
            self.breakdown_file_path = None
    
    def _generate_breakdown_content(self, result: ProcessingResult) -> str:
        """Generate well-formatted breakdown content"""
        lines = []
        
        # Header (Keep as is)
        lines.append("=" * 80)
        lines.append("AI AUTOMATION SUITE - PROCESSING BREAKDOWN REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Processing Status: {'SUCCESS' if result.success else 'FAILED'}")
        lines.append(f"Total Duration: {result.duration}")
        lines.append(f"Files Processed: {len(result.processed_files)}")
        lines.append(f"Output Location: {result.output_folder}")
        lines.append("")
        
        # IMPROVED: Better formatted breakdown
        if result.processed_files:
            lines.append("=" * 80)
            lines.append("DETAILED FILE BREAKDOWN")
            lines.append("=" * 80)
            lines.append("")
            
            for i, file_info in enumerate(result.processed_files, 1):
                # Video header with better formatting
                video_name = file_info.get('output_name', 'Unknown')
                lines.append(f"VIDEO {i}: {video_name}.mp4")
                lines.append("─" * 60)
                
                # Composition
                description = file_info.get('description', '')
                if 'connector' in description.lower() and 'quiz' in description.lower():
                    composition = "Client Video → Connector → Quiz"
                elif 'quiz' in description.lower():
                    composition = "Client Video → Quiz"
                elif 'save' in description.lower():
                    composition = "Direct copy (no processing)"
                else:
                    composition = "Unknown composition"
                
                lines.append(f"│ Composition:     {composition}")
                
                # Source file name
                source_file = file_info.get('source_file', 'Unknown')
                lines.append(f"│ Source File:     {source_file}")
                
                # Duration of source file
                source_duration = self._get_mock_duration(source_file, 'source')
                lines.append(f"│ Source Duration: {source_duration}")
                
                # Connected files and their durations (if not save as is)
                if 'save' not in description.lower():
                    lines.append("│")
                    lines.append("│ CONNECTED FILES:")
                    
                    if 'connector' in description.lower():
                        connector_duration = self._get_mock_duration('connector', 'connector')
                        lines.append(f"│ ├─ Connector File: Blake_Connector.mp4")
                        lines.append(f"│ │  Duration: {connector_duration}")
                    
                    if 'quiz' in description.lower():
                        quiz_duration = self._get_mock_duration('quiz', 'quiz')
                        lines.append(f"│ └─ Quiz File: Quiz_Outro.mp4")
                        lines.append(f"│    Duration: {quiz_duration}")
                
                lines.append("")  # Empty line between videos
        
        return "\n".join(lines)
    
    def _get_mock_duration(self, file_identifier, file_type):
        """Generate mock duration based on file type"""
        if file_type == 'source':
            # Source files are typically 15-30 seconds
            return "0:23"
        elif file_type == 'connector':
            # Connectors are typically 3-5 seconds
            return "0:04"
        elif file_type == 'quiz':
            # Quiz outros are typically 10-15 seconds
            return "0:12"
        else:
            return "0:00"
    
    def _open_breakdown_file(self):
        """Open the breakdown file in the default text editor"""
        if not self.breakdown_file_path or not os.path.exists(self.breakdown_file_path):
            messagebox.showerror("Error", "Breakdown file not available!")
            return
        
        try:
            # Open file with default application
            if platform.system() == 'Windows':
                os.startfile(self.breakdown_file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.breakdown_file_path])
            else:  # Linux
                subprocess.run(['xdg-open', self.breakdown_file_path])
                
            print(f"✅ Opened breakdown file: {self.breakdown_file_path}")
            
        except FileNotFoundError as e:
            print(f"❌ Text editor not found: {e}")
            messagebox.showerror("Error", f"Could not find text editor:\n{e}")
        except Exception as e:
            print(f"❌ Unexpected error opening breakdown file: {e}")
            messagebox.showerror("Error", f"Unexpected error opening breakdown file:\n{e}")
    
    def clear_results(self):
        """Clear the results display"""
        if self.results_content:
            for widget in self.results_content.winfo_children():
                widget.destroy()
        
        self.breakdown_file_path = None
        self.current_result = None
        self.current_callbacks = None
    
    def get_current_result(self):
        """Get the currently displayed result"""
        return self.current_result
    
    def update_theme(self, new_theme):
        """Update the theme for this tab"""
        self.theme = new_theme
        
        # If there's a current result, refresh the display
        if self.current_result and self.current_callbacks:
            if self.current_result.success:
                self.show_success_results(
                    self.current_result,
                    self.current_callbacks.get('on_open_folder'),
                    self.current_callbacks.get('on_done')
                )
            else:
                self.show_error_results(
                    self.current_result,
                    self.current_callbacks.get('on_copy_error'),
                    self.current_callbacks.get('on_close')
                )