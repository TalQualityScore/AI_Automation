# app/src/automation/workflow_dialog/dialog_controller.py - ENHANCED FOR DROPDOWN SELECTIONS

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
    """Main workflow dialog controller with dropdown selection support"""
    
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
        
        # CRITICAL: Store orchestrator reference for project name flow
        self.orchestrator = None
        self.updated_project_name = None  # Direct storage
        
        # NEW: Store user selections from dropdowns
        self.user_selections = {
            'account_code': None,
            'platform_code': None, 
            'processing_mode': None,
            'project_name': None
        }
        
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference for complete project name flow"""
        self.orchestrator = orchestrator
        print(f"🔗 DIALOG CONTROLLER: Orchestrator reference set")
        
        # Also pass reference to confirmation tab when it's created
        if hasattr(self, 'tab_manager') and self.tab_manager:
            if hasattr(self.tab_manager, 'confirmation_tab') and self.tab_manager.confirmation_tab:
                self.tab_manager.confirmation_tab.set_orchestrator(orchestrator)
                self.tab_manager.confirmation_tab.set_dialog_controller(self)
                print(f"✅ Confirmation tab orchestrator reference updated")
        
        # Store reference on orchestrator too
        if orchestrator:
            orchestrator.dialog_controller = self
            print(f"✅ Orchestrator dialog_controller reference set")
    
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
        """Main entry point - show unified workflow with FIXED project name flow"""
        self.confirmation_data = confirmation_data
        self.processing_callback = processing_callback
        
        print(f"🎬 SHOW_WORKFLOW: Starting with project name: '{confirmation_data.project_name}'")
        
        self._create_dialog()
        return self.result if self.result is not None else False
    
    def _create_dialog(self):
        """Create main dialog window with compact size (10% smaller)"""
        self.root = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.root.title("AI Automation Workflow")
        # CHANGED: Reduced window size by 10%
        self.root.geometry("540x720")  # Was 600x800
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
        
        # CRITICAL: Set orchestrator reference on confirmation tab after creation
        if (hasattr(self.tab_manager, 'confirmation_tab') and 
            self.tab_manager.confirmation_tab and 
            self.orchestrator):
            
            self.tab_manager.confirmation_tab.set_orchestrator(self.orchestrator)
            self.tab_manager.confirmation_tab.set_dialog_controller(self)
            print(f"✅ Confirmation tab references set after creation")
        
        self.tab_manager.show_tab(0)  # Start with confirmation
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.wait_window()
    
    def _initialize_managers(self):
        """Initialize all component managers"""
        self.tab_manager = TabManager(self)
        self.processing_manager = ProcessingThreadManager(self)
        # REMOVED: NotificationManager since we're removing notification icons
        # self.notification_manager = NotificationManager(self, self.theme)
    
    def _center_window(self):
        """Center dialog on screen with compact size"""
        self.root.update_idletasks()
        # CHANGED: Use new compact dimensions
        width = 540  # Was 600
        height = 720  # Was 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_header(self):
        """Create header with title only (NO notification icons)"""
        header_frame = ttk.Frame(self.root, style='White.TFrame')
        # CHANGED: Reduced padding
        header_frame.pack(fill=tk.X, padx=36, pady=(25, 0))  # Was padx=40, pady=(30, 0)
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack(fill=tk.X)
        
        # Icon and title with reduced sizes
        icon_label = ttk.Label(title_container, text="🎬", font=('Segoe UI', 22),  # Was 24
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 12))  # Was padx=(0, 15)
        
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(text_frame, text="AI Automation Workflow", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="Confirm → Process → Results", style='Subheader.TLabel').pack(anchor=tk.W)
        
        # REMOVED: Notification icons completely
        # notification_frame = ttk.Frame(title_container, style='White.TFrame')
        # notification_frame.pack(side=tk.RIGHT)
        # self.notification_manager.create_notification_icons(notification_frame)
    
    def _on_confirm(self):
        """Handle confirm button - ENHANCED to capture dropdown selections"""
        print(f"\n🎬 CONFIRM CLICKED - Capturing user selections")
        
        # CRITICAL: Capture any changes from confirmation tab before processing
        if hasattr(self.tab_manager, 'confirmation_tab') and self.tab_manager.confirmation_tab:
            # Get the updated confirmation data with dropdown selections
            updated_data = self.tab_manager.confirmation_tab.get_updated_data()
            
            if updated_data:
                # Track what changed
                changes = []
                
                # Check project name change
                if updated_data.project_name != self.confirmation_data.project_name:
                    changes.append(f"Project: '{self.confirmation_data.project_name}' → '{updated_data.project_name}'")
                    self.user_selections['project_name'] = updated_data.project_name
                
                # Check account change
                if hasattr(updated_data, 'account') and updated_data.account != getattr(self.confirmation_data, 'account', None):
                    changes.append(f"Account: '{getattr(self.confirmation_data, 'account', 'N/A')}' → '{updated_data.account}'")
                    self.user_selections['account_code'] = updated_data.account
                
                # Check platform change
                if hasattr(updated_data, 'platform') and updated_data.platform != getattr(self.confirmation_data, 'platform', None):
                    changes.append(f"Platform: '{getattr(self.confirmation_data, 'platform', 'N/A')}' → '{updated_data.platform}'")
                    self.user_selections['platform_code'] = updated_data.platform
                
                # Check processing mode change
                if hasattr(updated_data, 'processing_mode') and updated_data.processing_mode != getattr(self.confirmation_data, 'processing_mode', None):
                    changes.append(f"Mode: '{getattr(self.confirmation_data, 'processing_mode', 'N/A')}' → '{updated_data.processing_mode}'")
                    self.user_selections['processing_mode'] = updated_data.processing_mode
                
                # Log all changes
                if changes:
                    print(f"🔄 USER SELECTIONS CAPTURED:")
                    for change in changes:
                        print(f"   {change}")
                    
                    # NEW: Apply selections to orchestrator
                    self._apply_selections_to_orchestrator()
                else:
                    print(f"ℹ️ No changes detected from user selections")
                
                # Update our confirmation_data
                self.confirmation_data = updated_data
                print(f"✅ Updated dialog confirmation_data")
            else:
                print(f"⚠️ Could not get updated data from confirmation tab")
        
        # Proceed with tab management
        self.tab_manager.on_confirm_clicked()
    
    def _apply_selections_to_orchestrator(self):
        """NEW: Apply user selections to orchestrator for processing pipeline"""
        if not self.orchestrator:
            print(f"⚠️ No orchestrator reference - selections cannot be applied")
            return
        
        print(f"🔄 APPLYING USER SELECTIONS TO ORCHESTRATOR:")
        
        # Apply project name
        if self.user_selections['project_name']:
            self.orchestrator.updated_project_name = self.user_selections['project_name']
            print(f"   ✅ Project name: {self.user_selections['project_name']}")
        
        # Apply account code
        if self.user_selections['account_code']:
            self.orchestrator.detected_account_code = self.user_selections['account_code']
            self.orchestrator.user_selected_account = self.user_selections['account_code']
            print(f"   ✅ Account code: {self.user_selections['account_code']}")
        
        # Apply platform code
        if self.user_selections['platform_code']:
            self.orchestrator.detected_platform_code = self.user_selections['platform_code']
            self.orchestrator.user_selected_platform = self.user_selections['platform_code']
            print(f"   ✅ Platform code: {self.user_selections['platform_code']}")
        
        # Apply processing mode
        if self.user_selections['processing_mode']:
            self.orchestrator.processing_mode = self.user_selections['processing_mode']
            self.orchestrator.user_selected_mode = self.user_selections['processing_mode']
            print(f"   ✅ Processing mode: {self.user_selections['processing_mode']}")
        
        # Update validator with new account/platform if changed
        if (self.user_selections['account_code'] or self.user_selections['platform_code']) and hasattr(self.orchestrator, 'validator'):
            account = self.user_selections['account_code'] or self.orchestrator.detected_account_code
            platform = self.user_selections['platform_code'] or self.orchestrator.detected_platform_code
            
            self.orchestrator.validator.set_account_platform(account, platform)
            print(f"   🔧 Validator updated with: {account}/{platform}")
        
        # Update project_info if it exists
        if hasattr(self.orchestrator, 'project_info') and self.orchestrator.project_info:
            if self.user_selections['account_code']:
                self.orchestrator.project_info['account_code'] = self.user_selections['account_code']
                self.orchestrator.project_info['detected_account_code'] = self.user_selections['account_code']
            
            if self.user_selections['platform_code']:
                self.orchestrator.project_info['platform_code'] = self.user_selections['platform_code']
                self.orchestrator.project_info['detected_platform_code'] = self.user_selections['platform_code']
            
            print(f"   📊 Project info updated with user selections")
        
        print(f"✅ All user selections applied to orchestrator successfully")
    
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
        
        print(f"🎬 DIALOG CANCELLED")
        self.result = False
        self.root.destroy()
    
    def _on_success_close(self):
        """Handle successful completion"""
        print(f"🎬 DIALOG SUCCESS - CLOSING")
        self.result = True
        self.root.destroy()
    
    def _on_error_close(self):
        """Handle error close"""
        print(f"🎬 DIALOG ERROR - CLOSING")
        self.result = False
        self.root.destroy()