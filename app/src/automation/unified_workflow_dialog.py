# app/src/automation/unified_workflow_dialog.py - Modular Main Dialog
import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from typing import Callable

from .workflow_data_models import ConfirmationData, ProcessingResult
from .workflow_ui_components import (
    WorkflowTheme, ConfirmationTab, ProcessingTab, ResultsTab, 
    NotificationPopup, open_folder, copy_to_clipboard
)

class UnifiedWorkflowDialog:
    """Main workflow dialog controller - simplified and focused"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.root = None
        self.result = None
        self.notification_settings = {
            'email': {'enabled': False, 'address': ''},
            'slack': {'enabled': False, 'webhook': ''}
        }
        
        # UI components
        self.theme = None
        self.confirmation_tab = None
        self.processing_tab = None
        self.results_tab = None
        
        # Tab control
        self.current_tab = 0
        self.tab_buttons = {}
        
        # Processing state
        self.processing_callback = None
        self.start_time = None
        self.is_cancelled = False
        
    def show_workflow(self, confirmation_data: ConfirmationData, processing_callback: Callable) -> bool:
        """Main entry point - show unified workflow"""
        self.confirmation_data = confirmation_data
        self.processing_callback = processing_callback
        
        self._create_dialog()
        return self.result if self.result is not None else False
    
    def _create_dialog(self):
        """Create main dialog window"""
        self.root = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.root.title("AI Automation Workflow")
        self.root.geometry("600x800")
        self.root.resizable(False, False)
        
        # Initialize theme
        self.theme = WorkflowTheme(self.root)
        
        # Center and make modal
        self._center_window()
        if self.parent:
            self.root.transient(self.parent)
            self.root.grab_set()
        
        self.root.lift()
        self.root.focus_force()
        
        # Create UI structure
        self._create_header()
        self._create_tab_navigation()
        self._create_content_area()
        self._initialize_tabs()
        self._show_tab(0)  # Start with confirmation
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.wait_window()
    
    def _center_window(self):
        """Center dialog on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"600x800+{x}+{y}")
    
    def _create_header(self):
        """Create header with title and notification icon"""
        header_frame = ttk.Frame(self.root, style='White.TFrame')
        header_frame.pack(fill=tk.X, padx=40, pady=(30, 0))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack(fill=tk.X)
        
        # Icon and title
        icon_label = ttk.Label(title_container, text="🎬", font=('Segoe UI', 24),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(text_frame, text="AI Automation Workflow", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="Confirm → Process → Results", style='Subheader.TLabel').pack(anchor=tk.W)
        
        # Notification icon
        notification_icon = ttk.Label(title_container, text="📧", font=('Segoe UI', 20),
                                     style='Body.TLabel', cursor="hand2")
        notification_icon.pack(side=tk.RIGHT)
        notification_icon.bind("<Button-1>", self._show_notification_popup)
    
    def _create_tab_navigation(self):
        """Create tab navigation buttons"""
        tab_frame = ttk.Frame(self.root, style='White.TFrame')
        tab_frame.pack(fill=tk.X, padx=40, pady=(20, 0))
        
        tabs = [
            ("1. Confirmation", 0),
            ("2. Processing", 1),
            ("3. Results", 2)
        ]
        
        for tab_name, tab_index in tabs:
            btn = tk.Button(tab_frame, text=tab_name, font=('Segoe UI', 11),
                           bg=self.theme.colors['tab_inactive'], 
                           fg=self.theme.colors['text_primary'],
                           relief='flat', borderwidth=0, padx=20, pady=10,
                           command=lambda idx=tab_index: self._show_tab(idx))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 1))
            self.tab_buttons[tab_index] = btn
    
    def _create_content_area(self):
        """Create content container for tabs"""
        self.content_container = ttk.Frame(self.root, style='White.TFrame')
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
    
    def _initialize_tabs(self):
        """Initialize all tab components"""
        # Tab 1: Confirmation
        self.confirmation_tab = ConfirmationTab(
            self.content_container, 
            self.confirmation_data, 
            self.theme
        )
        
        # Tab 2: Processing
        self.processing_tab = ProcessingTab(self.content_container, self.theme)
        
        # Tab 3: Results
        self.results_tab = ResultsTab(self.content_container, self.theme)
    
    def _show_tab(self, tab_index):
        """Show specified tab and update navigation"""
        # Hide all existing frames
        for widget in self.content_container.winfo_children():
            widget.pack_forget()
        
        # Show selected tab
        if tab_index == 0:
            # Confirmation tab
            frame = self.confirmation_tab.create_tab()
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Add action buttons
            self._add_confirmation_buttons(frame)
            
        elif tab_index == 1:
            # Processing tab
            frame = self.processing_tab.create_tab(self.confirmation_data.estimated_time)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Add cancel button
            self._add_processing_buttons(frame)
            
        elif tab_index == 2:
            # Results tab
            frame = self.results_tab.create_tab()
            frame.pack(fill=tk.BOTH, expand=True)
        
        # Update tab button states
        self._update_tab_buttons(tab_index)
        self.current_tab = tab_index
    
    def _add_confirmation_buttons(self, parent):
        """Add action buttons to confirmation tab"""
        button_frame = ttk.Frame(parent, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        ttk.Button(button_container, text="❌ CANCEL", style='Secondary.TButton',
                  command=self._on_cancel).pack(side=tk.LEFT, padx=(0, 15))
        
        confirm_btn = ttk.Button(button_container, text="✅ CONFIRM & RUN", 
                                style='Accent.TButton', command=self._on_confirm)
        confirm_btn.pack(side=tk.LEFT)
        confirm_btn.focus_set()
    
    def _add_processing_buttons(self, parent):
        """Add cancel button to processing tab"""
        cancel_frame = ttk.Frame(parent, style='White.TFrame')
        cancel_frame.pack(fill=tk.X, pady=30)
        
        cancel_container = ttk.Frame(cancel_frame, style='White.TFrame')
        cancel_container.pack()
        
        self.processing_tab.cancel_btn = ttk.Button(cancel_container, text="❌ Cancel", 
                                                   style='Secondary.TButton',
                                                   command=self._on_cancel)
        self.processing_tab.cancel_btn.pack()
    
    def _update_tab_buttons(self, active_tab):
        """Update tab button appearance"""
        for idx, btn in self.tab_buttons.items():
            if idx == active_tab:
                btn.configure(bg=self.theme.colors['tab_active'], 
                             fg=self.theme.colors['text_primary'])
            elif idx < active_tab:
                # Previous tabs - accessible
                btn.configure(bg=self.theme.colors['tab_inactive'], 
                             fg=self.theme.colors['text_secondary'])
            else:
                # Future tabs - disabled
                btn.configure(bg=self.theme.colors['tab_inactive'], 
                             fg=self.theme.colors['text_secondary'], 
                             state='disabled')
    
    def _show_notification_popup(self, event):
        """Show notification settings popup"""
        popup = NotificationPopup(self.root, self.notification_settings, self.theme)
        popup.show_popup()
    
    def _on_confirm(self):
        """Handle confirm button - start processing"""
        self._show_tab(1)
        self.start_time = time.time()
        self._start_processing()
    
    def _start_processing(self):
        """Start processing in background thread"""
        def process():
            try:
                if self.processing_callback:
                    result = self.processing_callback(self._update_progress)
                    self.root.after(0, lambda: self._on_processing_complete(result))
                else:
                    self._simulate_processing()
                    
            except Exception as e:
                if not self.is_cancelled:
                    self.root.after(0, lambda: self._on_processing_error(str(e)))
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    
    def _simulate_processing(self):
        """Fallback simulation for testing"""
        steps = [
            (10, "Validating inputs..."),
            (30, "Processing files..."),
            (60, "Applying effects..."),
            (90, "Finalizing..."),
            (100, "Complete!")
        ]
        
        for progress, message in steps:
            if self.is_cancelled:
                return
            
            elapsed = time.time() - self.start_time
            self.root.after(0, lambda p=progress, m=message, e=elapsed: 
                           self._update_progress(p, m, e))
            time.sleep(1)
        
        # Create mock result
        result = ProcessingResult(
            success=True,
            duration="2 minutes 30 seconds",
            processed_files=[{
                'version': 'v01',
                'source_file': 'test.mp4',
                'output_name': 'test_output',
                'description': 'Test result'
            }],
            output_folder=r"C:\Users\Desktop\Test Output"
        )
        
        self.root.after(0, lambda: self._on_processing_complete(result))
    
    def _update_progress(self, progress: float, step_text: str = "", elapsed_time: float = 0):
        """Update progress display"""
        if self.is_cancelled or not self.processing_tab:
            return
        
        self.processing_tab.update_progress(progress, step_text, elapsed_time)
        
        # Update cancel button text
        if progress > 80 and self.processing_tab.cancel_btn:
            self.processing_tab.cancel_btn.config(text="❌ Cancel (Almost done...)")
    
    def _on_processing_complete(self, result: ProcessingResult):
        """Handle successful processing completion"""
        self.processing_tab.update_progress(100, "Processing completed successfully!")
        
        if self.processing_tab.cancel_btn:
            self.processing_tab.cancel_btn.config(text="✅ Continue", 
                                                 command=lambda: self._show_results(result))
        
        # Auto-advance to results after 2 seconds
        self.root.after(2000, lambda: self._show_results(result))
    
    def _on_processing_error(self, error_message: str):
        """Handle processing error"""
        error_result = ProcessingResult(
            success=False,
            duration="",
            processed_files=[],
            output_folder="",
            error_message=error_message,
            error_solution=self._generate_error_solution(error_message)
        )
        self._show_results(error_result)
    
    def _show_results(self, result: ProcessingResult):
        """Show results tab"""
        self._show_tab(2)
        
        if result.success:
            self.results_tab.show_success_results(
                result,
                on_open_folder=open_folder,
                on_done=self._on_success_close
            )
        else:
            self.results_tab.show_error_results(
                result,
                on_copy_error=lambda msg: copy_to_clipboard(self.root, msg),
                on_close=self._on_error_close
            )
    
    def _generate_error_solution(self, error_message: str) -> str:
        """Generate error solutions based on message content"""
        error_lower = error_message.lower()
        
        if "google drive" in error_lower and "404" in error_lower:
            return """1. Check if the Google Drive folder link is correct and accessible
2. Verify the folder is shared with your service account email  
3. Ensure the folder contains video files (.mp4 or .mov)
4. Try opening the Google Drive link in your browser to confirm access"""
        
        elif "trello" in error_lower:
            return """1. Verify your Trello API key and token are correct
2. Check if the Trello card ID exists and is accessible
3. Ensure the Trello card has proper description with Google Drive link"""
        
        elif "ffmpeg" in error_lower:
            return """1. Ensure FFmpeg is installed and available in your system PATH
2. Check if input video files are not corrupted
3. Verify you have enough disk space for processing"""
        
        else:
            return """1. Check your internet connection
2. Verify all API credentials are correct
3. Ensure input files and links are accessible
4. Try restarting the application"""
    
    def _on_success_close(self):
        """Handle successful completion"""
        self.result = True
        self.root.destroy()
    
    def _on_error_close(self):
        """Handle error close"""
        self.result = False
        self.root.destroy()
    
    def _on_cancel(self):
        """Handle cancel action"""
        if self.current_tab == 1:  # Processing tab
            response = messagebox.askyesno(
                "Cancel Processing", 
                "Are you sure you want to cancel? This will stop the current processing."
            )
            if not response:
                return
            self.is_cancelled = True
        
        self.result = False
        self.root.destroy()

# Helper functions for integration
def create_confirmation_data_from_orchestrator(card_data: dict, 
                                             processing_mode: str,
                                             project_info: dict,
                                             downloaded_videos: list,
                                             validation_issues: list = None):
    """Convert orchestrator data to ConfirmationData format"""
    import os
    from .workflow_data_models import ConfirmationData, ValidationIssue
    
    project_name = project_info.get('project_name', 'Unknown Project')
    account = f"{project_info.get('account_code', 'Unknown')} Account"
    platform = "YouTube"
    
    # Determine templates based on processing mode
    templates = []
    if processing_mode == "connector_quiz":
        templates = [
            "Add Blake connector (YT/Connectors/)",
            "Add quiz outro (YT/Quiz/)",
            "Apply slide transition effects"
        ]
    elif processing_mode == "quiz_only":
        templates = [
            "Add quiz outro (YT/Quiz/)",
            "Apply slide transition effects"  
        ]
    elif processing_mode == "save_only":
        templates = ["Save and rename videos"]
    
    output_location = f"GH {project_name} {project_info.get('ad_type', '')} {project_info.get('test_name', '')} Quiz"
    
    file_count = len(downloaded_videos)
    if processing_mode == "save_only":
        estimated_time = f"{file_count * 30} seconds - {file_count * 60} seconds"
    else:
        estimated_time = f"{file_count * 2}-{file_count * 3} minutes"
    
    file_sizes = [(os.path.basename(video), 150) for video in downloaded_videos]
    
    issues = []
    if validation_issues:
        for issue in validation_issues:
            issues.append(ValidationIssue(
                severity=issue.get('severity', 'info'),
                message=issue.get('message', str(issue))
            ))
    
    return ConfirmationData(
        project_name=project_name,
        account=account,
        platform=platform,
        processing_mode=processing_mode.replace('_', ' ').upper(),
        client_videos=[os.path.basename(video) for video in downloaded_videos],
        templates_to_add=templates,
        output_location=output_location,
        estimated_time=estimated_time,
        issues=issues,
        file_sizes=file_sizes
    )

def create_processing_result_from_orchestrator(processed_files: list,
                                             start_time: float,
                                             output_folder: str,
                                             success: bool = True):
    """Convert orchestrator results to ProcessingResult format"""
    import time
    from .workflow_data_models import ProcessingResult
    
    duration_seconds = time.time() - start_time
    duration_minutes = int(duration_seconds // 60)
    duration_secs = int(duration_seconds % 60)
    duration_str = f"{duration_minutes} minutes {duration_secs} seconds"
    
    result_files = []
    for file_info in processed_files:
        result_files.append({
            'version': file_info.get('version', 'v01'),
            'source_file': file_info.get('source_file', 'unknown'),
            'output_name': file_info.get('output_name', 'processed_video'),
            'description': file_info.get('description', 'Processed video')
        })
    
    return ProcessingResult(
        success=success,
        duration=duration_str,
        processed_files=result_files,
        output_folder=output_folder
    )

# Test function
def test_unified_workflow():
    """Test the unified workflow"""
    from .workflow_data_models import ConfirmationData, ValidationIssue, ProcessingResult
    import time
    
    test_data = ConfirmationData(
        project_name="Test Project VTD 12036",
        account="OO (Olive Oil)",
        platform="YouTube",
        processing_mode="CONNECTOR + QUIZ",
        client_videos=["video1.mp4", "video2.mp4"],
        templates_to_add=["Add connector", "Add quiz outro"],
        output_location="Test Output Location",
        estimated_time="3-5 minutes",
        issues=[ValidationIssue("info", "Test issue")],
        file_sizes=[("video1.mp4", 200), ("video2.mp4", 300)]
    )
    
    def mock_callback(progress_callback):
        steps = [(25, "Step 1"), (50, "Step 2"), (75, "Step 3"), (100, "Complete")]
        for progress, message in steps:
            progress_callback(progress, message)
            time.sleep(1)
        
        return ProcessingResult(
            success=True,
            duration="2 minutes",
            processed_files=[{'version': 'v01', 'source_file': 'test.mp4', 
                            'output_name': 'test_output', 'description': 'Test'}],
            output_folder=r"C:\Test"
        )
    
    dialog = UnifiedWorkflowDialog()
    result = dialog.show_workflow(test_data, mock_callback)
    print(f"Result: {'Success' if result else 'Cancelled'}")

if __name__ == "__main__":
    test_unified_workflow()