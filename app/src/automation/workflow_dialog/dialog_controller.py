# app/src/automation/workflow_dialog/dialog_controller.py - SIMPLIFIED VERSION

from ..workflow_ui_components.ui_imports import tk, ttk, messagebox
from typing import Callable

from ..workflow_data_models import ConfirmationData
from ..workflow_ui_components import WorkflowTheme
from ..trello_card_popup import TrelloCardPopup

from .tab_management import TabManager
from .processing_thread import ProcessingThreadManager

class UnifiedWorkflowDialog:
    """Main workflow dialog controller - Simplified orchestrator"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.root = None
        self.result = None
        
        # Managers
        self.theme = None
        self.tab_manager = None
        self.processing_manager = None
        
        # Data
        self.confirmation_data = None
        self.processing_callback = None
        self.orchestrator = None
        self.user_selections = {}
        
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference"""
        self.orchestrator = orchestrator
        if orchestrator:
            orchestrator.dialog_controller = self
    
    @staticmethod
    def get_trello_card_id(parent=None, theme=None):
        """Get Trello card ID"""
        popup = TrelloCardPopup(parent, theme)
        return popup.show_popup()
    
    def show_workflow(self, confirmation_data: ConfirmationData, processing_callback: Callable) -> bool:
        """Main entry point"""
        self.confirmation_data = confirmation_data
        self.processing_callback = processing_callback
        
        self._create_dialog()
        return self.result if self.result is not None else False
    
    def _create_dialog(self):
        """Create dialog window and initialize components"""
        # Create window
        self.root = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.root.title("AI Automation Workflow")
        self.root.geometry("540x850")
        self.root.resizable(False, False)
        
        # Setup theme and window
        self.theme = WorkflowTheme(self.root)
        self._setup_window()
        
        # Initialize managers
        self.tab_manager = TabManager(self)
        self.processing_manager = ProcessingThreadManager(self)
        
        # Create UI
        self._create_ui()
        
        # Setup event handlers
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.wait_window()
    
    def _setup_window(self):
        """Setup window properties"""
        self.root.update_idletasks()
        
        # Center window
        width, height = 540, 850
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make modal if has parent
        if self.parent:
            self.root.transient(self.parent)
            self.root.grab_set()
        
        self.root.lift()
        self.root.focus_force()
    
    def _create_ui(self):
        """Create UI components"""
        # Create header
        self._create_header()
        
        # Create tab structure
        self.tab_manager.create_tab_navigation(self.root)
        self.tab_manager.create_content_area(self.root)
        self.tab_manager.initialize_tabs(self.confirmation_data, self.theme)
        
        # Setup references
        if hasattr(self.tab_manager, 'confirmation_tab') and self.tab_manager.confirmation_tab:
            if self.orchestrator:
                self.tab_manager.confirmation_tab.set_orchestrator(self.orchestrator)
            self.tab_manager.confirmation_tab.set_dialog_controller(self)
    
    def _create_header(self):
        """Create header with theme toggle"""
        header_frame = ttk.Frame(self.root, style='White.TFrame')
        header_frame.pack(fill=tk.X, padx=36, pady=(25, 0))
        
        # Icon
        ttk.Label(header_frame, text="🎬", font=('Segoe UI', 22),
                 style='Body.TLabel').pack(side=tk.LEFT, padx=(0, 12))
        
        # Title
        text_frame = ttk.Frame(header_frame, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(text_frame, text="AI Automation Workflow", 
                 style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="Confirm → Process → Results", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
        
        # Theme toggle button container for precise positioning
        theme_container = tk.Frame(header_frame, bg=self.theme.colors['frame_bg'])
        theme_container.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Theme toggle button (sun/moon icon) - center positioned
        self.theme_button = tk.Button(
            theme_container,
            text="🌙" if self.theme.mode == 'light' else "🔆",
            font=('Segoe UI', 16),
            bd=0,
            bg=self.theme.colors['frame_bg'],
            fg=self.theme.colors['text_primary'],
            activebackground=self.theme.colors['frame_bg'],
            activeforeground=self.theme.colors['accent'],
            cursor='hand2',
            command=self._toggle_theme,
            width=3,  # Fixed width for consistent positioning
            height=1  # Fixed height for consistent positioning
        )
        # Use place for exact positioning
        self.theme_button.place(x=0, y=0, width=40, height=32)
        
        # Set container size to match button
        theme_container.config(width=40, height=32)
        theme_container.pack_propagate(False)
        
        # Store container reference for theme updates
        self.theme_container = theme_container
        
        # Add hover animation bindings
        self.theme_button.bind('<Enter>', self._on_theme_button_enter)
        self.theme_button.bind('<Leave>', self._on_theme_button_leave)
    
    def _on_theme_button_enter(self, event):
        """Handle theme button hover enter - scale up with animation"""
        self.theme_button.config(font=('Segoe UI', 18))  # Slightly larger
    
    def _on_theme_button_leave(self, event):
        """Handle theme button hover leave - scale back down"""
        self.theme_button.config(font=('Segoe UI', 16))  # Back to normal
    
    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        # Toggle the theme
        new_mode = self.theme.toggle_theme()
        
        # Update button icon and colors
        self.theme_button.config(
            text="🌙" if new_mode == 'light' else "🔆",
            bg=self.theme.colors['frame_bg'],
            fg=self.theme.colors['text_primary'],
            activebackground=self.theme.colors['frame_bg']
        )
        
        # Update container background
        if hasattr(self, 'theme_container'):
            self.theme_container.config(bg=self.theme.colors['frame_bg'])
        
        # Refresh all tabs to apply new theme
        if hasattr(self.tab_manager, 'refresh_theme'):
            self.tab_manager.refresh_theme()
    
    def _on_confirm(self):
        """Handle confirm - delegate to tab manager"""
        # Get updated data from confirmation tab
        if hasattr(self.tab_manager, 'confirmation_tab'):
            updated_data = self.tab_manager.confirmation_tab.get_updated_data()
            if updated_data:
                self.confirmation_data = updated_data
                self._update_orchestrator(updated_data)
        
        # Start processing
        self.tab_manager.on_confirm_clicked()
    
    def _update_orchestrator(self, data):
        """Update orchestrator with user selections"""
        if not self.orchestrator:
            return
        
        # Let the orchestrator handle the updates
        if hasattr(data, 'account'):
            self.orchestrator.detected_account_code = data.account
        if hasattr(data, 'platform'):
            self.orchestrator.detected_platform_code = data.platform
        if hasattr(data, 'processing_mode'):
            self.orchestrator.processing_mode = data.processing_mode
        if hasattr(data, 'project_name'):
            self.orchestrator.updated_project_name = data.project_name
    
    def _on_cancel(self):
        """Handle cancel"""
        if self.tab_manager.current_tab == 1 and self.processing_manager:
            if not messagebox.askyesno("Cancel Processing", 
                                       "Are you sure you want to cancel?"):
                return
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