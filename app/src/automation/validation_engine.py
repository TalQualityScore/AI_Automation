# app/src/automation/validation_engine.py
# Updated to validate SVSL and VSL assets with new folder structure

import os
import re
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass

class ErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationIssue:
    severity: ErrorSeverity
    category: str
    message: str
    suggestion: str = ""

class ValidationEngine:
    """Validation engine for checking card data and assets"""
    
    def __init__(self, account_code: str = None, platform_code: str = None):
        self.account_code = account_code
        self.platform_code = platform_code
        self.script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.assets_base_path = os.path.join(self.script_dir, "Assets", "Videos")
    
    def set_account_platform(self, account_code: str, platform_code: str):
        """Update account and platform codes for validation"""
        self.account_code = account_code
        self.platform_code = platform_code
    
    def _get_asset_path(self, asset_type: str) -> str:
        """Get the path to a specific asset type based on account and platform"""
        if not self.account_code or not self.platform_code:
            # Fallback to old structure
            if asset_type == "Connectors":
                return os.path.join(self.script_dir, "Assets", "Videos", "connectors")
            elif asset_type == "Quiz":
                return os.path.join(self.script_dir, "Assets", "Videos", "quiz_outro")
            else:
                return None
        
        # Build path based on new structure
        asset_path = os.path.join(self.assets_base_path, self.account_code, self.platform_code, asset_type)
        
        # Check if path exists, if not try without platform for some assets
        if not os.path.exists(asset_path) and asset_type in ["SVSL", "VSL"]:
            # Try direct account level for SVSL/VSL if not platform-specific
            asset_path = os.path.join(self.assets_base_path, self.account_code, asset_type)
        
        return asset_path if os.path.exists(asset_path) else None
    
    def validate_trello_card(self, card_data: dict) -> List[ValidationIssue]:
        """Validate Trello card data"""
        issues = []
        
        # Validation 1: Card Name
        if not card_data.get('name'):
            issues.append(ValidationIssue(
                severity=ErrorSeverity.CRITICAL,
                category="Missing Data",
                message="❌ Card has no name/title",
                suggestion="Please ensure the Trello card has a proper title"
            ))
        
        # Validation 2: Card Description
        if not card_data.get('desc'):
            issues.append(ValidationIssue(
                severity=ErrorSeverity.WARNING,
                category="Missing Data",
                message="⚠️ Card has no description",
                suggestion="Add processing instructions to the card description"
            ))
        
        # Validation 3: Google Drive Link
        gdrive_link = self.extract_gdrive_link(card_data.get('desc', ''))
        if not gdrive_link:
            issues.append(ValidationIssue(
                severity=ErrorSeverity.CRITICAL,
                category="Missing Link",
                message="❌ No Google Drive link found in card description",
                suggestion="Please add a valid Google Drive folder link"
            ))
        elif not self.validate_gdrive_link_format(gdrive_link):
            issues.append(ValidationIssue(
                severity=ErrorSeverity.ERROR,
                category="Invalid Link",
                message="⚠️ Google Drive link format appears invalid",
                suggestion="Please check the link format and ensure it's a folder link"
            ))
        
        # Validation 4: Conflicting Instructions
        conflicts = self.detect_instruction_conflicts(card_data.get('desc', ''))
        if conflicts:
            issues.append(ValidationIssue(
                severity=ErrorSeverity.WARNING,
                category="Conflicting Instructions",
                message=f"⚠️ Found conflicting instructions: {', '.join(conflicts)}",
                suggestion="Please clarify which instruction should take priority"
            ))
        
        return issues
    
    def validate_assets(self, processing_mode: str) -> List[ValidationIssue]:
        """Validate required assets are available based on processing mode"""
        issues = []
        
        print(f"🔍 Validating required assets for {processing_mode} mode...")
        
        # Check quiz assets
        if processing_mode in ["quiz_only", "connector_quiz"]:
            quiz_path = self._get_asset_path("Quiz")
            if not quiz_path:
                issues.append(ValidationIssue(
                    severity=ErrorSeverity.CRITICAL,
                    category="Missing Assets",
                    message=f"❌ Quiz outro folder not found for {self.account_code}/{self.platform_code}",
                    suggestion=f"Please ensure Assets/Videos/{self.account_code}/{self.platform_code}/Quiz/ exists"
                ))
            else:
                quiz_files = [f for f in os.listdir(quiz_path) if f.lower().endswith(('.mp4', '.mov'))]
                if not quiz_files:
                    issues.append(ValidationIssue(
                        severity=ErrorSeverity.CRITICAL,
                        category="Missing Assets",
                        message="❌ No quiz outro videos found",
                        suggestion=f"Please add quiz outro video files to {quiz_path}"
                    ))
                else:
                    # Check for corrupted quiz files
                    for quiz_file in quiz_files:
                        file_path = os.path.join(quiz_path, quiz_file)
                        if os.path.getsize(file_path) == 0:
                            issues.append(ValidationIssue(
                                severity=ErrorSeverity.ERROR,
                                category="Corrupted Assets",
                                message=f"⚠️ Quiz outro file is corrupted (0 bytes): {quiz_file}",
                                suggestion="Please replace the corrupted quiz outro file"
                            ))
        
        # Check SVSL assets
        if processing_mode in ["svsl_only", "connector_svsl"]:
            svsl_path = self._get_asset_path("SVSL")
            if not svsl_path:
                issues.append(ValidationIssue(
                    severity=ErrorSeverity.CRITICAL,
                    category="Missing Assets",
                    message=f"❌ SVSL folder not found for {self.account_code}/{self.platform_code}",
                    suggestion=f"Please ensure Assets/Videos/{self.account_code}/{self.platform_code}/SVSL/ exists"
                ))
            else:
                svsl_files = [f for f in os.listdir(svsl_path) if f.lower().endswith(('.mp4', '.mov'))]
                if not svsl_files:
                    issues.append(ValidationIssue(
                        severity=ErrorSeverity.CRITICAL,
                        category="Missing Assets",
                        message="❌ No SVSL videos found",
                        suggestion=f"Please add SVSL video files to {svsl_path}"
                    ))
        
        # Check VSL assets
        if processing_mode in ["vsl_only", "connector_vsl"]:
            vsl_path = self._get_asset_path("VSL")
            if not vsl_path:
                issues.append(ValidationIssue(
                    severity=ErrorSeverity.CRITICAL,
                    category="Missing Assets",
                    message=f"❌ VSL folder not found for {self.account_code}/{self.platform_code}",
                    suggestion=f"Please ensure Assets/Videos/{self.account_code}/{self.platform_code}/VSL/ exists"
                ))
            else:
                vsl_files = [f for f in os.listdir(vsl_path) if f.lower().endswith(('.mp4', '.mov'))]
                if not vsl_files:
                    issues.append(ValidationIssue(
                        severity=ErrorSeverity.CRITICAL,
                        category="Missing Assets",
                        message="❌ No VSL videos found",
                        suggestion=f"Please add VSL video files to {vsl_path}"
                    ))
        
        # Check connector assets
        if processing_mode in ["connector_quiz", "connector_svsl", "connector_vsl"]:
            connector_path = self._get_asset_path("Connectors")
            if not connector_path:
                issues.append(ValidationIssue(
                    severity=ErrorSeverity.CRITICAL,
                    category="Missing Assets",
                    message=f"❌ Connector folder not found for {self.account_code}/{self.platform_code}",
                    suggestion=f"Please ensure Assets/Videos/{self.account_code}/{self.platform_code}/Connectors/ exists"
                ))
            else:
                connector_files = [f for f in os.listdir(connector_path) if f.lower().endswith(('.mp4', '.mov'))]
                if not connector_files:
                    issues.append(ValidationIssue(
                        severity=ErrorSeverity.CRITICAL,
                        category="Missing Assets",
                        message="❌ No connector videos found",
                        suggestion=f"Please add connector video files to {connector_path}"
                    ))
        
        return issues
    
    def detect_instruction_conflicts(self, description):
        """Detect conflicting instructions in card description"""
        conflicts = []
        description_lower = description.lower()
        
        # Check for save vs process conflicts
        save_patterns = ["save as is", "save them as is", "just save", "save and rename"]
        process_patterns = ["attach to quiz", "connect to quiz", "add connector", "quiz outro", 
                          "attach to svsl", "connect to svsl", "attach to vsl", "connect to vsl"]
        
        has_save = any(pattern in description_lower for pattern in save_patterns)
        has_process = any(pattern in description_lower for pattern in process_patterns)
        
        if has_save and has_process:
            conflicts.append("Save vs Process instructions")
        
        # Check for multiple endpoint conflicts
        endpoints = []
        if "quiz" in description_lower:
            endpoints.append("Quiz")
        if "svsl" in description_lower:
            endpoints.append("SVSL")
        if "vsl" in description_lower:
            endpoints.append("VSL")
        
        if len(endpoints) > 1:
            conflicts.append(f"Multiple endpoints specified: {', '.join(endpoints)}")
        
        return conflicts
    
    def extract_gdrive_link(self, description):
        """Extract Google Drive link from description"""
        gdrive_pattern = r'https?://drive\.google\.com/drive/folders/[\w-]+'
        match = re.search(gdrive_pattern, description)
        return match.group(0) if match else None
    
    def validate_gdrive_link_format(self, link):
        """Basic validation of Google Drive link format"""
        return ("drive.google.com/drive/folders/" in link and 
                len(link.split('/')[-1]) > 10)
    
    def show_validation_results(self, issues):
        """Display validation results to user"""
        if not issues:
            print("✅ All validations passed!")
            return True
        
        # Group by severity
        critical_issues = [i for i in issues if i.severity == ErrorSeverity.CRITICAL]
        error_issues = [i for i in issues if i.severity == ErrorSeverity.ERROR]
        warning_issues = [i for i in issues if i.severity == ErrorSeverity.WARNING]
        info_issues = [i for i in issues if i.severity == ErrorSeverity.INFO]
        
        # Display issues
        if critical_issues:
            print("\n🔴 CRITICAL ISSUES (Must be fixed):")
            for issue in critical_issues:
                print(f"  {issue.message}")
                if issue.suggestion:
                    print(f"    → {issue.suggestion}")
        
        if error_issues:
            print("\n🟠 ERRORS (Should be fixed):")
            for issue in error_issues:
                print(f"  {issue.message}")
                if issue.suggestion:
                    print(f"    → {issue.suggestion}")
        
        if warning_issues:
            print("\n🟡 WARNINGS (Consider fixing):")
            for issue in warning_issues:
                print(f"  {issue.message}")
                if issue.suggestion:
                    print(f"    → {issue.suggestion}")
        
        if info_issues:
            print("\n🔵 INFO:")
            for issue in info_issues:
                print(f"  {issue.message}")
        
        # Return False if there are critical issues
        return len(critical_issues) == 0