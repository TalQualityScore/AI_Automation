# app/src/automation/api_clients/account_mapper/worksheet_matcher.py

from typing import List, Optional
from .config import ACCOUNT_MAPPING, WORKSHEET_NAME_MAPPINGS

class WorksheetMatcher:
    """Handles Google Sheets worksheet matching logic"""
    
    def __init__(self):
        self.account_mapping = ACCOUNT_MAPPING
        self.worksheet_mappings = WORKSHEET_NAME_MAPPINGS
    
    def find_exact_worksheet_match(self, worksheet_titles: List[str], account_code: str, platform_code: str) -> Optional[str]:
        """
        Find exact worksheet match with FIXED platform name mapping
        
        Args:
            worksheet_titles: List of available worksheet names
            account_code: Account code (e.g., 'BC3')
            platform_code: Platform code (e.g., 'SNAP')
            
        Returns:
            Worksheet name if found, None if not found
        """
        
        if not account_code or not platform_code:
            print(f"❌ Cannot search worksheets - missing account or platform")
            return None
        
        # Get the display name for the account
        account_display = self.account_mapping.get(account_code, account_code)
        
        # FIXED: Get the correct worksheet platform name
        worksheet_platform = self.worksheet_mappings.get(platform_code, platform_code)
        
        # FIXED: Try different worksheet name formats
        possible_formats = [
            f"{account_display} - {worksheet_platform}",  # "Bio Complete 3 - Snapchat"
            f"{account_code} - {worksheet_platform}",     # "BC3 - Snapchat"
            f"{account_display}-{worksheet_platform}",    # "Bio Complete 3-Snapchat"
            f"{account_code}-{worksheet_platform}",       # "BC3-Snapchat"
            f"{account_code} - {platform_code}",          # "BC3 - SNAP" (fallback)
        ]
        
        print(f"🎯 LOOKING FOR WORKSHEET MATCHES:")
        print(f"   Account: {account_code} ({account_display})")
        print(f"   Platform: {platform_code} -> Worksheet: {worksheet_platform}")
        print(f"📋 Available worksheets: {worksheet_titles}")
        
        # Try each possible format
        for i, target_format in enumerate(possible_formats, 1):
            print(f"   Trying format {i}: '{target_format}'")
            
            for worksheet_title in worksheet_titles:
                if worksheet_title == target_format:
                    print(f"✅ EXACT MATCH FOUND: '{worksheet_title}'")
                    return worksheet_title
        
        print(f"❌ NO WORKSHEET MATCH FOUND for account '{account_code}' + platform '{platform_code}'")
        print(f"   Tried formats: {possible_formats}")
        return None
    
    def get_best_fallback_worksheet(self, worksheet_titles: List[str], account_code: str) -> Optional[str]:
        """Get best fallback worksheet for the account"""
        
        if not worksheet_titles:
            return None
        
        account_display = self.account_mapping.get(account_code, account_code)
        
        # Look for any worksheet that starts with the account
        for worksheet in worksheet_titles:
            if worksheet.startswith(account_display) or worksheet.startswith(account_code):
                print(f"🔄 FALLBACK WORKSHEET: Using '{worksheet}' for account '{account_code}'")
                return worksheet
        
        # If no account-specific worksheet, return first available
        fallback = worksheet_titles[0]
        print(f"⚠️ EMERGENCY FALLBACK: Using '{fallback}' (first available)")
        return fallback
    
    def list_available_worksheets_for_account(self, worksheet_titles: List[str], account_code: str) -> List[str]:
        """List all worksheets that match the given account"""
        
        account_display = self.account_mapping.get(account_code, account_code)
        matching_worksheets = []
        
        for worksheet in worksheet_titles:
            if (worksheet.startswith(account_display) or 
                worksheet.startswith(account_code) or
                account_code in worksheet or
                account_display in worksheet):
                matching_worksheets.append(worksheet)
        
        return matching_worksheets