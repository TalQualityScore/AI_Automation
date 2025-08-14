# app/src/automation/workflow_ui_components/results_tab.py - MAIN CLASS ONLY

from .ui_imports import tk, ttk
from ..workflow_data_models import ProcessingResult
from .results.success_display import SuccessDisplay
from .results.error_display import ErrorDisplay

class ResultsTab:
    """Main ResultsTab class - delegates to focused components"""
    
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.frame = None
        self.results_content = None
        self.current_result = None
        self.current_callbacks = None
        
        # Initialize display components
        self.success_display = SuccessDisplay(self, theme)
        self.error_display = ErrorDisplay(self, theme)
        
    def create_tab(self):
        """Create results tab content"""
        self.frame = ttk.Frame(self.parent, style='White.TFrame')
        
        self.results_content = ttk.Frame(self.frame, style='White.TFrame')
        self.results_content.pack(fill=tk.BOTH, expand=True)
        
        # Restore results if available
        if self.current_result and self.current_callbacks:
            if self.current_result.success:
                self.show_success_results(
                    self.current_result, 
                    self.current_callbacks['on_open_folder'],
                    self.current_callbacks['on_done']
                )
            else:
                self.show_error_results(
                    self.current_result,
                    self.current_callbacks['on_copy_error'],
                    self.current_callbacks['on_close']
                )
        
        return self.frame
    
    def show_success_results(self, result: ProcessingResult, on_open_folder, on_done):
        """Delegate to success display component"""
        self.current_result = result
        self.current_callbacks = {
            'on_open_folder': on_open_folder,
            'on_done': on_done
        }
        self.success_display.show_results(result, on_open_folder, on_done)
    
    def show_error_results(self, result: ProcessingResult, on_copy_error, on_close):
        """Delegate to error display component"""
        self.current_result = result
        self.current_callbacks = {
            'on_copy_error': on_copy_error,
            'on_close': on_close
        }
        self.error_display.show_results(result, on_copy_error, on_close)
    
    def clear_results(self):
        """Clear the results display"""
        if self.results_content:
            for widget in self.results_content.winfo_children():
                widget.destroy()
        
        self.current_result = None
        self.current_callbacks = None
    
    def get_current_result(self):
        """Get the currently displayed result"""
        return self.current_result
    
    def update_theme(self, new_theme):
        """Update the theme for this tab"""
        self.theme = new_theme
        self.success_display.theme = new_theme
        self.error_display.theme = new_theme
    
    def refresh_theme(self):
        """Refresh theme for results tab"""
        print("DEBUG: refresh_theme() called on ResultsTab")
        if hasattr(self.theme, 'update_widget_theme') and self.frame:
            self.theme.update_widget_theme(self.frame)
        
        # Update display components
        if hasattr(self.success_display, 'refresh_theme'):
            self.success_display.refresh_theme()
        elif hasattr(self.success_display, 'theme'):
            self.success_display.theme = self.theme
            
        if hasattr(self.error_display, 'refresh_theme'):
            self.error_display.refresh_theme()
        elif hasattr(self.error_display, 'theme'):
            self.error_display.theme = self.theme