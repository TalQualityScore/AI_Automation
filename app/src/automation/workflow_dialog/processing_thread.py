# app/src/automation/workflow_dialog/processing_thread.py - COMPLETE FIX for Results Display

import threading
import time
from queue import Queue, Empty
from typing import Callable

from ..workflow_data_models import ProcessingResult

class ProcessingThreadManager:
    """Handles background processing threads and UI communication - COMPLETE FIX"""
    
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
            while True:  # Process all pending items
                try:
                    task = self.ui_queue.get_nowait()
                    if callable(task):
                        # It's a function - execute it
                        task()
                    elif isinstance(task, ProcessingResult):
                        # It's a ProcessingResult - handle completion
                        self._handle_processing_completion_ui_thread(task)
                    else:
                        # It's some other data - try to call it
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
        """Handle processing completion - RUNS ON UI THREAD"""
        try:
            print(f"🎬 Processing completed on UI thread: {result.success if result else 'No result'}")
            
            self.processing_complete = True
            
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
                
                # Update tab navigation to allow results access
                if self.dialog.tab_manager:
                    self.dialog.tab_manager.processing_complete = True
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
        """Show results tab with data - RUNS ON UI THREAD - FIXED"""
        try:
            print("🎬 Showing results tab...")
            
            if not self.dialog.tab_manager:
                print("❌ No tab manager available")
                return
            
            # FIXED: Try different method names that might exist
            try:
                # Try the show_tab method (without underscore)
                if hasattr(self.dialog.tab_manager, 'show_tab'):
                    self.dialog.tab_manager.show_tab(2)
                # Try _show_tab method (with underscore) 
                elif hasattr(self.dialog.tab_manager, '_show_tab'):
                    self.dialog.tab_manager._show_tab(2)
                # Try show_results method directly
                elif hasattr(self.dialog.tab_manager, 'show_results'):
                    self.dialog.tab_manager.show_results(result)
                    return  # Exit early if this works
                else:
                    print("❌ No tab switching method found, using direct results display")
                    # Fallback - try to show results directly
                    self._show_results_directly(result)
                    return
                    
            except Exception as tab_switch_error:
                print(f"❌ Tab switching failed: {tab_switch_error}")
                # Fallback to direct results display
                self._show_results_directly(result)
                return
            
            # If we got here, tab switching worked, now show results
            print("✅ Tab switched successfully, now showing results...")
            
            # Show results based on success/failure
            if result.success:
                print("📊 Showing success results...")
                
                # Import the helper functions we need
                from ..workflow_ui_components import open_folder
                
                if hasattr(self.dialog.tab_manager, 'results_tab') and self.dialog.tab_manager.results_tab:
                    self.dialog.tab_manager.results_tab.show_success_results(
                        result,
                        on_open_folder=open_folder,
                        on_done=self._on_success_close
                    )
                else:
                    print("❌ No results tab available")
                    self._show_results_directly(result)
            else:
                print("❌ Showing error results...")
                
                # Import the helper functions we need
                from ..workflow_ui_components import copy_to_clipboard
                
                if hasattr(self.dialog.tab_manager, 'results_tab') and self.dialog.tab_manager.results_tab:
                    self.dialog.tab_manager.results_tab.show_error_results(
                        result,
                        on_copy_error=lambda msg: copy_to_clipboard(self.dialog.root, msg),
                        on_close=self._on_error_close
                    )
                else:
                    print("❌ No results tab available")
                    self._show_results_directly(result)
                    
        except Exception as results_error:
            print(f"❌ Error showing results tab: {results_error}")
            import traceback
            traceback.print_exc()
            
            # Fallback - show results directly
            self._show_results_directly(result)

    def _show_results_directly(self, result: ProcessingResult):
        """Fallback - show results in a simple popup window"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            if result.success:
                # Create success popup
                success_window = tk.Toplevel(self.dialog.root) if self.dialog.root else tk.Tk()
                success_window.title("Processing Complete!")
                success_window.geometry("600x400")
                success_window.configure(bg='white')
                
                # Center window
                x = (success_window.winfo_screenwidth() // 2) - 300
                y = (success_window.winfo_screenheight() // 2) - 200
                success_window.geometry(f"600x400+{x}+{y}")
                
                # Header
                header_frame = tk.Frame(success_window, bg='white')
                header_frame.pack(fill=tk.X, padx=20, pady=20)
                
                tk.Label(header_frame, text="🎉 Success!", font=('Segoe UI', 18, 'bold'), 
                        bg='white', fg='#107c10').pack()
                tk.Label(header_frame, text="Your videos have been processed successfully", 
                        font=('Segoe UI', 11), bg='white', fg='#605e5c').pack()
                
                # Results info
                info_frame = tk.Frame(success_window, bg='white')
                info_frame.pack(fill=tk.BOTH, expand=True, padx=20)
                
                tk.Label(info_frame, text=f"✅ Processing completed in {result.duration}", 
                        font=('Segoe UI', 12, 'bold'), bg='white', fg='#107c10').pack(anchor=tk.W, pady=5)
                tk.Label(info_frame, text=f"📊 {len(result.processed_files)} video(s) processed successfully", 
                        font=('Segoe UI', 10), bg='white').pack(anchor=tk.W, pady=2)
                tk.Label(info_frame, text=f"📁 Output: {result.output_folder}", 
                        font=('Segoe UI', 10), bg='white').pack(anchor=tk.W, pady=2)
                
                # File list
                tk.Label(info_frame, text="📋 Processed Files:", 
                        font=('Segoe UI', 11, 'bold'), bg='white').pack(anchor=tk.W, pady=(10, 5))
                
                for i, file_info in enumerate(result.processed_files, 1):
                    file_text = f"{i}. {file_info.get('output_name', 'Unknown')}.mp4"
                    tk.Label(info_frame, text=file_text, font=('Segoe UI', 9), 
                            bg='white', fg='#323130').pack(anchor=tk.W, padx=20, pady=1)
                
                # Buttons
                button_frame = tk.Frame(success_window, bg='white')
                button_frame.pack(fill=tk.X, padx=20, pady=20)
                
                def open_folder():
                    try:
                        import os, subprocess, platform
                        if platform.system() == "Windows":
                            os.startfile(result.output_folder)
                        elif platform.system() == "Darwin":
                            subprocess.run(["open", result.output_folder])
                        else:
                            subprocess.run(["xdg-open", result.output_folder])
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not open folder:\n{e}")
                
                def close_success():
                    success_window.destroy()
                    self._on_success_close()
                
                tk.Button(button_frame, text="📂 Open Output Folder", font=('Segoe UI', 11, 'bold'),
                        bg='#0078d4', fg='white', padx=20, pady=10, command=open_folder).pack(side=tk.LEFT, padx=(0, 10))
                tk.Button(button_frame, text="✅ Done", font=('Segoe UI', 11),
                        bg='#f3f3f3', fg='#323130', padx=20, pady=10, command=close_success).pack(side=tk.LEFT)
                
            else:
                # Show error popup
                messagebox.showerror("Processing Failed", 
                                f"Processing failed:\n{result.error_message}\n\nSolution:\n{result.error_solution}")
                self._on_error_close()
                
        except Exception as popup_error:
            print(f"❌ Error showing results popup: {popup_error}")
            # Ultimate fallback - just print and close
            self._print_results_fallback(result)
            if result.success:
                self._on_success_close()
            else:
                self._on_error_close()
    
    def _print_results_fallback(self, result: ProcessingResult):
        """Fallback - print results to console if UI fails"""
        print("\n" + "="*60)
        if result.success:
            print("🎉 AUTOMATION COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"✅ Duration: {result.duration}")
            print(f"📊 Files processed: {len(result.processed_files)}")
            print(f"📁 Output folder: {result.output_folder}")
            
            # List processed files
            for i, file_info in enumerate(result.processed_files, 1):
                print(f"   {i}. {file_info.get('output_name', 'Unknown')}")
                print(f"      Source: {file_info.get('source_file', 'Unknown')}")
                print(f"      Description: {file_info.get('description', 'No description')}")
        else:
            print("❌ PROCESSING FAILED")
            print("="*60)
            print(f"Error: {result.error_message}")
            if result.error_solution:
                print(f"Solution: {result.error_solution}")
        
        print("="*60)
    
    def _on_success_close(self):
        """Handle successful close from results tab"""
        print("🎬 Success close from results")
        if self.dialog:
            self.dialog.result = True
            if self.dialog.root:
                self.dialog.root.destroy()
    
    def _on_error_close(self):
        """Handle error close from results tab"""
        print("🎬 Error close from results")
        if self.dialog:
            self.dialog.result = False
            if self.dialog.root:
                self.dialog.root.destroy()
    
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
        """Cancel the current processing"""
        self.is_cancelled = True