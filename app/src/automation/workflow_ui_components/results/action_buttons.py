# app/src/automation/workflow_ui_components/results/action_buttons.py

from ..ui_imports import tk, ttk

class ActionButtons:
    """Handles action button creation with FIXED equal sizing"""
    
    def __init__(self, theme):
        self.theme = theme
    
    def create_success_buttons(self, parent, on_open_folder, on_done):
        """Create success action buttons with FORCED equal sizing"""
        
        # Action Buttons
        button_frame = ttk.Frame(parent, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        # Center the buttons
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        # FORCE equal sizing by using configure after creation
        folder_btn = ttk.Button(button_container, text="📁 Open Output Folder", 
                               style='ResultsButton.TButton',
                               command=on_open_folder)
        folder_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        done_btn = ttk.Button(button_container, text="✅ Done", 
                             style='ResultsButton.TButton',
                             command=on_done)
        done_btn.pack(side=tk.LEFT)
        
        # Make buttons same size as Confirm & Run button, but ensure text fits
        # "📁 Open Output Folder" is ~18 chars, so we need slightly more width
        folder_btn.configure(width=20)  # Slightly larger to prevent text cropping
        done_btn.configure(width=17)    # Match Confirm & Run button size

    
    def create_error_buttons(self, parent, on_copy_error, on_close):
        """Create error action buttons with FIXED equal sizing"""
        
        # Error action buttons
        button_frame = ttk.Frame(parent, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        # Make buttons same size as Confirm & Run button
        copy_btn = ttk.Button(button_container, text="📋 Copy Error Details", 
                             style='Secondary.TButton', command=on_copy_error)
        copy_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        close_btn = ttk.Button(button_container, text="❌ Close", 
                              style='Primary.TButton', command=on_close)
        close_btn.pack(side=tk.LEFT)
        
        # Configure to match Confirm & Run button size (140x32px equivalent)
        copy_btn.configure(width=17)
        close_btn.configure(width=17)
    
    def refresh_theme(self):
        """Refresh theme for action buttons"""
        # The button styles are automatically refreshed when the theme is updated
        pass