# app/src/automation/validation_engine.py
import os
import re
from dataclasses import dataclass
from typing import List
from enum import Enum

class ErrorSeverity(Enum):
    WARNING = "warning"
    ERROR = "error" 
    CRITICAL = "critical"

@dataclass
class ValidationIssue:
    severity: ErrorSeverity
    category: str
    message: str
    suggestion: str

class ValidationEngine:
    """Handles all validation logic for Trello cards, assets, and Google Drive"""
    
    def validate_trello_card(self, card_data) -> List[ValidationIssue]:
        """Comprehensive validation of Trello card data"""
        issues = []
        
        print("🔍 Validating Trello card data...")
        
        # Validation 1: Card Title
        if not card_data.get('name') or card_data['name'].strip() == '':
            issues.append(ValidationIssue(
                severity=ErrorSeverity.CRITICAL,
                category="Missing Data",
                message="❌ Card has no title",
                suggestion="Please add a descriptive title to the Trello card"
            ))
        
        # Validation 2: Card Description
        if not card_data.get('desc') or card_data['desc'].strip() == '':
            issues.append(ValidationIssue(
                severity=ErrorSeverity.CRITICAL,
                category="Missing Data", 
                message="❌ Card has no description",
                suggestion="Please add processing instructions and Google Drive link to card description"
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
    
    def validate_assets(self, processing_mode) -> List[ValidationIssue]:
        """Validate required assets are available"""
        issues = []
        
        print("🔍 Validating required assets...")
        
        if processing_mode in ["quiz_only", "connector_quiz"]:
            # Check quiz outro
            quiz_path = "Assets/Videos/quiz_outro/"
            if not os.path.exists(quiz_path):
                issues.append(ValidationIssue(
                    severity=ErrorSeverity.CRITICAL,
                    category="Missing Assets",
                    message="❌ Quiz outro folder not found",
                    suggestion="Please ensure Assets/Videos/quiz_outro/ exists with quiz video files"
                ))
            else:
                quiz_files = [f for f in os.listdir(quiz_path) if f.lower().endswith(('.mp4', '.mov'))]
                if not quiz_files:
                    issues.append(ValidationIssue(
                        severity=ErrorSeverity.CRITICAL,
                        category="Missing Assets",
                        message="❌ No quiz outro videos found",
                        suggestion="Please add quiz outro video files to Assets/Videos/quiz_outro/"
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
        
        if processing_mode == "connector_quiz":
            # Check connector
            connector_path = "Assets/Videos/connectors/"
            if not os.path.exists(connector_path):
                issues.append(ValidationIssue(
                    severity=ErrorSeverity.CRITICAL,
                    category="Missing Assets", 
                    message="❌ Connector folder not found",
                    suggestion="Please ensure Assets/Videos/connectors/ exists with connector video files"
                ))
            else:
                connector_files = [f for f in os.listdir(connector_path) if f.lower().endswith(('.mp4', '.mov'))]
                if not connector_files:
                    issues.append(ValidationIssue(
                        severity=ErrorSeverity.CRITICAL,
                        category="Missing Assets",
                        message="❌ No connector videos found", 
                        suggestion="Please add connector video files to Assets/Videos/connectors/"
                    ))
        
        return issues
    
    def detect_instruction_conflicts(self, description):
        """Detect conflicting instructions in card description"""
        conflicts = []
        description_lower = description.lower()
        
        # Check for save vs process conflicts
        save_patterns = ["save as is", "save them as is", "just save", "save and rename"]
        process_patterns = ["attach to quiz", "connect to quiz", "add connector", "quiz outro"]
        
        has_save = any(pattern in description_lower for pattern in save_patterns)
        has_process = any(pattern in description_lower for pattern in process_patterns)
        
        if has_save and has_process:
            conflicts.append("Save vs Process instructions")
        
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
        
        print("\n" + "="*50)
        print("🔍 VALIDATION RESULTS")
        print("="*50)
        
        critical_count = len([i for i in issues if i.severity == ErrorSeverity.CRITICAL])
        error_count = len([i for i in issues if i.severity == ErrorSeverity.ERROR])
        warning_count = len([i for i in issues if i.severity == ErrorSeverity.WARNING])
        
        print(f"Found {len(issues)} issues:")
        print(f"  • {critical_count} Critical (must fix)")
        print(f"  • {error_count} Errors (should fix)")
        print(f"  • {warning_count} Warnings (review)")
        print()
        
        for issue in issues:
            print(f"{issue.message}")
            print(f"  💡 {issue.suggestion}")
            print()
        
        if critical_count > 0:
            print("❌ Cannot proceed due to critical issues.")
            print("Please fix the issues above and try again.")
            return False
        
        if error_count > 0:
            print("⚠️ Found errors that may cause processing to fail.")
            print("Recommend fixing these issues before proceeding.")
        
        return True