# app/src/automation/processing_dialog.py
import tkinter as tk
from tkinter import ttk
import time
import threading
from typing import Callable, Optional

class ProcessingDialog:
    """Real-time processing dialog with progress bar and time estimates"""
    
    def __init__(self, parent=None):
        self.root = None
        self.parent = parent
        self.processing_callback = None
        self.progress_var = None
        self.progress_label = None
        self.time_label = None
        self.start_time = None
        self.is_cancelled = False
        
    def show_processing(self, processing_callback: Callable, estimated_duration: str = "5-8 minutes"):
        """Show processing dialog and execute callback"""
        self.processing_callback = processing_callback
        self._create_dialog(estimated_duration)
        
    def _create_dialog(self, estimated_duration: str):
        """Create and display the processing dialog"""
        self.root = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.root.title("Processing Videos")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Apply white theme
        self._apply_white_theme()
        
        # Center and make modal
        self._center_window()
        self.root.transient(self.parent)
        self.root.grab_set()
        self.root.lift()
        self.root.focus_force()
        
        # Create UI
        self._create_header()
        self._create_progress_section(estimated_duration)
        self._create_cancel_button()
        
        # Prevent window close during processing
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Start processing
        self.start_time = time.time()
        self._start_processing()
        
        self.root.wait_window()
        
    def _apply_white_theme(self):
        """Apply pure white theme"""
        self.colors = {
            'bg': '#ffffff',
            'accent': '#0078d4',
            'text_primary': '#323130',
            'text_secondary': '#605e5c',
            'progress_bg': '#f3f3f3'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        style = ttk.Style()
        style.configure('White.TFrame', background=self.colors['bg'])
        style.configure('Header.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 16, 'bold'))
        style.configure('Body.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        style.configure('Secondary.TButton', font=('Segoe UI', 10),
                       padding=(20, 8))
        
        # Custom progress bar style
        style.configure('Custom.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['progress_bg'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])
    
    def _center_window(self):
        """Center dialog on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"500x300+{x}+{y}")
    
    def _create_header(self):
        """Create header section"""
        header_frame = ttk.Frame(self.root, style='White.TFrame')
        header_frame.pack(fill=tk.X, padx=40, pady=(40, 30))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack()
        
        # Icon
        icon_label = ttk.Label(title_container, text="⚙️", font=('Segoe UI', 24),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Title
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT)
        
        ttk.Label(text_frame, text="Processing Videos", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="Please wait while we process your videos...", 
                 style='Body.TLabel', font=('Segoe UI', 11),
                 foreground=self.colors['text_secondary']).pack(anchor=tk.W)
    
    def _create_progress_section(self, estimated_duration: str):
        """Create progress bar and status section"""
        progress_frame = ttk.Frame(self.root, style='White.TFrame')
        progress_frame.pack(fill=tk.X, padx=40, pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.progress_var,
                                           style='Custom.Horizontal.TProgressbar',
                                           length=420, height=20)
        self.progress_bar.pack(pady=(0, 15))
        
        # Progress percentage
        self.progress_label = ttk.Label(progress_frame,
                                       text="Initializing...",
                                       style='Body.TLabel',
                                       font=('Segoe UI', 11, 'bold'))
        self.progress_label.pack(pady=(0, 8))
        
        # Current step
        self.step_label = ttk.Label(progress_frame,
                                   text="Starting validation process...",
                                   style='Body.TLabel',
                                   font=('Segoe UI', 10))
        self.step_label.pack(pady=(0, 8))
        
        # Time remaining
        self.time_label = ttk.Label(progress_frame,
                                   text=f"Estimated duration: {estimated_duration}",
                                   style='Body.TLabel',
                                   font=('Segoe UI', 9, 'italic'),
                                   foreground=self.colors['text_secondary'])
        self.time_label.pack()
    
    def _create_cancel_button(self):
        """Create cancel button"""
        button_frame = ttk.Frame(self.root, style='White.TFrame')
        button_frame.pack(fill=tk.X, padx=40, pady=30)
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        self.cancel_btn = ttk.Button(button_container, text="❌ Cancel", 
                                    style='Secondary.TButton',
                                    command=self._on_cancel)
        self.cancel_btn.pack()
    
    def _start_processing(self):
        """Start processing in background thread"""
        def process():
            try:
                if self.processing_callback:
                    # Execute the actual processing with progress updates
                    self.processing_callback(self._update_progress)
                else:
                    # Fallback simulation for testing
                    self._simulate_processing()
                    
            except Exception as e:
                if not self.is_cancelled:
                    self.root.after(0, lambda: self._on_error(str(e)))
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    
    def _simulate_processing(self):
        """Simulate processing for testing purposes"""
        steps = [
            (10, "Validating Trello card data..."),
            (20, "Downloading videos from Google Drive..."),
            (35, "Analyzing video dimensions..."),
            (50, "Processing video 1 of 3..."),
            (65, "Processing video 2 of 3..."),
            (80, "Processing video 3 of 3..."),
            (90, "Applying transitions and effects..."),
            (95, "Finalizing outputs..."),
            (100, "Processing complete!")
        ]
        
        for progress, step_text in steps:
            if self.is_cancelled:
                return
                
            elapsed_time = time.time() - self.start_time
            self.root.after(0, lambda p=progress, s=step_text, e=elapsed_time: 
                           self._update_progress(p, s, e))
            time.sleep(1)  # Simulate work
        
        # Processing complete
        self.root.after(0, self._on_complete)
    
    def _update_progress(self, progress: float, step_text: str = "", elapsed_time: float = 0):
        """Update progress bar and labels"""
        if self.is_cancelled:
            return
            
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
        
        # Update cancel button text as we progress
        if progress > 80:
            self.cancel_btn.config(text="❌ Cancel (Almost done...)")
    
    def _on_complete(self):
        """Handle processing completion"""
        self.progress_var.set(100)
        self.progress_label.config(text="100%")
        self.step_label.config(text="Processing completed successfully!")
        self.time_label.config(text="Ready to view results...")
        self.cancel_btn.config(text="✅ Continue", command=self._on_continue)
    
    def _on_error(self, error_message: str):
        """Handle processing error"""
        self.step_label.config(text="❌ Processing failed")
        self.time_label.config(text=f"Error: {error_message}")
        self.cancel_btn.config(text="❌ Close", command=self._on_cancel)
    
    def _on_continue(self):
        """Handle continue button after completion"""
        self.root.destroy()
    
    def _on_cancel(self):
        """Handle cancel button"""
        self.is_cancelled = True
        
        # Show cancellation confirmation if processing is active
        if hasattr(self, 'progress_var') and self.progress_var.get() < 100:
            response = tk.messagebox.askyesno(
                "Cancel Processing", 
                "Are you sure you want to cancel? This will stop the current processing."
            )
            if not response:
                self.is_cancelled = False
                return
        
        self.root.destroy()
    
    def update_from_external(self, progress: float, message: str):
        """Allow external updates to progress (thread-safe)"""
        if not self.is_cancelled:
            elapsed = time.time() - self.start_time if self.start_time else 0
            self.root.after(0, lambda: self._update_progress(progress, message, elapsed))

# Test function
def test_processing_dialog():
    """Test the processing dialog"""
    def dummy_processing_callback(update_func):
        """Dummy processing function that uses the update callback"""
        steps = [
            (15, "Connecting to Trello API..."),
            (30, "Downloading large video files..."),
            (50, "Running FFmpeg processing..."),
            (75, "Applying video transitions..."),
            (90, "Saving final outputs..."),
            (100, "All processing complete!")
        ]
        
        for progress, message in steps:
            time.sleep(1.5)  # Simulate processing time
            update_func(progress, message)
    
    dialog = ProcessingDialog()
    dialog.show_processing(dummy_processing_callback, "3-5 minutes")

if __name__ == "__main__":
    # Test the processing dialog
    test_processing_dialog()