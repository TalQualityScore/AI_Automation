# app/src/automation/workflow_dialog/tab_management/state_handler.py
"""State Handler - Manages state preservation and restoration"""

class StateHandler:
    """Handles state management for tabs"""
    
    def __init__(self, tab_manager):
        self.tm = tab_manager
    
    def save_processing_state(self):
        """Save current processing state"""
        if not self.tm.processing_tab:
            return None
            
        state = {
            'progress': 0,
            'step_text': '',
            'counter_text': '',
            'current_video': 0,
            'total_videos': 0
        }
        
        # Save progress
        if self.tm.processing_tab.progress_var:
            state['progress'] = self.tm.processing_tab.progress_var.get()
        
        # Save labels
        if self.tm.processing_tab.step_label:
            state['step_text'] = self.tm.processing_tab.step_label.cget('text')
        
        if self.tm.processing_tab.video_counter_label:
            state['counter_text'] = self.tm.processing_tab.video_counter_label.cget('text')
        
        # Save counters
        state['current_video'] = getattr(self.tm.processing_tab, 'current_video', 0)
        state['total_videos'] = getattr(self.tm.processing_tab, 'total_videos', 0)
        
        print(f"📌 Saved processing state: {state}")
        return state
    
    def restore_processing_state(self):
        """Restore saved processing state"""
        if not self.tm.saved_processing_state or not self.tm.processing_tab:
            return
        
        state = self.tm.saved_processing_state
        
        # Restore progress bar
        if self.tm.processing_tab.progress_var:
            self.tm.processing_tab.progress_var.set(state['progress'])
        
        # Restore progress label
        if self.tm.processing_tab.progress_label:
            self.tm.processing_tab.progress_label.config(text=f"{int(state['progress'])}%")
        
        # Restore step label
        if self.tm.processing_tab.step_label:
            self.tm.processing_tab.step_label.config(text=state['step_text'])
        
        # Restore video counter
        if self.tm.processing_tab.video_counter_label and state['counter_text']:
            self.tm.processing_tab.video_counter_label.config(text=state['counter_text'])
        
        # Restore internal counters
        self.tm.processing_tab.current_video = state['current_video']
        self.tm.processing_tab.total_videos = state['total_videos']
        
        print(f"📌 Restored processing state successfully")
    
    def restore_results(self):
        """Restore results tab with saved data"""
        if not self.tm.processing_result:
            print("⚠️ No processing result to restore")
            return
        
        print(f"📊 Restoring results: success={self.tm.processing_result.success}")
        
        # Define callbacks
        def on_open_folder():
            """Open the output folder"""
            try:
                import os
                import subprocess
                if self.tm.processing_result and self.tm.processing_result.output_folder:
                    if os.path.exists(self.tm.processing_result.output_folder):
                        subprocess.Popen(f'explorer "{self.tm.processing_result.output_folder}"')
                        print(f"📁 Opened folder: {self.tm.processing_result.output_folder}")
            except Exception as e:
                print(f"❌ Error opening folder: {e}")
        
        def on_done():
            """Handle done button"""
            print("✅ Done clicked - closing workflow")
            if self.tm.dialog:
                self.tm.dialog._on_success_close()
        
        def on_copy_error():
            """Copy error details to clipboard"""
            try:
                import pyperclip
                if self.tm.processing_result and self.tm.processing_result.error_message:
                    error_text = f"Error: {self.tm.processing_result.error_message}\n"
                    if self.tm.processing_result.error_solution:
                        error_text += f"Solution: {self.tm.processing_result.error_solution}"
                    pyperclip.copy(error_text)
                    print("📋 Error details copied to clipboard")
            except Exception as e:
                print(f"❌ Error copying to clipboard: {e}")
        
        def on_close():
            """Handle close button on error"""
            print("❌ Close clicked after error")
            if self.tm.dialog:
                self.tm.dialog._on_error_close()
        
        # Show results based on success/failure
        if self.tm.processing_result.success:
            self.tm.results_tab.show_success_results(
                self.tm.processing_result,
                on_open_folder,
                on_done
            )
        else:
            self.tm.results_tab.show_error_results(
                self.tm.processing_result,
                on_copy_error,
                on_close
            )