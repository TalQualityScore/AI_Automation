# app/src/automation/api_clients/account_mapper.py
"""
Account and Platform Detection Logic
Handles parsing of card titles to extract account codes and platforms
FIXES: BC3 FB routing issue with direct card title parsing
"""

from typing import Tuple
from .config import ACCOUNT_MAPPING, PLATFORM_MAPPING

class AccountMapper:
    """Handles account and platform detection from Trello card titles"""
    
    def __init__(self):
        self.account_mapping = ACCOUNT_MAPPING
        self.platform_mapping = PLATFORM_MAPPING
    
    def extract_account_and_platform(self, concept_name: str) -> Tuple[str, str]:
        """
        CORRECTED: Extract account and platform from card title format
        
        Expected format: "BC3 FB - New Ads from..."
        Returns: (account_code, platform_code)
        
        Example:
            Input: "BC3 FB - New Ads from GH AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416 (STOR 3133) | Quiz"
            Output: ("BC3", "FB")
        """
        
        print(f"🔍 ACCOUNT MAPPER - Analyzing: '{concept_name}'")
        
        # PRIORITY 1: Extract prefix before " - " (e.g., "BC3 FB" from "BC3 FB - New Ads from...")
        if " - " in concept_name:
            prefix = concept_name.split(" - ")[0].strip()
            print(f"🔍 EXTRACTED PREFIX: '{prefix}'")
            
            # Split prefix into account and platform
            parts = prefix.split()
            if len(parts) >= 2:
                account_code = parts[0]  # "BC3"
                platform_code = parts[1]  # "FB"
                print(f"✅ PARSED: Account='{account_code}', Platform='{platform_code}'")
                return account_code, platform_code
            elif len(parts) == 1:
                # Only account provided, default to YT
                account_code = parts[0]
                platform_code = "YT"
                print(f"✅ SINGLE PART: Account='{account_code}', Platform='{platform_code}' (defaulted)")
                return account_code, platform_code
        
        # FALLBACK: Try to detect from anywhere in the concept name
        print(f"⚠️ FALLBACK DETECTION")
        concept_upper = concept_name.upper()
        
        # Account detection - prioritize BC3 first
        account_code = "UNKNOWN"
        if 'BC3' in concept_upper:
            account_code = 'BC3'
            print(f"🎯 PRIORITY: BC3 detected")
        else:
            # Check other account codes (longest first to avoid partial matches)
            for code in sorted(self.account_mapping.keys(), key=len, reverse=True):
                if code != 'BC3' and code in concept_upper:
                    account_code = code
                    print(f"✅ FALLBACK Account detected: {code}")
                    break
        
        # Platform detection - prioritize FB when BC3 is detected
        platform_code = "YT"  # Default
        if account_code == 'BC3' and ('FB' in concept_upper or 'FACEBOOK' in concept_upper):
            platform_code = "FB"
            print(f"🎯 BC3 + FB combination detected!")
        else:
            # Check other platforms (longest first)
            platform_codes = sorted(self.platform_mapping.keys(), key=len, reverse=True)
            for code in platform_codes:
                if code in concept_upper:
                    platform_display = self.platform_mapping[code]
                    # Convert display name back to simple code
                    if platform_display == 'Facebook':
                        platform_code = 'FB'
                    elif platform_display == 'YouTube':
                        platform_code = 'YT'
                    else:
                        platform_code = code
                    print(f"✅ Platform detected: {code} -> {platform_code}")
                    break
        
        print(f"🎯 FINAL RESULT: Account='{account_code}', Platform='{platform_code}'")
        return account_code, platform_code
    
    def find_exact_worksheet_match(self, worksheet_titles: list, account_code: str, platform_code: str) -> str:
        """
        CORRECTED: Find exact match for 'Account - Platform' format
        
        Args:
            worksheet_titles: List of available worksheet names
            account_code: Account code (e.g., "BC3")
            platform_code: Platform code (e.g., "FB")
            
        Returns:
            Exact worksheet name or None if not found
            
        Example:
            Input: account_code="BC3", platform_code="FB"
            Output: "BC3 - FB"
        """
        
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
        return None
    
    def get_account_display_name(self, account_code: str) -> str:
        """Get display name for account code"""
        return self.account_mapping.get(account_code, account_code)
    
    def get_platform_display_name(self, platform_code: str) -> str:
        """Get display name for platform code"""
        return self.platform_mapping.get(platform_code.upper(), platform_code)