# app/src/automation/workflow_ui_components/theme.py
import tkinter as tk
from tkinter import ttk

class WorkflowTheme:
    """Handles UI theming and styling"""
    
    def __init__(self, root):
        self.root = root
        self.colors = {
            'bg': '#ffffff',
            'accent': '#0078d4',
            'success': '#107c10',
            'warning': '#ff8c00',
            'error': '#d13438',
            'text_primary': '#323130',
            'text_secondary': '#605e5c',
            'border': '#e1dfdd',
            'tab_active': '#ffffff',
            'tab_inactive': '#f8f8f8'
        }
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply pure white Windows 11 theme"""
        self.root.configure(bg=self.colors['bg'])
        
        style = ttk.Style()
        style.configure('White.TFrame', background=self.colors['bg'])
        style.configure('Header.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 18, 'bold'))
        style.configure('Subheader.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 11))
        style.configure('Body.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        style.configure('Accent.TButton', font=('Segoe UI', 11, 'bold'),
                       padding=(25, 12))
        style.configure('Secondary.TButton', font=('Segoe UI', 11),
                       padding=(25, 12))