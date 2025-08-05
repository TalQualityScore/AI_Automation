# app/src/automation/unified_workflow_dialog.py - SIMPLE FIX using existing modules
from .trello_card_popup import TrelloCardPopup

# Import helper functions
from .workflow_dialog.helpers import (
    create_confirmation_data_from_orchestrator,
    create_processing_result_from_orchestrator
)

# Try to import the actual modular dialog controller
try:
    from .workflow_dialog.dialog_controller import UnifiedWorkflowDialog as ModularDialog
    print("✅ Successfully imported modular UnifiedWorkflowDialog")
    MODULAR_AVAILABLE = True
except ImportError as e:
    print(f"❌ Could not import modular dialog: {e}")
    print("Will create fallback implementation...")
    MODULAR_AVAILABLE = False

if MODULAR_AVAILABLE:
    # Use the existing modular components
    class UnifiedWorkflowDialog:
        """Wrapper that uses your existing modular workflow dialog"""
        
        def __init__(self, parent=None):
            self.modular_dialog = ModularDialog(parent)
        
        @staticmethod
        def get_trello_card_id(parent=None):
            """Get Trello card ID using existing popup"""
            print("🎬 Getting Trello card ID...")
            popup = TrelloCardPopup(parent)
            return popup.show_popup()
        
        def show_workflow(self, confirmation_data, processing_callback):
            """Delegate to modular dialog controller"""
            print("🎬 Using modular workflow dialog...")
            return self.modular_dialog.show_workflow(confirmation_data, processing_callback)

else:
    # Fallback - minimal working implementation for debugging
    import tkinter as tk
    from tkinter import messagebox
    
    class UnifiedWorkflowDialog:
        """Fallback implementation for debugging import issues"""
        
        def __init__(self, parent=None):
            self.parent = parent
        
        @staticmethod
        def get_trello_card_id(parent=None):
            """Get Trello card ID using existing popup"""
            print("🎬 Getting Trello card ID (fallback)...")
            popup = TrelloCardPopup(parent)
            return popup.show_popup()
        
        def show_workflow(self, confirmation_data, processing_callback):
            """Fallback - just run processing directly for now"""
            print("🎬 Using fallback workflow (modular dialog not available)...")
            
            # Show simple confirmation
            response = messagebox.askyesno(
                "Confirm Processing",
                f"Process {confirmation_data.project_name}?\n\n"
                f"Mode: {confirmation_data.processing_mode}\n"
                f"Files: {len(confirmation_data.client_videos)} videos\n"
                f"Estimated time: {confirmation_data.estimated_time}"
            )
            
            if not response:
                return False
            
            # Show processing message
            processing_window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
            processing_window.title("Processing...")
            processing_window.geometry("400x200")
            processing_window.resizable(False, False)
            
            # Center window
            x = (processing_window.winfo_screenwidth() // 2) - 200
            y = (processing_window.winfo_screenheight() // 2) - 100
            processing_window.geometry(f"400x200+{x}+{y}")
            
            tk.Label(processing_window, text="Processing videos...", 
                    font=('Segoe UI', 14)).pack(pady=50)
            
            progress_label = tk.Label(processing_window, text="Starting...", 
                                    font=('Segoe UI', 10))
            progress_label.pack()
            
            processing_window.update()
            
            def simple_progress_callback(progress, message="", elapsed=0):
                progress_label.config(text=f"{int(progress)}% - {message}")
                processing_window.update()
            
            try:
                # Run the actual processing
                result = processing_callback(simple_progress_callback)
                
                processing_window.destroy()
                
                # Show results
                if result and result.success:
                    messagebox.showinfo(
                        "Success!",
                        f"Processing completed successfully!\n\n"
                        f"Duration: {result.duration}\n"
                        f"Files processed: {len(result.processed_files)}\n"
                        f"Output: {result.output_folder}"
                    )
                    return True
                else:
                    messagebox.showerror(
                        "Processing Failed",
                        f"Processing failed:\n{result.error_message if result else 'Unknown error'}"
                    )
                    return False
                    
            except Exception as e:
                processing_window.destroy()
                messagebox.showerror("Error", f"Processing failed: {str(e)}")
                return False

# Export the main class and helpers
__all__ = [
    'UnifiedWorkflowDialog',
    'create_confirmation_data_from_orchestrator',
    'create_processing_result_from_orchestrator'
]