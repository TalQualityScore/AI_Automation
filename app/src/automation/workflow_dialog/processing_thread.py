# app/src/automation/workflow_dialog/processing_thread.py
import threading
import time
from queue import Queue, Empty
from typing import Callable

from ..workflow_data_models import ProcessingResult

class ProcessingThreadManager:
    """Handles background processing threads and UI communication"""
    
    def __init__(self, dialog_controller):
        self.dialog = dialog_controller
        self.ui_queue = Queue()
        self.is_cancelled = False
        self.start_time = None
        self.processing_thread = None
        
        # Start UI queue checker
        self._start_ui_queue_checker()
    
    def _start_ui_queue_checker(self):
        """Start the UI queue checker to handle cross-thread communication"""
        if self.dialog.root:
            self.dialog.root.after(100, self._check_ui_queue)
    
    def _check_ui_queue(self):
        """Check UI queue for cross-thread updates"""
        try:
            task = self.ui_queue.get_nowait()
            if callable(task):
                # It's a function - execute it
                task()
            else:
                # It's a ProcessingResult - handle completion
                self._handle_processing_completion(task)
        except Empty:
            pass
        
        # Continue checking if dialog still exists
        if self.dialog.root:
            self.dialog.root.after(100, self._check_ui_queue)
    
    def start_processing(self, processing_callback: Callable, estimated_duration: str):
        """Start processing in background thread"""
        self.start_time = time.time()
        self.is_cancelled = False
        
        def process():
            try:
                if processing_callback:
                    print("🔍 DEBUG: About to call processing callback")
                    result = processing_callback(self._update_progress)
                    print(f"🔍 DEBUG: Processing returned result: {result}")
                    
                    if result:
                        # Schedule completion on main thread
                        if self.dialog.root and self.dialog.root.winfo_exists():
                            self.ui_queue.put(result)
                        else:
                            print("🔍 DEBUG: UI window closed, cannot show results")
                    else:
                        print("❌ No result returned from processing")
                else:
                    # Fallback simulation
                    self._simulate_processing()
                    
            except Exception as e:
                if not self.is_cancelled:
                    # Schedule error handling on main thread
                    try:
                        self.ui_queue.put(lambda: self._on_processing_error(str(e)))
                    except:
                        pass
        
        self.processing_thread = threading.Thread(target=process, daemon=True)
        self.processing_thread.start()
    
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
        
        try:
            self.ui_queue.put(result)
        except:
            pass
    
    def _update_progress(self, progress: float, step_text: str = "", elapsed_time: float = 0):
        """Update progress display - thread-safe"""
        if self.is_cancelled or not self.dialog.tab_manager.processing_tab:
            return
        
        # Calculate elapsed time if not provided
        if elapsed_time == 0 and self.start_time:
            elapsed_time = time.time() - self.start_time
        
        # Schedule UI update on main thread
        def update_ui():
            try:
                if not self.is_cancelled and self.dialog.tab_manager.processing_tab:
                    self.dialog.tab_manager.processing_tab.update_progress(progress, step_text, elapsed_time)
                    
                    # Update cancel button text
                    if progress > 80 and hasattr(self.dialog.tab_manager.processing_tab, 'cancel_btn'):
                        try:
                            self.dialog.tab_manager.processing_tab.cancel_btn.config(
                                text="❌ Cancel (Almost done...)"
                            )
                        except:
                            pass
            except Exception:
                # Silently ignore UI update errors
                pass
        
        try:
            if hasattr(self.dialog, 'root') and self.dialog.root:
                self.ui_queue.put(update_ui)
        except Exception:
            # Silently ignore scheduling errors
            pass
    
    def _handle_processing_completion(self, result: ProcessingResult):
        """Handle successful processing completion"""
        try:
            if not self.is_cancelled and self.dialog.tab_manager:
                self.dialog.tab_manager.on_processing_complete(result)
        except Exception as e:
            print(f"Error handling processing completion: {e}")
    
    def _on_processing_error(self, error_message: str):
        """Handle processing error"""
        try:
            error_result = ProcessingResult(
                success=False,
                duration="",
                processed_files=[],
                output_folder="",
                error_message=error_message,
                error_solution=self._generate_error_solution(error_message)
            )
            
            if self.dialog.tab_manager:
                self.dialog.tab_manager.show_results(error_result)
        except Exception:
            # Basic error fallback
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
        """Cancel the current processing"""
        self.is_cancelled = True