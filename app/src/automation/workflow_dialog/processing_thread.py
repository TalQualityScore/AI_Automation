# app/src/automation/workflow_dialog/processing_thread.py - UPDATED for Tab State

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
        
        # Continue checking if dialog still exists and not cancelled
        if self.dialog.root and not self.is_cancelled:
            self.dialog.root.after(100, self._check_ui_queue)
    
    def start_processing(self, processing_callback: Callable, estimated_duration: str):
        """Start processing in background thread"""
        self.start_time = time.time()
        self.is_cancelled = False
        self.processing_complete = False
        
        def process():
            try:
                if processing_callback:
                    print("🔍 DEBUG: About to call processing callback")
                    result = processing_callback(self._update_progress)
                    print(f"🔍 DEBUG: Processing returned result: {result}")
                    
                    if result and not self.is_cancelled:
                        # Put the result directly in the queue
                        self.ui_queue.put(result)
                    else:
                        print("❌ No result returned from processing or cancelled")
                else:
                    # Fallback simulation
                    self._simulate_processing()
                    
            except Exception as processing_exception:
                print(f"❌ Processing failed: {processing_exception}")
                if not self.is_cancelled:
                    # Create error result
                    error_result = ProcessingResult(
                        success=False,
                        duration="",
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
                
                # FIXED: Update tab buttons to allow navigation
                if self.dialog.tab_manager:
                    self.dialog.tab_manager._update_tab_buttons(self.dialog.tab_manager.current_tab)
                
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
        
        for progress, message in steps:
            if self.is_cancelled:
                return
            
            elapsed = time.time() - self.start_time if self.start_time else 0
            self._update_progress(progress, message, elapsed)
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
        
        # Put result in queue
        try:
            self.ui_queue.put(result)
        except:
            pass
    
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
    
    def cancel_processing(self):
        """Cancel the current processing and update tab states"""
        print("🛑 Canceling processing...")
        self.is_cancelled = True
        
        # FIXED: Update tab manager state when cancelling
        if self.dialog.tab_manager:
            self.dialog.tab_manager.processing_active = False
            self.dialog.tab_manager._update_tab_buttons(self.dialog.tab_manager.current_tab)