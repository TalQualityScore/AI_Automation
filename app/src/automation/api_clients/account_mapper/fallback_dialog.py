# app/src/automation/api_clients/account_mapper/fallback_dialog.py

import tkinter as tk
from tkinter import ttk
from typing import Tuple
import time

class FallbackSelectionDialog:
    """Shows verification dialog when account/platform detection needs confirmation"""
    
    def __init__(self):
        self.account_mapping = {
            'TR': 'Total Restore',
            'BC3': 'Bio Complete 3',
            'OO': 'Olive Oil',
            'MCT': 'MCT',
            'DS': 'Dark Spot',
            'NB': 'Nature\'s Blend',
            'MK': 'Morning Kick',
            'DRC': 'Dermal Repair Complex',
            'PC': 'Phyto Collagen',
            'GD': 'Glucose Defense',
            'MC': 'Morning Complete',
            'PP': 'Pro Plant',
            'SPC': 'Superfood Complete',
            'MA': 'Metabolic Advanced',
            'KA': 'Keto Active',
            'BLR': 'BadLand Ranch',
            'Bio X4': 'Bio X4',
            'Upwellness': 'Upwellness'
        }
        
        self.platform_mapping = {
            'FB': 'Facebook',
            'YT': 'YouTube',
            'IG': 'Instagram',
            'TT': 'TikTok',
            'SNAP': 'Snapchat'  # Fixed: SNAP -> Snapchat
        }
    
    def show_fallback_selection(self, card_title: str, detected_account: str = None, detected_platform: str = None, card_url: str = None) -> Tuple[str, str]:
        """
        Show verification dialog for account/platform confirmation
        
        Args:
            card_title: The Trello card title for context
            detected_account: Previously detected account (if any)
            detected_platform: Previously detected platform (if any)
            card_url: The Trello card URL to display (optional)
            
        Returns:
            Tuple of (selected_account, selected_platform)
        """
        
        print(f"🎬 VERIFICATION DIALOG: Showing for '{card_title}'")
        print(f"🎬 VERIFICATION DIALOG: Detected account='{detected_account}', platform='{detected_platform}'")
        
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        dialog = tk.Toplevel(root)
        dialog.title("⚠️ Verification Required")
        dialog.geometry("500x500")  # INCREASED HEIGHT
        dialog.resizable(False, False)
        dialog.configure(bg='white')
        
        # Center dialog
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 250  # Adjusted for new height
        dialog.geometry(f"500x500+{x}+{y}")
        
        # Make dialog modal and on top
        dialog.attributes('-topmost', True)
        dialog.focus_force()
        
        result = {"account": None, "platform": None, "action": None, "done": False}
        
        # Main frame
        main_frame = tk.Frame(dialog, bg='white', padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = tk.Label(main_frame, text="⚠️ Verification Required", 
                               font=('Segoe UI', 16, 'bold'), bg='white', fg='#d9534f')
        header_label.pack(pady=(0, 15))
        
        # Instruction
        instruction_label = tk.Label(main_frame, 
                                   text="Please verify the account and platform detection:", 
                                   font=('Segoe UI', 11), bg='white', fg='#333')
        instruction_label.pack(pady=(0, 20))
        
        # Card context - show URL instead of title
        if card_url:
            context_text = card_url
            context_prefix = "Card URL: "
        else:
            # Fallback to truncated title if no URL provided
            context_text = card_title[:50] + "..." if len(card_title) > 50 else card_title
            context_prefix = "Card: "
            
        context_label = tk.Label(main_frame, 
                                text=f"{context_prefix}{context_text}", 
                                font=('Segoe UI', 9), bg='white', fg='#666',
                                wraplength=440)
        context_label.pack(pady=(0, 25))
        
        # Selection frame
        selection_frame = tk.Frame(main_frame, bg='white')
        selection_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Account selection
        account_frame = tk.Frame(selection_frame, bg='white')
        account_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(account_frame, text="Account:", font=('Segoe UI', 11, 'bold'), 
                bg='white', fg='#333').pack(anchor=tk.W)
        
        account_var = tk.StringVar()
        account_combo = ttk.Combobox(account_frame, textvariable=account_var, 
                                   font=('Segoe UI', 10), width=40, state='readonly')
        
        # Populate account options
        account_options = []
        for code, name in self.account_mapping.items():
            account_options.append(f"{code} - {name}")
        
        account_combo['values'] = account_options
        account_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Set default account selection
        if detected_account and detected_account in self.account_mapping:
            default_account = f"{detected_account} - {self.account_mapping[detected_account]}"
            account_combo.set(default_account)
        else:
            account_combo.set("TR - Total Restore")  # Default fallback
        
        # Platform selection
        platform_frame = tk.Frame(selection_frame, bg='white')
        platform_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(platform_frame, text="Platform:", font=('Segoe UI', 11, 'bold'), 
                bg='white', fg='#333').pack(anchor=tk.W)
        
        platform_var = tk.StringVar()
        platform_combo = ttk.Combobox(platform_frame, textvariable=platform_var, 
                                     font=('Segoe UI', 10), width=40, state='readonly')
        
        # Populate platform options
        platform_options = []
        for code, name in self.platform_mapping.items():
            platform_options.append(f"{code} - {name}")
        
        platform_combo['values'] = platform_options
        platform_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Set default platform selection
        if detected_platform and detected_platform in self.platform_mapping:
            default_platform = f"{detected_platform} - {self.platform_mapping[detected_platform]}"
            platform_combo.set(default_platform)
        else:
            platform_combo.set("FB - Facebook")  # Default fallback
        
        # Separator
        separator = tk.Frame(main_frame, height=1, bg='#ddd')
        separator.pack(fill=tk.X, pady=(15, 20))
        
        # Button frame - SINGLE APPLY BUTTON ONLY
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(30, 0))
        
        def on_apply():
            """User wants to apply the selected values"""
            account_selection = account_var.get()
            platform_selection = platform_var.get()
            
            if account_selection and platform_selection:
                # Extract codes from "CODE - Name" format
                account_code = account_selection.split(' - ')[0]
                platform_code = platform_selection.split(' - ')[0]
                
                result["account"] = account_code
                result["platform"] = platform_code
                result["action"] = "apply"
                result["done"] = True
                print(f"✅ User applied: {account_code}, {platform_code}")
        
        print("🔍 DEBUG - Creating Apply button...")
        
        # Single Apply button - centered
        apply_btn = tk.Button(button_frame, text="Apply", 
                             bg='#28a745', fg='white', font=('Segoe UI', 12, 'bold'),
                             padx=40, pady=15, command=on_apply, cursor='hand2',
                             relief='flat', borderwidth=0)
        apply_btn.pack(anchor=tk.CENTER)
        
        print("🔍 DEBUG - Apply button created successfully")
        
        # Handle window close (X button) - FORCE USER TO MAKE SELECTION
        def on_window_close():
            # Show warning that they must make a selection
            response = tk.messagebox.askyesno(
                "Selection Required", 
                "You must verify the account and platform to continue.\n\n"
                "Close anyway? This will exit the entire program.",
                default='no'
            )
            
            if response:  # User confirmed they want to exit
                result["account"] = None
                result["platform"] = None
                result["action"] = "exit_program"
                result["done"] = True
                print(f"❌ User chose to exit program instead of selecting")
            else:
                # User cancelled the close - do nothing, keep dialog open
                print(f"🔄 User cancelled close - dialog remains open")
                pass
        
        dialog.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # POLLING APPROACH - works reliably in your environment
        print("🔍 Starting verification dialog polling...")
        start_time = time.time()
        max_wait = 120  # 2 minute timeout
        
        while not result["done"] and (time.time() - start_time) < max_wait:
            try:
                root.update()  # Process events
                time.sleep(0.1)  # Wait 100ms
            except tk.TclError:
                # Dialog was closed
                break
                
        if not result["done"]:
            print("⏰ Verification dialog timed out, using defaults")
            result = {"account": "TR", "platform": "FB", "action": "timeout", "done": True}
            
        # Cleanup
        try:
            dialog.destroy()
        except:
            pass
        try:
            root.destroy()
        except:
            pass
        
        selected_account = result.get("account", "TR")
        selected_platform = result.get("platform", "FB")
        action = result.get("action", "timeout")
        
        print(f"🎯 VERIFICATION RESULT: Account='{selected_account}', Platform='{selected_platform}', Action='{action}'")
        
        return selected_account, selected_platform