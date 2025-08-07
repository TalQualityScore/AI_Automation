# app/src/automation/api_clients/account_mapper/detection.py

from typing import Tuple
from .config import (
    ACCOUNT_MAPPING, PLATFORM_DETECTION_MAPPINGS, 
    ACCOUNT_KEYWORDS, PLATFORM_KEYWORDS
)

class DetectionEngine:
    """Handles account and platform detection logic"""
    
    def __init__(self):
        self.account_mapping = ACCOUNT_MAPPING
        self.platform_mappings = PLATFORM_DETECTION_MAPPINGS
        self.account_keywords = ACCOUNT_KEYWORDS
        self.platform_keywords = PLATFORM_KEYWORDS
    
    def parse_direct_prefix(self, concept_name: str) -> Tuple[str, str]:
        """Parse direct prefix format like 'BC3 Snapchat - New Ads from...'"""
        
        if " - " not in concept_name:
            return "UNKNOWN", "UNKNOWN"
        
        prefix = concept_name.split(" - ")[0].strip()
        print(f"🔍 EXTRACTED PREFIX: '{prefix}'")
        
        parts = prefix.split()
        if len(parts) < 2:
            print(f"⚠️ PREFIX TOO SHORT: Need at least 2 parts, got {len(parts)}")
            return "UNKNOWN", "UNKNOWN"
        
        account_part = parts[0].upper()
        platform_part = parts[1].upper()
        
        # Validate account exists in mapping
        if account_part not in self.account_mapping:
            print(f"⚠️ ACCOUNT NOT VALID: '{account_part}' not in {list(self.account_mapping.keys())}")
            return "UNKNOWN", "UNKNOWN"
        
        # FIXED: Use enhanced platform mapping
        if platform_part not in self.platform_mappings:
            print(f"⚠️ PLATFORM NOT VALID: '{platform_part}' not in {list(self.platform_mappings.keys())}")
            return "UNKNOWN", "UNKNOWN"
        
        mapped_platform = self.platform_mappings[platform_part]
        print(f"✅ MAPPED PLATFORM: '{platform_part}' -> '{mapped_platform}'")
        return account_part, mapped_platform
    
    def smart_detection(self, concept_name: str) -> Tuple[str, str]:
        """Smart detection for common patterns"""
        
        concept_lower = concept_name.lower()
        
        # Account detection from keywords
        detected_account = "UNKNOWN"
        for keyword, account in self.account_keywords.items():
            if keyword in concept_lower:
                detected_account = account
                print(f"🧠 SMART ACCOUNT DETECTION: Found '{keyword}' -> '{account}'")
                break
        
        # Platform detection from keywords
        detected_platform = "UNKNOWN"
        for keyword, platform in self.platform_keywords.items():
            if keyword in concept_lower:
                detected_platform = platform
                print(f"🧠 SMART PLATFORM DETECTION: Found '{keyword}' -> '{platform}'")
                break
        
        if detected_account != "UNKNOWN" or detected_platform != "UNKNOWN":
            print(f"🧠 SMART DETECTION RESULT: Account='{detected_account}', Platform='{detected_platform}'")
        
        return detected_account, detected_platform
    
    def validate_detection(self, account: str, platform: str) -> Tuple[bool, str]:
        """Validate that detected account and platform are valid"""
        
        if account == "UNKNOWN" or platform == "UNKNOWN":
            return False, f"Detection incomplete: Account='{account}', Platform='{platform}'"
        
        if account not in self.account_mapping:
            return False, f"Invalid account: '{account}' not in {list(self.account_mapping.keys())}"
        
        if platform not in self.platform_mappings.values():
            return False, f"Invalid platform: '{platform}' not in {list(self.platform_mappings.values())}"
        
        return True, "Detection valid"