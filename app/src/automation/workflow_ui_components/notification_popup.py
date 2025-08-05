# app/src/automation/workflow_ui_components/notification_popup.py
import tkinter as tk
from tkinter import ttk

class NotificationPopup:
    """Handles notification settings popup"""
    
    def __init__(self, parent, current_settings, theme):
        self.parent = parent
        self.current_settings = current_settings
        self.theme = theme
        self.popup = None
        self.email_var = None
        self.slack_var = None
        self.email_entry = None
        self.slack_entry = None
    
    def show_popup(self):
        """Show notification settings popup"""
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Notification Settings")
        self.popup.geometry("400x250")
        self.popup.resizable(False, False)
        self.popup.configure(bg=self.theme.colors['bg'])
        
        # Center popup
        self.popup.transient(self.parent)
        self.popup.grab_set()
        
        x = self.parent.winfo_x() + 100
        y = self.parent.winfo_y() + 100
        self.popup.geometry(f"400x250+{x}+{y}")
        
        main_frame = ttk.Frame(self.popup, style='White.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="📧 Notification Settings", style='Body.TLabel',
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Email notification
        email_frame = ttk.Frame(main_frame, style='White.TFrame')
        email_frame.pack(fill=tk.X, pady=10)
        
        self.email_var = tk.BooleanVar(value=self.current_settings['email']['enabled'])
        email_check = ttk.Checkbutton(email_frame, text="Email notification", 
                                     variable=self.email_var)
        email_check.pack(anchor=tk.W)
        
        self.email_entry = ttk.Entry(email_frame, width=35)
        self.email_entry.pack(fill=tk.X, pady=(5, 0))
        self.email_entry.insert(0, self.current_settings['email']['address'] or "your.email@domain.com")
        
        # Slack notification  
        slack_frame = ttk.Frame(main_frame, style='White.TFrame')
        slack_frame.pack(fill=tk.X, pady=10)
        
        self.slack_var = tk.BooleanVar(value=self.current_settings['slack']['enabled'])
        slack_check = ttk.Checkbutton(slack_frame, text="Slack notification",
                                     variable=self.slack_var)
        slack_check.pack(anchor=tk.W)
        
        self.slack_entry = ttk.Entry(slack_frame, width=35)
        self.slack_entry.pack(fill=tk.X, pady=(5, 0))
        self.slack_entry.insert(0, self.current_settings['slack']['webhook'] or "slack-webhook-url")
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='White.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.popup.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save", command=self._save_settings).pack(side=tk.RIGHT)
    
    def _save_settings(self):
        """Save notification settings and close popup"""
        self.current_settings['email']['enabled'] = self.email_var.get()
        self.current_settings['email']['address'] = self.email_entry.get()
        self.current_settings['slack']['enabled'] = self.slack_var.get()  
        self.current_settings['slack']['webhook'] = self.slack_entry.get()
        self.popup.destroy()