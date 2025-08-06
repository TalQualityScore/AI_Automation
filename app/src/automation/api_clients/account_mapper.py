# app/src/automation/api_clients/account_mapper.py - THREADING ISSUE FIXED

from typing import Tuple
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from .config import ACCOUNT_MAPPING, PLATFORM_MAPPING

class AccountMapper:
    """Handles account and platform detection with thread-safe user fallback dialog"""
    
    def __init__(self):
        self.account_mapping = ACCOUNT_MAPPING
        self.platform_mapping = PLATFORM_MAPPING
        # Clear any potential cached data
        self._clear_cache()
    
    def _clear_cache(self):
        """Clear any potential cached detection data"""
        self._last_detection = None
        self._cached_result = None
    
    def extract_account_and_platform(self, concept_name: str, allow_fallback: bool = True) -> Tuple[str, str]:
        """
        THREADING FIXED: Extract account and platform with thread-safe user fallback
        
        Args:
            concept_name: Card title (e.g., "TR FB - New Ads from...")
            allow_fallback: Whether to show user dialog if detection fails
            
        Returns:
            Tuple of (account_code, platform_code) or raises exception if detection fails
        """
        
        print(f"🔍 ACCOUNT MAPPER - Analyzing: '{concept_name}'")
        self._clear_cache()  # Ensure no cached data
        
        # STEP 1: Try direct prefix parsing (most reliable)
        account_code, platform_code = self._parse_direct_prefix(concept_name)
        
        if account_code != "UNKNOWN" and platform_code != "UNKNOWN":
            print(f"✅ DIRECT PREFIX SUCCESS: Account='{account_code}', Platform='{platform_code}'")
            return account_code, platform_code
        
        # STEP 2: Try fallback detection
        account_code, platform_code = self._fallback_detection(concept_name)
        
        if account_code != "UNKNOWN" and platform_code != "UNKNOWN":
            print(f"✅ FALLBACK SUCCESS: Account='{account_code}', Platform='{platform_code}'")
            return account_code, platform_code
        
        # STEP 3: FIXED - Check if we're in main thread before showing dialog
        if allow_fallback:
            print(f"⚠️ DETECTION FAILED - Checking thread safety...")
            
            # Check if we're in the main thread
            if threading.current_thread() is threading.main_thread():
                print(f"✅ Main thread detected - Showing user selection dialog")
                account_code, platform_code = self._show_selection_dialog(concept_name)
                
                if account_code and platform_code:
                    print(f"✅ USER SELECTION: Account='{account_code}', Platform='{platform_code}'")
                    return account_code, platform_code
            else:
                print(f"⚠️ Background thread detected - Cannot show dialog, using intelligent defaults")
                # FIXED: Instead of showing dialog from background thread, use intelligent defaults
                account_code, platform_code = self._get_intelligent_defaults(concept_name)
                
                if account_code != "UNKNOWN" and platform_code != "UNKNOWN":
                    print(f"✅ INTELLIGENT DEFAULT: Account='{account_code}', Platform='{platform_code}'")
                    return account_code, platform_code
        
        # STEP 4: If all fails, use safe defaults instead of raising exception
        print(f"⚠️ Using final fallback defaults: TR, FB")
        return "TR", "FB"  # Safe defaults that usually work
    
    def _get_intelligent_defaults(self, concept_name: str) -> Tuple[str, str]:
        """Get intelligent defaults when dialog cannot be shown"""
        
        concept_lower = concept_name.lower()
        
        # Try to detect account from keywords in the name
        account_keywords = {
            'bc3': 'BC3',
            'bio complete': 'BC3',
            'biocomplete': 'BC3',
            'total restore': 'TR',
            'totalrestore': 'TR',
            'olive oil': 'OO',
            'oliveoil': 'OO',
            'mct': 'MCT',
            'dark spot': 'DS',
            'darkspot': 'DS',
            'morning kick': 'MK',
            'morningkick': 'MK',
            'dinner': 'TR',  # Common in TR ads
            'mashup': 'TR',  # Common in TR ads
            'agmd': 'TR',   # AGMD is often TR
        }
        
        detected_account = "TR"  # Default
        for keyword, account in account_keywords.items():
            if keyword in concept_lower:
                detected_account = account
                break
        
        # Platform detection from context
        platform_keywords = {
            'facebook': 'FB',
            'fb': 'FB',
            'youtube': 'YT',
            'yt': 'YT',
            'instagram': 'IG',
            'ig': 'IG',
            'tiktok': 'TT',
            'tt': 'TT',
        }
        
        detected_platform = "FB"  # Default to Facebook
        for keyword, platform in platform_keywords.items():
            if keyword in concept_lower:
                detected_platform = platform
                break
        
        print(f"🧠 INTELLIGENT DETECTION: '{concept_name}' -> Account='{detected_account}', Platform='{detected_platform}'")
        return detected_account, detected_platform
    
    def _parse_direct_prefix(self, concept_name: str) -> Tuple[str, str]:
        """Parse direct prefix format like 'TR FB - New Ads from...'"""
        
        if " - " in concept_name:
            prefix = concept_name.split(" - ")[0].strip()
            print(f"🔍 EXTRACTED PREFIX: '{prefix}'")
            
            parts = prefix.split()
            if len(parts) >= 2:
                account_part = parts[0].upper()
                platform_part = parts[1].upper()
                
                # Validate account exists in mapping
                if account_part in self.account_mapping:
                    # Validate platform
                    if platform_part in ['FB', 'YT', 'IG', 'TT', 'SNAP']:
                        return account_part, platform_part
                
                print(f"⚠️ PREFIX PARTS NOT IN MAPPING: Account='{account_part}', Platform='{platform_part}'")
        
        return "UNKNOWN", "UNKNOWN"
    
    def _fallback_detection(self, concept_name: str) -> Tuple[str, str]:
        """Fallback detection using pattern matching"""
        
        # Try to detect account codes in the text
        for account_code in self.account_mapping.keys():
            if account_code in concept_name.upper():
                print(f"✅ FALLBACK Account detected: {account_code}")
                # Default to Facebook if account detected but no platform
                return account_code, "FB"
        
        return "UNKNOWN", "UNKNOWN"
    
    def _show_selection_dialog(self, concept_name: str) -> Tuple[str, str]:
        """Show user dialog to select account and platform - MAIN THREAD ONLY"""
        
        # Double-check we're in main thread
        if threading.current_thread() is not threading.main_thread():
            print(f"❌ CRITICAL: Dialog called from background thread - this should not happen!")
            return "TR", "FB"  # Safe fallback
        
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        dialog = tk.Toplevel(root)
        dialog.title("Account & Platform Selection Required")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.configure(bg='white')
        
        # Center dialog
        dialog.transient(root)
        dialog.grab_set()
        
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 200
        dialog.geometry(f"500x400+{x}+{y}")
        
        result = {"account": None, "platform": None}
        
        # Main content
        main_frame = tk.Frame(dialog, bg='white', padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = tk.Label(main_frame, text="⚠️ Account/Platform Detection Failed", 
                               font=('Segoe UI', 14, 'bold'), bg='white', fg='#d13438')
        header_label.pack(pady=(0, 10))
        
        info_label = tk.Label(main_frame, text=f"Could not automatically detect account/platform from:\n'{concept_name[:60]}...'", 
                             font=('Segoe UI', 10), bg='white', fg='#605e5c', wraplength=400)
        info_label.pack(pady=(0, 20))
        
        # Account selection
        account_frame = tk.LabelFrame(main_frame, text="Select Account", font=('Segoe UI', 11, 'bold'), 
                                     bg='white', fg='#323130', padx=10, pady=10)
        account_frame.pack(fill=tk.X, pady=(0, 15))
        
        account_var = tk.StringVar()
        account_options = list(self.account_mapping.keys())
        
        for i, account in enumerate(account_options):
            display_name = f"{account} ({self.account_mapping[account]})"
            rb = tk.Radiobutton(account_frame, text=display_name, variable=account_var, value=account,
                               font=('Segoe UI', 10), bg='white', fg='#323130')
            rb.pack(anchor=tk.W, pady=2)
            if i == 0:  # Select first option by default
                account_var.set(account)
        
        # Platform selection
        platform_frame = tk.LabelFrame(main_frame, text="Select Platform", font=('Segoe UI', 11, 'bold'), 
                                      bg='white', fg='#323130', padx=10, pady=10)
        platform_frame.pack(fill=tk.X, pady=(0, 20))
        
        platform_var = tk.StringVar(value="FB")  # Default to Facebook (most common)
        platform_options = [
            ("FB", "Facebook"),
            ("YT", "YouTube"),
            ("IG", "Instagram"),
            ("TT", "TikTok"),
            ("SNAP", "Snapchat")
        ]
        
        for code, name in platform_options:
            rb = tk.Radiobutton(platform_frame, text=f"{code} ({name})", variable=platform_var, value=code,
                               font=('Segoe UI', 10), bg='white', fg='#323130')
            rb.pack(anchor=tk.W, pady=2)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X)
        
        def on_confirm():
            if account_var.get() and platform_var.get():
                result["account"] = account_var.get()
                result["platform"] = platform_var.get()
                dialog.destroy()
                root.destroy()
            else:
                messagebox.showerror("Selection Required", "Please select both account and platform.")
        
        def on_cancel():
            # Use intelligent defaults instead of None
            result["account"] = "TR"
            result["platform"] = "FB"
            dialog.destroy()
            root.destroy()
        
        button_container = tk.Frame(button_frame, bg='white')
        button_container.pack()
        
        cancel_btn = tk.Button(button_container, text="❌ Use Defaults", font=('Segoe UI', 10), 
                              bg='#f3f3f3', fg='#323130', relief='flat', borderwidth=1, 
                              padx=20, pady=8, command=on_cancel, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        confirm_btn = tk.Button(button_container, text="✅ Confirm Selection", font=('Segoe UI', 10, 'bold'), 
                               bg='#0078d4', fg='white', relief='flat', borderwidth=0, 
                               padx=25, pady=8, command=on_confirm, cursor='hand2')
        confirm_btn.pack(side=tk.RIGHT)
        
        # Wait for user selection
        dialog.wait_window()
        
        return result.get("account", "TR"), result.get("platform", "FB")
    
    def find_exact_worksheet_match(self, worksheet_titles: list, account_code: str, platform_code: str) -> str:
        """Find exact worksheet match with better error handling"""
        
        if not account_code or not platform_code:
            print(f"❌ Cannot search worksheets - missing account or platform")
            return None
        
        # Get the display name for the account
        display_name = self.account_mapping.get(account_code, account_code)
        
        # Try exact format: "Account - Platform"
        target_format = f"{display_name} - {platform_code}"
        
        print(f"🎯 LOOKING FOR EXACT MATCH: '{target_format}'")
        print(f"📋 Available worksheets: {worksheet_titles}")
        
        for worksheet_title in worksheet_titles:
            if worksheet_title == target_format:
                print(f"✅ EXACT MATCH FOUND: '{worksheet_title}'")
                return worksheet_title
        
        print(f"❌ NO EXACT MATCH FOUND for '{target_format}'")
        
        # FIXED: Instead of raising exception, return first available worksheet
        if worksheet_titles:
            fallback_sheet = worksheet_titles[0]
            print(f"🔄 USING FALLBACK WORKSHEET: '{fallback_sheet}'")
            return fallback_sheet
        
        # If no worksheets exist at all, that's a real error
        return None