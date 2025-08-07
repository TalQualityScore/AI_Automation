# app/src/automation/api_clients/account_mapper/user_dialogs.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Tuple
from .config import ACCOUNT_MAPPING, PLATFORM_MAPPING

class UserDialogs:
    """Handles all user dialog interactions for account/platform selection"""
    
    def __init__(self):
        self.account_mapping = ACCOUNT_MAPPING
        self.platform_mapping = PLATFORM_MAPPING
    
    def confirm_with_user(self, concept_name: str, suggested_account: str, suggested_platform: str) -> Tuple[str, str]:
        """Show confirmation dialog for detected values"""
        
        if threading.current_thread() is not threading.main_thread():
            print(f"⚠️ Background thread - cannot show confirmation, using detected values")
            return suggested_account, suggested_platform
        
        root = tk.Tk()
        root.withdraw()
        
        dialog = tk.Toplevel(root)
        dialog.title("Confirm Detection")
        dialog.geometry("550x350")
        dialog.resizable(False, False)
        dialog.configure(bg='white')
        
        # Center dialog
        dialog.transient(root)
        dialog.grab_set()
        
        x = (dialog.winfo_screenwidth() // 2) - 275
        y = (dialog.winfo_screenheight() // 2) - 175
        dialog.geometry(f"550x350+{x}+{y}")
        
        result = {"confirmed": False, "account": suggested_account, "platform": suggested_platform}
        
        # Main content
        main_frame = tk.Frame(dialog, bg='white', padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = tk.Label(main_frame, text="✅ Confirm Detected Account/Platform", 
                               font=('Segoe UI', 14, 'bold'), bg='white', fg='#107c10')
        header_label.pack(pady=(0, 15))
        
        # Card info
        info_label = tk.Label(main_frame, text=f"Detected from card:", 
                             font=('Segoe UI', 10), bg='white', fg='#605e5c')
        info_label.pack()
        
        card_label = tk.Label(main_frame, text=f"'{concept_name[:70]}...'", 
                             font=('Segoe UI', 10, 'italic'), bg='white', fg='#323130', 
                             wraplength=480)
        card_label.pack(pady=(0, 20))
        
        # Detection display
        detection_frame = tk.Frame(main_frame, bg='#f0f8ff', relief='solid', borderwidth=2)
        detection_frame.pack(fill=tk.X, pady=(0, 25), padx=20)
        
        account_display = self.account_mapping.get(suggested_account, suggested_account)
        platform_display = self.platform_mapping.get(suggested_platform, suggested_platform)
        
        tk.Label(detection_frame, text="DETECTED:", 
                font=('Segoe UI', 10, 'bold'), bg='#f0f8ff', fg='#107c10').pack(pady=(15, 5))
        
        tk.Label(detection_frame, text=f"Account: {suggested_account} ({account_display})", 
                font=('Segoe UI', 12, 'bold'), bg='#f0f8ff', fg='#323130').pack(pady=5)
        tk.Label(detection_frame, text=f"Platform: {suggested_platform} ({platform_display})", 
                font=('Segoe UI', 12, 'bold'), bg='#f0f8ff', fg='#323130').pack(pady=(5, 15))
        
        # Info message
        info_msg = tk.Label(main_frame, 
                           text="Is this detection correct? Click 'Confirm' to proceed or 'Choose Manually' to select different options.", 
                           font=('Segoe UI', 9), bg='white', fg='#605e5c', wraplength=480)
        info_msg.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X)
        
        def on_confirm():
            result["confirmed"] = True
            dialog.destroy()
            root.destroy()
        
        def on_manual():
            result["confirmed"] = False
            dialog.destroy()
            root.destroy()
        
        button_container = tk.Frame(button_frame, bg='white')
        button_container.pack()
        
        manual_btn = tk.Button(button_container, text="❌ Choose Manually", font=('Segoe UI', 10), 
                              bg='#f3f3f3', fg='#323130', relief='flat', borderwidth=1, 
                              padx=25, pady=10, command=on_manual, cursor='hand2')
        manual_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        confirm_btn = tk.Button(button_container, text="✅ Confirm Detection", font=('Segoe UI', 10, 'bold'), 
                               bg='#107c10', fg='white', relief='flat', borderwidth=0, 
                               padx=30, pady=10, command=on_confirm, cursor='hand2')
        confirm_btn.pack(side=tk.RIGHT)
        
        dialog.wait_window()
        
        if result["confirmed"]:
            return suggested_account, suggested_platform
        else:
            # Show manual selection dialog
            return self.show_selection_dialog(concept_name)
    
    def show_selection_dialog(self, concept_name: str) -> Tuple[str, str]:
        """Show user dialog to manually select account and platform"""
        
        if threading.current_thread() is not threading.main_thread():
            print(f"❌ CRITICAL: Dialog called from background thread!")
            return "TR", "FB"
        
        root = tk.Tk()
        root.withdraw()
        
        dialog = tk.Toplevel(root)
        dialog.title("Manual Account & Platform Selection")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        dialog.configure(bg='white')
        
        # Center dialog
        dialog.transient(root)
        dialog.grab_set()
        
        x = (dialog.winfo_screenwidth() // 2) - 300
        y = (dialog.winfo_screenheight() // 2) - 250
        dialog.geometry(f"600x500+{x}+{y}")
        
        result = {"account": None, "platform": None}
        
        # Main content
        main_frame = tk.Frame(dialog, bg='white', padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = tk.Label(main_frame, text="⚠️ Manual Selection Required", 
                               font=('Segoe UI', 14, 'bold'), bg='white', fg='#d13438')
        header_label.pack(pady=(0, 10))
        
        info_label = tk.Label(main_frame, text=f"Could not detect account/platform from:", 
                             font=('Segoe UI', 10), bg='white', fg='#605e5c')
        info_label.pack()
        
        card_label = tk.Label(main_frame, text=f"'{concept_name[:60]}...'", 
                             font=('Segoe UI', 10, 'italic'), bg='white', fg='#323130', wraplength=500)
        card_label.pack(pady=(0, 25))
        
        # Account selection
        account_frame = tk.LabelFrame(main_frame, text="Select Account", font=('Segoe UI', 11, 'bold'), 
                                     bg='white', fg='#323130', padx=15, pady=15)
        account_frame.pack(fill=tk.X, pady=(0, 20))
        
        account_var = tk.StringVar()
        account_options = list(self.account_mapping.keys())
        
        # Create scrollable frame for accounts
        account_scroll_frame = tk.Frame(account_frame, bg='white')
        account_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        for i, account in enumerate(account_options):
            display_name = f"{account} ({self.account_mapping[account]})"
            rb = tk.Radiobutton(account_scroll_frame, text=display_name, variable=account_var, value=account,
                               font=('Segoe UI', 10), bg='white', fg='#323130')
            rb.pack(anchor=tk.W, pady=3)
            if i == 0:  # Select first option by default
                account_var.set(account)
        
        # Platform selection
        platform_frame = tk.LabelFrame(main_frame, text="Select Platform", font=('Segoe UI', 11, 'bold'), 
                                      bg='white', fg='#323130', padx=15, pady=15)
        platform_frame.pack(fill=tk.X, pady=(0, 25))
        
        platform_var = tk.StringVar(value="FB")  # Default to Facebook
        platform_options = [
            ("FB", "Facebook"),
            ("YT", "YouTube"), 
            ("IG", "Instagram"),
            ("TT", "TikTok"),
            ("SNAP", "Snapchat")  # FIXED: Include Snapchat
        ]
        
        platform_scroll_frame = tk.Frame(platform_frame, bg='white')
        platform_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        for code, name in platform_options:
            rb = tk.Radiobutton(platform_scroll_frame, text=f"{code} ({name})", variable=platform_var, value=code,
                               font=('Segoe UI', 10), bg='white', fg='#323130')
            rb.pack(anchor=tk.W, pady=3)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def on_confirm():
            if account_var.get() and platform_var.get():
                result["account"] = account_var.get()
                result["platform"] = platform_var.get()
                dialog.destroy()
                root.destroy()
            else:
                messagebox.showerror("Selection Required", "Please select both account and platform.")
        
        def on_cancel():
            # Emergency defaults if user cancels
            result["account"] = "TR"
            result["platform"] = "FB"
            dialog.destroy()
            root.destroy()
        
        button_container = tk.Frame(button_frame, bg='white')
        button_container.pack()
        
        cancel_btn = tk.Button(button_container, text="❌ Cancel", font=('Segoe UI', 10), 
                              bg='#f3f3f3', fg='#323130', relief='flat', borderwidth=1, 
                              padx=25, pady=10, command=on_cancel, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        confirm_btn = tk.Button(button_container, text="✅ Confirm Selection", font=('Segoe UI', 10, 'bold'), 
                               bg='#0078d4', fg='white', relief='flat', borderwidth=0, 
                               padx=30, pady=10, command=on_confirm, cursor='hand2')
        confirm_btn.pack(side=tk.RIGHT)
        
        dialog.wait_window()
        
        return result.get("account", "TR"), result.get("platform", "FB")