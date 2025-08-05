# app/src/automation/workflow_dialog/notification_handlers.py
import tkinter as tk
from tkinter import ttk

class NotificationManager:
    """Handles notification settings and popups"""
    
    def __init__(self, dialog_controller, theme):
        self.dialog = dialog_controller
        self.theme = theme
        self.notification_settings = {
            'email': {'enabled': False, 'address': ''},
            'slack': {'enabled': False, 'webhook': ''}
        }
    
    def create_notification_icons(self, parent_frame):
        """Create notification icons in the header"""
        # Slack icon
        slack_icon = ttk.Label(parent_frame, text="💬", font=('Segoe UI', 18),
                              style='Body.TLabel', cursor="hand2")
        slack_icon.pack(side=tk.RIGHT, padx=(0, 10))
        slack_icon.bind("<Button-1>", self._show_slack_popup)
        
        # Email icon
        email_icon = ttk.Label(parent_frame, text="📧", font=('Segoe UI', 18),
                              style='Body.TLabel', cursor="hand2")
        email_icon.pack(side=tk.RIGHT, padx=(0, 5))
        email_icon.bind("<Button-1>", self._show_email_popup)
    
    def _show_email_popup(self, event):
        """Show email notification popup"""
        popup = tk.Toplevel(self.dialog.root)
        popup.title("Email Notifications")
        popup.geometry("400x200")
        popup.resizable(False, False)
        popup.configure(bg=self.theme.colors['bg'])
        
        # Center popup
        popup.transient(self.dialog.root)
        popup.grab_set()
        
        x = self.dialog.root.winfo_x() + 100
        y = self.dialog.root.winfo_y() + 100
        popup.geometry(f"400x200+{x}+{y}")
        
        main_frame = ttk.Frame(popup, style='White.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="📧 Email Notifications", style='Body.TLabel',
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Email settings
        email_var = tk.BooleanVar(value=self.notification_settings['email']['enabled'])
        email_check = ttk.Checkbutton(main_frame, text="Enable email notifications", 
                                     variable=email_var)
        email_check.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(main_frame, text="Email address:", style='Body.TLabel').pack(anchor=tk.W)
        email_entry = ttk.Entry(main_frame, width=40)
        email_entry.pack(fill=tk.X, pady=(5, 20))
        email_entry.insert(0, self.notification_settings['email']['address'] or "your.email@domain.com")
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='White.TFrame')
        button_frame.pack(fill=tk.X)
        
        def save_email():
            self.notification_settings['email']['enabled'] = email_var.get()
            self.notification_settings['email']['address'] = email_entry.get()
            popup.destroy()
        
        ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save", command=save_email).pack(side=tk.RIGHT)
    
    def _show_slack_popup(self, event):
        """Show Slack notification popup"""
        popup = tk.Toplevel(self.dialog.root)
        popup.title("Slack Notifications")
        popup.geometry("400x200")
        popup.resizable(False, False)
        popup.configure(bg=self.theme.colors['bg'])
        
        # Center popup
        popup.transient(self.dialog.root)
        popup.grab_set()
        
        x = self.dialog.root.winfo_x() + 150
        y = self.dialog.root.winfo_y() + 100
        popup.geometry(f"400x200+{x}+{y}")
        
        main_frame = ttk.Frame(popup, style='White.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="💬 Slack Notifications", style='Body.TLabel',
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Slack settings
        slack_var = tk.BooleanVar(value=self.notification_settings['slack']['enabled'])
        slack_check = ttk.Checkbutton(main_frame, text="Enable Slack notifications",
                                     variable=slack_var)
        slack_check.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(main_frame, text="Slack webhook URL:", style='Body.TLabel').pack(anchor=tk.W)
        slack_entry = ttk.Entry(main_frame, width=40)
        slack_entry.pack(fill=tk.X, pady=(5, 20))
        slack_entry.insert(0, self.notification_settings['slack']['webhook'] or "https://hooks.slack.com/...")
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='White.TFrame')
        button_frame.pack(fill=tk.X)
        
        def save_slack():
            self.notification_settings['slack']['enabled'] = slack_var.get()
            self.notification_settings['slack']['webhook'] = slack_entry.get()
            popup.destroy()
        
        ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save", command=save_slack).pack(side=tk.RIGHT)
    
    def get_notification_settings(self):
        """Get current notification settings"""
        return self.notification_settings.copy()