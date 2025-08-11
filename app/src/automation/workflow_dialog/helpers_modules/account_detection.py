# app/src/automation/workflow_dialog/helpers_modules/account_detection.py
"""
Account and Platform Detection Module
Handles all detection logic and fallback dialogs
"""

import sys
import threading

class AccountDetector:
    """Handles account and platform detection from various sources"""
    
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
            'SNAP': 'Snapchat',
            'REELS': 'Reels'
        }
    
    def detect_account_and_platform(self, card_data, project_info):
        """
        Main detection method that tries multiple sources
        
        Returns:
            tuple: (account_code, platform_code, account_display, platform_display)
        """
        card_title = card_data.get('name', '')
        print(f"🔍 Starting account/platform detection for: '{card_title}'")
        
        # Try detection from multiple sources
        account_code = None
        platform_code = None
        
        # Source 1: Check project_info
        account_code, platform_code = self._check_project_info(project_info)
        
        # Source 2: Check card_data
        if not self._is_valid_detection(account_code, platform_code):
            account_code, platform_code = self._check_card_data(card_data)
        
        # Source 3: Fresh detection from title
        if not self._is_valid_detection(account_code, platform_code):
            account_code, platform_code = self._fresh_detection(card_title)
        
        # Source 4: User fallback dialog
        if not self._is_valid_detection(account_code, platform_code):
            account_code, platform_code = self._show_fallback_dialog(
                card_title, account_code, platform_code, card_data
            )
        
        # Ensure valid values
        if not account_code or account_code == 'UNKNOWN':
            account_code = 'TR'
        if not platform_code or platform_code == 'UNKNOWN':
            platform_code = 'FB'
        
        # Store back in project_info
        project_info['account_code'] = account_code
        project_info['platform_code'] = platform_code
        project_info['detected_account_code'] = account_code
        project_info['detected_platform_code'] = platform_code
        
        # Get display names
        account_display = f"{account_code} ({self.account_mapping.get(account_code, account_code)})"
        platform_display = self.platform_mapping.get(platform_code, platform_code)
        
        print(f"✅ Detection complete: {account_code}/{platform_code}")
        
        return account_code, platform_code, account_display, platform_display
    
    def _check_project_info(self, project_info):
        """Check project_info for account/platform data"""
        account_keys = ['account_code', 'account', 'detected_account', 'detected_account_code']
        platform_keys = ['platform_code', 'platform', 'detected_platform', 'detected_platform_code']
        
        account_code = None
        platform_code = None
        
        for key in account_keys:
            if key in project_info and project_info[key] and project_info[key] != 'UNKNOWN':
                account_code = project_info[key]
                print(f"  Found account in project_info['{key}']: '{account_code}'")
                break
        
        for key in platform_keys:
            if key in project_info and project_info[key] and project_info[key] != 'UNKNOWN':
                platform_code = project_info[key]
                print(f"  Found platform in project_info['{key}']: '{platform_code}'")
                break
        
        return account_code, platform_code
    
    def _check_card_data(self, card_data):
        """Check card_data for account/platform data"""
        account_code = card_data.get('detected_account_code')
        platform_code = card_data.get('detected_platform_code')
        
        if account_code:
            print(f"  Found account in card_data: '{account_code}'")
        if platform_code:
            print(f"  Found platform in card_data: '{platform_code}'")
        
        return account_code, platform_code
    
    def _fresh_detection(self, card_title):
        """Attempt fresh detection from card title"""
        print(f"  Attempting fresh detection from title...")
        
        try:
            from ...api_clients.account_mapper import AccountMapper
            mapper = AccountMapper()
            
            account_code, platform_code = mapper.extract_account_and_platform(
                card_title, allow_fallback=False
            )
            
            if account_code and account_code != 'UNKNOWN':
                print(f"  ✅ Fresh detection: {account_code}/{platform_code}")
            else:
                print(f"  ⚠️ Fresh detection incomplete")
            
            return account_code, platform_code
            
        except Exception as e:
            print(f"  ❌ Fresh detection failed: {e}")
            return None, None
    
    def _show_fallback_dialog(self, card_title, current_account, current_platform, card_data):
        """Show user fallback dialog for manual selection"""
        
        if not self._can_show_dialog():
            print("  ❌ Cannot show dialog (not main thread), using defaults")
            return 'TR', 'FB'
        
        try:
            print("  📝 Showing user fallback dialog...")
            
            from ...api_clients.account_mapper.fallback_dialog import FallbackSelectionDialog
            dialog = FallbackSelectionDialog()
            
            account_code, platform_code = dialog.show_fallback_selection(
                card_title=card_title,
                detected_account=current_account if current_account != 'UNKNOWN' else None,
                detected_platform=current_platform if current_platform != 'UNKNOWN' else None,
                card_url=card_data.get('shortUrl', '')
            )
            
            if account_code is None or platform_code is None:
                print("❌ User cancelled - exiting program")
                sys.exit(0)
            
            print(f"  ✅ User selected: {account_code}/{platform_code}")
            return account_code, platform_code
            
        except Exception as e:
            print(f"  ❌ Fallback dialog error: {e}")
            return 'TR', 'FB'
    
    def _is_valid_detection(self, account_code, platform_code):
        """Check if detection is valid and complete"""
        return (account_code and account_code != 'UNKNOWN' and 
                platform_code and platform_code != 'UNKNOWN')
    
    def _can_show_dialog(self):
        """Check if we can show a dialog (main thread only)"""
        return threading.current_thread() is threading.main_thread()