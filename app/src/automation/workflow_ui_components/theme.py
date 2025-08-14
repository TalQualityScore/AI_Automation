# app/src/automation/workflow_ui_components/theme.py
from .ui_imports import tk, ttk
import json
import os

class WorkflowTheme:
    """Handles UI theming and styling with dark/light mode support"""
    
    def __init__(self, root, initial_mode=None):
        self.root = root
        self.mode = initial_mode or self.load_theme_preference()
        self.theme_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'theme_settings.json')
        
        # Light mode colors (keeping as-is with blue CONFIRM & RUN button)
        self.light_colors = {
            'bg': '#ffffff',
            'frame_bg': '#ffffff',
            'accent': '#0078d4',  # Blue for CONFIRM & RUN button
            'success': '#107c10',
            'warning': '#ff8c00',
            'error': '#d13438',
            'text_primary': '#323130',
            'text_secondary': '#605e5c',
            'border': '#e1dfdd',
            'tab_active': '#ffffff',
            'tab_inactive': '#f8f8f8',
            'entry_bg': '#ffffff',
            'entry_fg': '#323130',
            'button_bg': '#f3f2f1',
            'button_fg': '#323130',
            'button_hover': '#e1dfdd',
            'combo_bg': '#ffffff',
            'checkbox_bg': '#ffffff',
            'scrollbar_bg': '#f3f2f1',
            'scrollbar_thumb': '#c8c6c4',
            'confirm_button': '#0078d4',  # Blue CONFIRM & RUN button
            'field_label': '#000000'  # Field labels - always black
        }
        
        # Dark mode colors (simplified - single #232323 color)
        self.dark_colors = {
            'bg': '#232323',  # Single background color
            'frame_bg': '#232323',  # Same color for panels/containers
            'accent': '#0078d4',  # Blue for CONFIRM & RUN button (same as light)
            'success': '#4ec9b0',
            'warning': '#ce9178',
            'error': '#f48771',
            'text_primary': '#ffffff',  # White text for good contrast
            'text_secondary': '#cccccc',  # Lighter secondary text
            'border': '#444444',
            'tab_active': '#1a1a1a',  # Darker tab for active (darker than #232323)
            'tab_inactive': '#2a2a2a',  # Slightly brighter than #232323 for inactive
            'entry_bg': '#232323',  # Entry fields same as background
            'entry_fg': '#000000',  # Black text in entry fields
            'button_bg': '#232323',
            'button_fg': '#ffffff',
            'button_hover': '#333333',
            'combo_bg': '#232323',
            'combo_fg': '#000000',  # Black text in comboboxes
            'checkbox_bg': '#232323',
            'scrollbar_bg': '#232323',
            'scrollbar_thumb': '#444444',
            'confirm_button': '#0078d4',  # Blue CONFIRM & RUN button
            'field_label': '#000000',  # Field labels - always black
            'cancel_button_bg': '#ffffff',  # Cancel button: WHITE fill
            'cancel_button_fg': '#000000',  # Cancel button: BLACK text
            'icon_area_bg': '#232323',  # Area around theme icon: same color
            'special_text': '#ffffff'  # For specific text that needs to be white
        }
        
        # Set initial colors
        self.colors = self.dark_colors if self.mode == 'dark' else self.light_colors
        
        # Track theme change callbacks
        self.theme_change_callbacks = []
        
        # Apply initial theme
        self._apply_theme()
    
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.mode = 'dark' if self.mode == 'light' else 'light'
        self.colors = self.dark_colors if self.mode == 'dark' else self.light_colors
        self._apply_theme()
        self.save_theme_preference()
        
        # Notify all registered callbacks
        for callback in self.theme_change_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in theme callback: {e}")
        
        return self.mode
    
    def register_theme_callback(self, callback):
        """Register a callback to be called when theme changes"""
        if callback not in self.theme_change_callbacks:
            self.theme_change_callbacks.append(callback)
    
    def unregister_theme_callback(self, callback):
        """Unregister a theme callback"""
        if callback in self.theme_change_callbacks:
            self.theme_change_callbacks.remove(callback)
    
    def _apply_theme(self):
        """Apply theme to all widgets"""
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Frame styles
        style.configure('White.TFrame', background=self.colors['frame_bg'])
        style.configure('TFrame', background=self.colors['frame_bg'])
        
        # Label styles
        style.configure('Header.TLabel', 
                       background=self.colors['frame_bg'],  # Use frame_bg for panels
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 18, 'bold'))
        
        style.configure('Subheader.TLabel', 
                       background=self.colors['frame_bg'],  # Use frame_bg for panels
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 11))
        
        style.configure('Body.TLabel', 
                       background=self.colors['frame_bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        
        style.configure('TLabel', 
                       background=self.colors['frame_bg'],
                       foreground=self.colors['text_primary'])
        
        # Field labels (Project/Account/Platform/Processing) - special color in dark mode
        style.configure('FieldLabel.TLabel',
                       background=self.colors['frame_bg'],
                       foreground=self.colors.get('field_label', self.colors['text_primary']),
                       font=('Segoe UI', 11, 'bold'))
        
        # Special text that needs to be white in dark mode
        style.configure('SpecialText.TLabel',
                       background=self.colors['frame_bg'],
                       foreground=self.colors.get('special_text', self.colors['text_secondary']),
                       font=('Segoe UI', 9, 'italic'))
        
        # Button styles
        style.configure('Accent.TButton', 
                       font=('Segoe UI', 11, 'bold'),
                       padding=(25, 12),
                       foreground=self.colors['button_fg'] if self.mode == 'dark' else self.colors['text_primary'])
        
        style.configure('Secondary.TButton', 
                       font=('Segoe UI', 11),
                       padding=(25, 12),
                       foreground=self.colors['button_fg'] if self.mode == 'dark' else self.colors['text_primary'])
        
        style.configure('TButton',
                       foreground=self.colors['button_fg'] if self.mode == 'dark' else self.colors['text_primary'])
        
        # CONFIRM & RUN button - BLUE in both modes
        style.configure('ConfirmButton.TButton',
                       background=self.colors['confirm_button'],  # Blue in both modes
                       foreground='white',  # White text on blue
                       font=('Segoe UI', 11, 'bold'),
                       padding=(25, 12))
        style.map('ConfirmButton.TButton',
                 background=[('active', '#005a9e')],  # Darker blue on hover
                 foreground=[('active', 'white')])
        
        # Special cancel button style for dark mode
        if self.mode == 'dark':
            style.configure('CancelButton.TButton',
                           background=self.colors['cancel_button_bg'],
                           foreground=self.colors['cancel_button_fg'],
                           font=('Segoe UI', 11),
                           padding=(25, 12))
            style.map('CancelButton.TButton',
                     background=[('active', '#f0f0f0')],  # Slightly darker white on hover
                     foreground=[('active', self.colors['cancel_button_fg'])])
        else:
            # In light mode, use normal secondary style
            style.configure('CancelButton.TButton',
                           font=('Segoe UI', 11),
                           padding=(25, 12))
        
        # Results tab buttons - BLACK text in dark mode
        if self.mode == 'dark':
            style.configure('ResultsButton.TButton',
                           background=self.colors['button_bg'],
                           foreground='#000000',  # BLACK text per requirements
                           font=('Segoe UI', 11),
                           padding=(25, 12))
            style.map('ResultsButton.TButton',
                     background=[('active', self.colors['button_hover'])],
                     foreground=[('active', '#000000')])
        else:
            # In light mode, use normal styling
            style.configure('ResultsButton.TButton',
                           font=('Segoe UI', 11),
                           padding=(25, 12))
        
        # Entry styles
        style.configure('TEntry',
                       fieldbackground=self.colors['entry_bg'],
                       foreground=self.colors['entry_fg'],
                       insertcolor=self.colors['text_primary'],
                       bordercolor=self.colors['border'])
        
        # Force entry text color in dark mode
        if self.mode == 'dark':
            style.map('TEntry',
                     fieldbackground=[('readonly', self.colors['entry_bg'])],
                     foreground=[('readonly', self.colors['entry_fg']),
                                ('active', self.colors['entry_fg']),
                                ('focus', self.colors['entry_fg']),
                                ('!disabled', self.colors['entry_fg'])])
        else:
            style.map('TEntry',
                     fieldbackground=[('readonly', self.colors['entry_bg'])],
                     foreground=[('readonly', self.colors['entry_fg'])])
        
        # Combobox styles
        combo_fg = self.colors.get('combo_fg', self.colors['entry_fg'])
        style.configure('TCombobox',
                       fieldbackground=self.colors['combo_bg'],
                       foreground=combo_fg,
                       selectbackground=self.colors['accent'],
                       selectforeground='white',
                       bordercolor=self.colors['border'])
        
        # Force combobox text visibility in dark mode
        if self.mode == 'dark':
            style.map('TCombobox',
                     fieldbackground=[('readonly', self.colors['combo_bg']),
                                    ('focus', self.colors['combo_bg']),
                                    ('active', self.colors['combo_bg'])],
                     foreground=[('readonly', self.colors['combo_fg']),
                               ('focus', self.colors['combo_fg']), 
                               ('active', self.colors['combo_fg']),
                               ('!disabled', self.colors['combo_fg'])],
                     selectbackground=[('readonly', self.colors['accent']),
                                     ('focus', self.colors['accent'])],
                     selectforeground=[('readonly', 'white'),
                                     ('focus', 'white')])
        else:
            style.map('TCombobox',
                     fieldbackground=[('readonly', self.colors['combo_bg'])],
                     selectbackground=[('readonly', self.colors['accent'])],
                     selectforeground=[('readonly', 'white')])
        
        # Checkbutton styles
        style.configure('TCheckbutton',
                       background=self.colors['frame_bg'],
                       foreground=self.colors['text_primary'])
        
        # Radiobutton styles
        style.configure('TRadiobutton',
                       background=self.colors['frame_bg'],
                       foreground=self.colors['text_primary'])
        
        # Notebook (tab) styles
        style.configure('TNotebook',
                       background=self.colors['bg'],
                       borderwidth=0)
        
        style.configure('TNotebook.Tab',
                       background=self.colors['tab_inactive'],
                       foreground=self.colors['text_primary'],
                       padding=[20, 10])
        
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['tab_active'])],
                 foreground=[('selected', self.colors['text_primary'])])
        
        # Scrollbar styles
        style.configure('Vertical.TScrollbar',
                       background=self.colors['scrollbar_bg'],
                       troughcolor=self.colors['scrollbar_bg'],
                       bordercolor=self.colors['scrollbar_bg'],
                       arrowcolor=self.colors['scrollbar_thumb'],
                       darkcolor=self.colors['scrollbar_bg'],
                       lightcolor=self.colors['scrollbar_bg'])
        
        style.map('Vertical.TScrollbar',
                 background=[('active', self.colors['scrollbar_thumb'])])
        
        # Text widget configuration (for results display)
        for widget in self.root.winfo_children():
            self._apply_theme_to_widget(widget)
    
    def _apply_theme_to_widget(self, widget):
        """Recursively apply theme to widget and its children"""
        try:
            # Handle Text widgets
            if isinstance(widget, tk.Text):
                widget.configure(
                    bg=self.colors['entry_bg'],
                    fg=self.colors['text_primary'],
                    insertbackground=self.colors['text_primary'],
                    selectbackground=self.colors['accent'],
                    selectforeground='white'
                )
            # Handle Listbox widgets
            elif isinstance(widget, tk.Listbox):
                widget.configure(
                    bg=self.colors['entry_bg'],
                    fg=self.colors['text_primary'],
                    selectbackground=self.colors['accent'],
                    selectforeground='white'
                )
            # Handle Canvas widgets
            elif isinstance(widget, tk.Canvas):
                widget.configure(bg=self.colors['bg'])
            # Handle regular Frame widgets
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=self.colors['frame_bg'])
            # Handle regular Label widgets
            elif isinstance(widget, tk.Label):
                widget.configure(
                    bg=self.colors['frame_bg'],
                    fg=self.colors['text_primary']
                )
            # Handle regular Button widgets
            elif isinstance(widget, tk.Button):
                widget.configure(
                    bg=self.colors['button_bg'],
                    fg=self.colors['button_fg'],
                    activebackground=self.colors['button_hover'],
                    activeforeground=self.colors['button_fg']
                )
        except tk.TclError:
            pass  # Some widgets might not support all options
        
        # Recursively apply to children
        for child in widget.winfo_children():
            self._apply_theme_to_widget(child)
    
    def get_mode(self):
        """Get current theme mode"""
        return self.mode
    
    def save_theme_preference(self):
        """Save theme preference to file"""
        try:
            settings = {'theme_mode': self.mode}
            os.makedirs(os.path.dirname(self.theme_file), exist_ok=True)
            with open(self.theme_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Could not save theme preference: {e}")
    
    def load_theme_preference(self):
        """Load theme preference from file"""
        try:
            if os.path.exists(self.theme_file):
                with open(self.theme_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('theme_mode', 'light')
        except Exception as e:
            print(f"Could not load theme preference: {e}")
        return 'light'  # Default to light mode
    
    def update_widget_theme(self, widget):
        """Update theme for a specific widget and its children"""
        self._apply_theme_to_widget(widget)
    
    @classmethod
    def create_for_standalone_window(cls, window):
        """Create and apply theme to a standalone window"""
        current_mode = cls.load_current_theme_mode()
        theme = cls(window, current_mode)
        return theme
    
    @classmethod
    def load_current_theme_mode(cls):
        """Load the current theme mode from settings"""
        try:
            theme_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'theme_settings.json')
            if os.path.exists(theme_file):
                with open(theme_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('theme_mode', 'light')
        except Exception:
            pass
        return 'light'  # Default to light mode
    
    @classmethod 
    def get_current_colors(cls):
        """Get current theme colors without creating a theme object"""
        current_mode = cls.load_current_theme_mode()
        
        # Use the actual color definitions from this class
        dummy_theme = cls.__new__(cls)  # Create instance without __init__
        dummy_theme.mode = current_mode
        dummy_theme.light_colors = {
            'bg': '#ffffff',
            'frame_bg': '#ffffff',
            'accent': '#0078d4',
            'text_primary': '#323130',
            'text_secondary': '#605e5c',
        }
        dummy_theme.dark_colors = {
            'bg': '#232323',
            'frame_bg': '#232323', 
            'accent': '#0078d4',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
        }
        dummy_theme.colors = dummy_theme.dark_colors if current_mode == 'dark' else dummy_theme.light_colors
        return dummy_theme.colors