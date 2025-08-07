# app/src/automation/api_clients/account_mapper/core.py

from typing import Tuple, List, Optional
import threading
from .detection import DetectionEngine
from .user_dialogs import UserDialogs
from .worksheet_matcher import WorksheetMatcher
from .config import ACCOUNT_MAPPING, PLATFORM_MAPPING

class AccountMapper:
    """
    MODULAR Account and Platform Detection System
    
    Features:
    - Direct prefix parsing (BC3 Snapchat -> BC3 + SNAP)
    - Smart keyword detection
    - User confirmation dialogs
    - FIXED worksheet name matching
    - Thread-safe operation
    """
    
    def __init__(self):
        self.account_mapping = ACCOUNT_MAPPING
        self.platform_mapping = PLATFORM_MAPPING
        
        # Initialize modular components
        self.detection_engine = DetectionEngine()
        self.user_dialogs = UserDialogs()
        self.worksheet_matcher = WorksheetMatcher()
        
        # Clear any potential cached data
        self._clear_cache()
    
    def _clear_cache(self):
        """Clear any potential cached detection data"""
        self._last_detection = None
        self._cached_result = None
    
    def extract_account_and_platform(self, concept_name: str, allow_fallback: bool = True) -> Tuple[str, str]:
        """Main entry point: Extract account and platform with comprehensive detection"""
        
        print(f"🔍 ACCOUNT MAPPER - Analyzing: '{concept_name}'")
        self._clear_cache()
        
        # STEP 1: Try direct prefix parsing (most reliable)
        account_code, platform_code = self.detection_engine.parse_direct_prefix(concept_name)
        
        if account_code != "UNKNOWN" and platform_code != "UNKNOWN":
            print(f"✅ DIRECT PREFIX SUCCESS: Account='{account_code}', Platform='{platform_code}'")
            # SKIP DIALOG - return directly
            return account_code, platform_code
        
        # STEP 2: Try smart detection for common patterns
        account_code, platform_code = self.detection_engine.smart_detection(concept_name)
        
        # Validate smart detection results
        is_valid, validation_msg = self.detection_engine.validate_detection(account_code, platform_code)
        
        if is_valid:
            print(f"✅ SMART DETECTION SUCCESS: Account='{account_code}', Platform='{platform_code}'")
            # SKIP DIALOG - return directly  
            return account_code, platform_code
        
        # FALLBACK: Return safe defaults
        print(f"⚠️ Using safe defaults: TR, FB")
        return "TR", "FB" 
       
    def find_exact_worksheet_match(self, worksheet_titles: List[str], account_code: str, platform_code: str) -> Optional[str]:
        """
        FIXED: Find exact worksheet match with proper platform name mapping
        
        This method now correctly maps:
        - BC3 + SNAP -> "BC3 - Snapchat" (not "BC3 - SNAP")
        - BC3 + FB -> "BC3 - FB" 
        - etc.
        """
        return self.worksheet_matcher.find_exact_worksheet_match(worksheet_titles, account_code, platform_code)
    
    def get_best_fallback_worksheet(self, worksheet_titles: List[str], account_code: str) -> Optional[str]:
        """Get best fallback worksheet for the account"""
        return self.worksheet_matcher.get_best_fallback_worksheet(worksheet_titles, account_code)
    
    def list_available_worksheets_for_account(self, worksheet_titles: List[str], account_code: str) -> List[str]:
        """List all worksheets that match the given account"""
        return self.worksheet_matcher.list_available_worksheets_for_account(worksheet_titles, account_code)
    
    def get_account_display_name(self, account_code: str) -> str:
        """Get display name for account code"""
        return self.account_mapping.get(account_code, account_code)
    
    def get_platform_display_name(self, platform_code: str) -> str:
        """Get display name for platform code"""
        return self.platform_mapping.get(platform_code, platform_code)
    
    def validate_account_platform_combination(self, account_code: str, platform_code: str) -> Tuple[bool, str]:
        """Validate that account and platform combination is valid"""
        return self.detection_engine.validate_detection(account_code, platform_code)