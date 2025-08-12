# app/src/automation/workflow_dialog/processing_thread.py - FIXED TabManager Method

import threading
import time
from queue import Queue, Empty
from typing import Callable

from ..workflow_data_models import ProcessingResult

class ProcessingThreadManager:
    """Handles background processing threads with FIXED tab state integration"""
    
    def __init__(self, dialog_controller):
        self.dialog = dialog_controller
        self.ui_queue = Queue()
        self.is_cancelled = False
        self.start_time = None
        self.processing_thread = None
        self.processing_complete = False
        
        # Start UI queue checker
        self._start_ui_queue_checker()
    
    def _start_ui_queue_checker(self):
        """Start the UI queue checker to handle cross-thread communication"""
        if self.dialog.root:
            self.dialog.root.after(100, self._check_ui_queue)
    
    def _check_ui_queue(self):
        """Check UI queue for cross-thread updates"""
        try:
            while True:
                try:
                    task = self.ui_queue.get_nowait()
                    if callable(task):
                        task()
                    elif isinstance(task, ProcessingResult):
                        self._handle_processing_completion_ui_thread(task)
                    else:
                        if hasattr(task, '__call__'):
                            task()
                except Empty:
                    break
        except Exception as e:
            print(f"Error in UI queue checker: {e}")
        
        # Reschedule
        if self.dialog.root:
            self.dialog.root.after(100, self._check_ui_queue)
    
    def start_processing(self, processing_callback: Callable, estimated_time: str):
        """Start processing in background thread"""
        
        # Reset states
        self.is_cancelled = False
        self.processing_complete = False
        self.start_time = time.time()
        
        # Update tab manager state
        if self.dialog.tab_manager:
            self.dialog.tab_manager.processing_active = True
            self.dialog.tab_manager.processing_started = True
        
        print("🎬 Starting processing thread...")
        
        def process():
            """Background processing function"""
            try:
                # Call the actual processing function
                result = processing_callback(self._update_progress)
                
                if not self.is_cancelled:
                    # Put result in queue for UI thread handling
                    self.ui_queue.put(result)
                    
            except Exception as processing_exception:
                print(f"❌ Processing error: {processing_exception}")
                import traceback
                traceback.print_exc()
                
                if not self.is_cancelled:
                    # Create error result
                    error_result = ProcessingResult(
                        success=False,
                        duration="0s",
                        processed_files=[],
                        output_folder="",
                        error_message=str(processing_exception),
                        error_solution=self._generate_error_solution(str(processing_exception))
                    )
                    # Put error result in queue
                    self.ui_queue.put(error_result)
        
        self.processing_thread = threading.Thread(target=process, daemon=True)
        self.processing_thread.start()
    
    def _update_progress(self, progress: float, step_text: str = "", elapsed_time: float = 0):
        """Update progress display - thread-safe"""
        if self.is_cancelled:
            return
        
        # Calculate elapsed time if not provided
        if elapsed_time == 0 and self.start_time:
            elapsed_time = time.time() - self.start_time
        
        # Create UI update function
        def update_ui():
            try:
                if not self.is_cancelled and self.dialog.tab_manager and self.dialog.tab_manager.processing_tab:
                    self.dialog.tab_manager.processing_tab.update_progress(progress, step_text, elapsed_time)
                    
                    # Update cancel button text
                    if progress > 80 and hasattr(self.dialog.tab_manager.processing_tab, 'cancel_btn'):
                        try:
                            self.dialog.tab_manager.processing_tab.cancel_btn.config(
                                text="❌ Cancel (Almost done...)"
                            )
                        except:
                            pass
            except Exception as ui_error:
                print(f"UI update error: {ui_error}")
        
        # Put update function in queue
        try:
            if not self.is_cancelled:
                self.ui_queue.put(update_ui)
        except Exception as queue_error:
            print(f"Queue error: {queue_error}")
    
    def _handle_processing_completion_ui_thread(self, result: ProcessingResult):
        """FIXED: Handle processing completion with proper tab state updates"""
        try:
            print(f"🎬 Processing completed on UI thread: {result.success if result else 'No result'}")
            
            self.processing_complete = True
            
            # FIXED: Update tab manager processing state
            if self.dialog.tab_manager:
                self.dialog.tab_manager.processing_active = False  # Clear active state
                self.dialog.tab_manager.processing_complete = True
                self.dialog.tab_manager.processing_result = result
            
            if result and result.success:
                print("✅ PROCESSING SUCCESSFUL - Transitioning to Results")
                
                # Update processing tab to show completion
                if self.dialog.tab_manager and self.dialog.tab_manager.processing_tab:
                    if hasattr(self.dialog.tab_manager.processing_tab, 'update_progress'):
                        self.dialog.tab_manager.processing_tab.update_progress(100, "✅ Processing completed successfully!")
                    
                    # Update cancel button to continue button
                    if hasattr(self.dialog.tab_manager.processing_tab, 'cancel_btn'):
                        try:
                            def go_to_results():
                                self._show_results_tab(result)
                            
                            self.dialog.tab_manager.processing_tab.cancel_btn.config(
                                text="✅ View Results", 
                                command=go_to_results
                            )
                        except Exception as btn_error:
                            print(f"Button update error: {btn_error}")
                
                # FIXED: Update tab buttons to allow navigation using correct method path
                if self.dialog.tab_manager and self.dialog.tab_manager.navigation:
                    self.dialog.tab_manager.navigation._update_tab_buttons(self.dialog.tab_manager.current_tab)
                
                # Auto-advance to results after 3 seconds
                self.dialog.root.after(3000, lambda: self._show_results_tab(result))
                
            else:
                print("❌ Processing failed - showing error")
                self._show_results_tab(result)
                
        except Exception as completion_error:
            print(f"Error in completion handler: {completion_error}")
            import traceback
            traceback.print_exc()
    
    def _show_results_tab(self, result: ProcessingResult):
        """Show results tab with proper result storage"""
        try:
            print("🎬 Showing results tab...")
            
            if not self.dialog.tab_manager:
                print("❌ No tab manager available")
                return
            
            # Use the tab manager's method which properly stores results
            self.dialog.tab_manager.show_results(result)
            
        except Exception as results_error:
            print(f"❌ Error showing results tab: {results_error}")
            import traceback
            traceback.print_exc()
    
    def _simulate_processing(self):
        """Fallback simulation for testing"""
        steps = [
            (10, "Validating inputs..."),
            (30, "Processing files..."),
            (60, "Applying effects..."),
            (90, "Finalizing..."),
            (100, "Complete!")
        ]
        
        def simulate():
            for progress, step in steps:
                if self.is_cancelled:
                    break
                
                self._update_progress(progress, step)
                time.sleep(0.5)
            
            if not self.is_cancelled:
                # Simulate successful result
                result = ProcessingResult(
                    success=True,
                    duration="2.5s",
                    processed_files=[{"output_name": "simulated_output.mp4"}],
                    output_folder="C:/temp/output"
                )
                self.ui_queue.put(result)
        
        self.processing_thread = threading.Thread(target=simulate, daemon=True)
        self.processing_thread.start()
    
    def cancel_processing(self):
        """Cancel current processing"""
        print("⏹️ Cancelling processing...")
        self.is_cancelled = True
        
        if self.dialog.tab_manager:
            self.dialog.tab_manager.processing_active = False
    
    def _generate_error_solution(self, error_message: str) -> str:
        """Generate helpful solution for common errors"""
        error_lower = error_message.lower()
        
        if "file not found" in error_lower:
            return "Please check that all required files exist and paths are correct."
        elif "permission" in error_lower:
            return "Please check file permissions or try running as administrator."
        elif "memory" in error_lower:
            return "Please close other applications or try processing smaller files."
        elif "ffmpeg" in error_lower:
            return "Please ensure FFmpeg is installed and accessible."
        else:
            return "Please check the logs for more details or contact support."