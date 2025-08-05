# app/src/automation/workflow_dialog/dialog_controller.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from ..workflow_data_models import ConfirmationData
from ..workflow_ui_components import WorkflowTheme
from ..trello_card_popup import TrelloCardPopup

from .tab_management import TabManager
from .processing_thread import ProcessingThreadManager
from .notification_handlers import NotificationManager

class UnifiedWorkflowDialog:
    """Main workflow dialog controller - coordinates all components"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.root = None
        self.result = None
        
        # Initialize managers
        self.theme = None
        self.tab_manager = None
        self.processing_manager = None
        self.notification_manager = None
        
        # Data
        self.confirmation_data = None
        self.processing_callback = None
        
    @staticmethod
    def get_trello_card_id(parent=None):
        """Static method to get Trello card ID before starting workflow"""
        print("🎬 UnifiedWorkflowDialog.get_trello_card_id() called")
        
        try:
            popup = TrelloCardPopup(parent)
            card_id = popup.show_popup()
            
            print(f"🎬 get_trello_card_id() returning: {card_id}")
            return card_id
            
        except Exception as e:
            print(f"❌ Error in get_trello_card_id(): {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
        
        # Initialize managers
        self._initialize_managers()
        
        # Create UI structure
        self._create_header()
        self.tab_manager.create_tab_navigation(self.root)
        self.tab_manager.create_content_area(self.root)
        self.tab_manager.initialize_tabs(self.confirmation_data, self.theme)
        self.tab_manager.show_tab(0)  # Start with confirmation
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.wait_window()
    
    def _initialize_managers(self):
        """Initialize all component managers"""
        self.tab_manager = TabManager(self)
        self.processing_manager = ProcessingThreadManager(self)
        self.notification_manager = NotificationManager(self, self.theme)
    
    def _center_window(self):
        """Center dialog on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"600x800+{x}+{y}")
    
    def _create_header(self):
        """Create header with title and notification icons"""
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
        
        # Notification icons container
        notification_frame = ttk.Frame(title_container, style='White.TFrame')
        notification_frame.pack(side=tk.RIGHT)
        
        # Create notification icons
        self.notification_manager.create_notification_icons(notification_frame)
    
    def _on_confirm(self):
        """Handle confirm button - start processing"""
        self.tab_manager.on_confirm_clicked()
    
    def _on_cancel(self):
        """Handle cancel action"""
        if hasattr(self.tab_manager, 'current_tab') and self.tab_manager.current_tab == 1:  # Processing tab
            response = messagebox.askyesno(
                "Cancel Processing", 
                "Are you sure you want to cancel? This will stop the current processing."
            )
            if not response:
                return
            
            if self.processing_manager:
                self.processing_manager.cancel_processing()
        
        self.result = False
        self.root.destroy()
    
    def _on_success_close(self):
        """Handle successful completion"""
        self.result = True
        self.root.destroy()
    
    def _on_error_close(self):
        """Handle error close"""
        self.result = False
        self.root.destroy()