# app/src/automation/api_clients/account_mapper/fallback_dialog.py

import tkinter as tk
from tkinter import ttk
from typing import Tuple
from .config import ACCOUNT_MAPPING, PLATFORM_MAPPING

class FallbackSelectionDialog:
    """Shows fallback dialog when helpers receive UNKNOWN account/platform"""
    
    def __init__(self):
        self.account_mapping = ACCOUNT_MAPPING
        self.platform_mapping = PLATFORM_MAPPING
    
    def show_fallback_selection(self, card_title: str, detected_account: str = None, detected_platform: str = None) -> Tuple[str, str]:
        """
        Show fallback selection dialog when helpers get UNKNOWN values
        
        Args:
            card_title: The Trello card title for context
            detected_account: Previously detected account (if any)
            detected_platform: Previously detected platform (if any)
            
        Returns:
            Tuple of (selected_account, selected_platform)
        """
        
        root = tk.Tk()
        root.withdraw()
        
        dialog = tk.Toplevel(root)
        dialog.title("⚠️ Account/Platform Selection Required")
        dialog.geometry("650x550")
        dialog.resizable(False, False)
        dialog.configure(bg='white')
        
        # Center dialog
        dialog.transient(root)
        dialog.grab_set()
        
        x = (dialog.winfo_screenwidth() // 2) - 325
        y = (dialog.winfo_screenheight() // 2) - 275
        dialog.geometry(f"650x550+{x}+{y}")
        
        # Make dialog modal and on top
        dialog.attributes('-topmost', True)
        dialog.focus_force()
        
        result = {"account": None, "platform": None, "confirmed": False}
        
        # Main content
        main_frame = tk.Frame(dialog, bg='white', padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with warning
        header_frame = tk.Frame(main_frame, bg='#fff3cd', relief='solid', borderwidth=2)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        warning_label = tk.Label(header_frame, text="⚠️ MANUAL SELECTION REQUIRED", 
                               font=('Segoe UI', 14, 'bold'), bg='#fff3cd', fg='#856404')
        warning_label.pack(pady=15)
        
        # Problem description
        problem_label = tk.Label(main_frame, 
                                text="The system couldn't determine the correct account and platform automatically.", 
                                font=('Segoe UI', 11), bg='white', fg='#d73527', wraplength=580)
        problem_label.pack(pady=(0, 10))
        
        # Card info
        card_frame = tk.LabelFrame(main_frame, text="Trello Card", font=('Segoe UI', 10, 'bold'), 
                                  bg='white', fg='#323130', padx=15, pady=10)
        card_frame.pack(fill=tk.X, pady=(0, 20))
        
        card_text = tk.Text(card_frame, height=3, wrap=tk.WORD, font=('Segoe UI', 9), 
                           bg='#f8f9fa', relief='flat', borderwidth=0)
        card_text.pack(fill=tk.X)
        card_text.insert('1.0', card_title)
        card_text.config(state='disabled')
        
        # Detection status (if any)
        if detected_account or detected_platform:
            status_frame = tk.LabelFrame(main_frame, text="Previous Detection", font=('Segoe UI', 10, 'bold'), 
                                       bg='white', fg='#323130', padx=15, pady=10)
            status_frame.pack(fill=tk.X, pady=(0, 20))
            
            status_text = f"Account: {detected_account or 'UNKNOWN'} | Platform: {detected_platform or 'UNKNOWN'}"
            status_label = tk.Label(status_frame, text=status_text, font=('Segoe UI', 10), 
                                  bg='white', fg='#6c757d')
            status_label.pack()
        
        # Selection area
        selection_frame = tk.Frame(main_frame, bg='white')
        selection_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Account selection
        account_frame = tk.LabelFrame(selection_frame, text="📋 Select Account", font=('Segoe UI', 11, 'bold'), 
                                     bg='white', fg='#323130', padx=15, pady=15)
        account_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        account_var = tk.StringVar()
        
        # Create scrollable frame for accounts
        account_canvas = tk.Canvas(account_frame, bg='white', height=200)
        account_scrollbar = ttk.Scrollbar(account_frame, orient=tk.VERTICAL, command=account_canvas.yview)
        account_scroll_frame = tk.Frame(account_canvas, bg='white')
        
        account_scroll_frame.bind(
            "<Configure>",
            lambda e: account_canvas.configure(scrollregion=account_canvas.bbox("all"))
        )
        
        account_canvas.create_window((0, 0), window=account_scroll_frame, anchor="nw")
        account_canvas.configure(yscrollcommand=account_scrollbar.set)
        
        account_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        account_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add account options
        account_options = list(self.account_mapping.keys())
        for i, account in enumerate(account_options):
            display_name = f"{account} ({self.account_mapping[account]})"
            rb = tk.Radiobutton(account_scroll_frame, text=display_name, variable=account_var, value=account,
                               font=('Segoe UI', 10), bg='white', fg='#323130', wraplength=200)
            rb.pack(anchor=tk.W, pady=3, padx=5)
            
            # Set default selection
            if i == 0 or (detected_account and account == detected_account):
                account_var.set(account)
        
        # Platform selection
        platform_frame = tk.LabelFrame(selection_frame, text="🌐 Select Platform", font=('Segoe UI', 11, 'bold'), 
                                      bg='white', fg='#323130', padx=15, pady=15)
        platform_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        platform_var = tk.StringVar()
        platform_options = [
            ("FB", "Facebook"),
            ("YT", "YouTube"), 
            ("IG", "Instagram"),
            ("TT", "TikTok"),
            ("SNAP", "Snapchat")
        ]
        
        # Add platform options
        for code, name in platform_options:
            rb = tk.Radiobutton(platform_frame, text=f"{code} ({name})", variable=platform_var, value=code,
                               font=('Segoe UI', 10), bg='white', fg='#323130')
            rb.pack(anchor=tk.W, pady=5, padx=5)
            
            # Set default selection
            if code == "FB" or (detected_platform and code == detected_platform):
                platform_var.set(code)
        
        # Bottom instruction
        instruction_label = tk.Label(main_frame, 
                                   text="Please select the correct account and platform, then click 'Confirm Selection' to continue.", 
                                   font=('Segoe UI', 10), bg='white', fg='#6c757d', wraplength=580)
        instruction_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X)
        
        def on_confirm():
            if account_var.get() and platform_var.get():
                result["account"] = account_var.get()
                result["platform"] = platform_var.get()
                result["confirmed"] = True
                dialog.destroy()
                root.destroy()
            else:
                tk.messagebox.showerror("Selection Required", 
                                      "Please select both account and platform before confirming.")
        
        def on_cancel():
            # Use safe defaults if user cancels
            result["account"] = "TR"
            result["platform"] = "FB"
            result["confirmed"] = False
            dialog.destroy()
            root.destroy()
        
        button_container = tk.Frame(button_frame, bg='white')
        button_container.pack()
        
        cancel_btn = tk.Button(button_container, text="❌ Use Defaults (TR-FB)", font=('Segoe UI', 10), 
                              bg='#6c757d', fg='white', relief='flat', borderwidth=0, 
                              padx=25, pady=12, command=on_cancel, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        confirm_btn = tk.Button(button_container, text="✅ Confirm Selection", font=('Segoe UI', 11, 'bold'), 
                               bg='#28a745', fg='white', relief='flat', borderwidth=0, 
                               padx=30, pady=12, command=on_confirm, cursor='hand2')
        confirm_btn.pack(side=tk.RIGHT)
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            account_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        account_canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Wait for user selection
        dialog.wait_window()
        
        selected_account = result.get("account", "TR")
        selected_platform = result.get("platform", "FB")
        
        print(f"🎯 FALLBACK SELECTION: Account='{selected_account}', Platform='{selected_platform}', Confirmed={result['confirmed']}")
        
        return selected_account, selected_platform