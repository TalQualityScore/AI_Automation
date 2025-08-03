# Enhanced Error Detection and Recovery System
import time
import threading
import traceback
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class ErrorSeverity(Enum):
    WARNING = "warning"
    ERROR = "error" 
    CRITICAL = "critical"

class ValidationResult(Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"

@dataclass
class ValidationIssue:
    severity: ErrorSeverity
    category: str
    message: str
    suggestion: str
    auto_fixable: bool = False

@dataclass
class ProcessingStatus:
    step: str
    progress: float
    message: str
    start_time: float
    timeout_seconds: int = 300  # 5 minutes default

class RobustAutomationEngine:
    def __init__(self):
        self.current_status = None
        self.validation_issues = []
        self.timeout_monitor = None
        
    def validate_trello_card(self, card_data) -> List[ValidationIssue]:
        """Comprehensive validation of Trello card data"""
        issues = []
        
        # Validation 1: Card Title
        if not card_data.get('name') or card_data['name'].strip() == '':
            issues.append(ValidationIssue(
                severity=ErrorSeverity.CRITICAL,
                category="Missing Data",
                message="Card has no title",
                suggestion="Please add a descriptive title to the Trello card"
            ))
        
        # Validation 2: Card Description
        if not card_data.get('desc') or card_data['desc'].strip() == '':
            issues.append(ValidationIssue(
                severity=ErrorSeverity.CRITICAL,
                category="Missing Data", 
                message="Card has no description",
                suggestion="Please add processing instructions and Google Drive link to card description"
            ))
        
        # Validation 3: Google Drive Link
        gdrive_link = self.extract_gdrive_link(card_data.get('desc', ''))
        if not gdrive_link:
            issues.append(ValidationIssue(
                severity=ErrorSeverity.CRITICAL,
                category="Missing Link",
                message="No Google Drive link found in card description",
                suggestion="Please add a valid Google Drive folder link"
            ))
        elif not self.validate_gdrive_link(gdrive_link):
            issues.append(ValidationIssue(
                severity=ErrorSeverity.CRITICAL,
                category="Invalid Link",
                message="Google Drive link appears to be broken or inaccessible",
                suggestion="Please check the link and ensure it's properly shared"
            ))
        
        # Validation 4: Conflicting Instructions
        conflicts = self.detect_instruction_conflicts(card_data.get('desc', ''))
        if conflicts:
            issues.append(ValidationIssue(
                severity=ErrorSeverity.WARNING,
                category="Conflicting Instructions",
                message=f"Found conflicting instructions: {', '.join(conflicts)}",
                suggestion="Please clarify which instruction should take priority"
            ))
        
        # Validation 5: Project Name Consistency
        title_project = self.extract_project_from_title(card_data.get('name', ''))
        desc_project = self.extract_project_from_description(card_data.get('desc', ''))
        if title_project and desc_project and title_project != desc_project:
            issues.append(ValidationIssue(
                severity=ErrorSeverity.WARNING,
                category="Data Mismatch",
                message=f"Project name mismatch: Title='{title_project}', Description='{desc_project}'",
                suggestion="Please ensure project names match between title and description"
            ))
        
        return issues
    
    def validate_google_drive_access(self, folder_url, creds) -> List[ValidationIssue]:
        """Validate Google Drive folder access and contents"""
        issues = []
        
        try:
            # Test folder access
            folder_id = folder_url.split('/')[-1]
            drive_service = build("drive", "v3", credentials=creds)
            
            # Check folder permissions
            try:
                folder_info = drive_service.files().get(fileId=folder_id).execute()
            except Exception as e:
                issues.append(ValidationIssue(
                    severity=ErrorSeverity.CRITICAL,
                    category="Access Denied",
                    message="Cannot access Google Drive folder",
                    suggestion="Please ensure the folder is shared with the automation account"
                ))
                return issues
            
            # Check for video files
            query = f"'{folder_id}' in parents and mimeType contains 'video/'"
            results = drive_service.files().list(q=query, fields="files(id, name, size)").execute()
            video_files = results.get("files", [])
            
            if not video_files:
                issues.append(ValidationIssue(
                    severity=ErrorSeverity.CRITICAL,
                    category="No Files",
                    message="No video files found in Google Drive folder",
                    suggestion="Please ensure video files are uploaded to the shared folder"
                ))
            else:
                # Check for corrupted files (0 bytes)
                corrupted_files = [f for f in video_files if f.get('size', '0') == '0']
                if corrupted_files:
                    issues.append(ValidationIssue(
                        severity=ErrorSeverity.ERROR,
                        category="Corrupted Files",
                        message=f"Found corrupted files: {[f['name'] for f in corrupted_files]}",
                        suggestion="Please re-upload corrupted files"
                    ))
                
                # Check for very large files (>1GB)
                large_files = [f for f in video_files if int(f.get('size', '0')) > 1073741824]
                if large_files:
                    issues.append(ValidationIssue(
                        severity=ErrorSeverity.WARNING,
                        category="Large Files",
                        message=f"Found large files (>1GB): {[f['name'] for f in large_files]}",
                        suggestion="Large files may take longer to process. Consider compressing if possible."
                    ))
        
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ErrorSeverity.CRITICAL,
                category="System Error",
                message=f"Error validating Google Drive access: {str(e)}",
                suggestion="Please check your internet connection and try again"
            ))
        
        return issues
    
    def validate_assets(self, processing_mode) -> List[ValidationIssue]:
        """Validate required assets are available"""
        issues = []
        
        if processing_mode in ["quiz_only", "connector_quiz"]:
            # Check quiz outro
            quiz_path = "Assets/Videos/quiz_outro/"
            if not os.path.exists(quiz_path):
                issues.append(ValidationIssue(
                    severity=ErrorSeverity.CRITICAL,
                    category="Missing Assets",
                    message="Quiz outro folder not found",
                    suggestion="Please ensure Assets/Videos/quiz_outro/ exists with quiz video files"
                ))
            else:
                quiz_files = [f for f in os.listdir(quiz_path) if f.lower().endswith(('.mp4', '.mov'))]
                if not quiz_files:
                    issues.append(ValidationIssue(
                        severity=ErrorSeverity.CRITICAL,
                        category="Missing Assets",
                        message="No quiz outro videos found",
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
                                message=f"Quiz outro file is corrupted: {quiz_file}",
                                suggestion="Please replace the corrupted quiz outro file"
                            ))
        
        if processing_mode == "connector_quiz":
            # Check connector
            connector_path = "Assets/Videos/connectors/"
            if not os.path.exists(connector_path):
                issues.append(ValidationIssue(
                    severity=ErrorSeverity.CRITICAL,
                    category="Missing Assets", 
                    message="Connector folder not found",
                    suggestion="Please ensure Assets/Videos/connectors/ exists with connector video files"
                ))
            else:
                connector_files = [f for f in os.listdir(connector_path) if f.lower().endswith(('.mp4', '.mov'))]
                if not connector_files:
                    issues.append(ValidationIssue(
                        severity=ErrorSeverity.CRITICAL,
                        category="Missing Assets",
                        message="No connector videos found", 
                        suggestion="Please add connector video files to Assets/Videos/connectors/"
                    ))
        
        return issues
    
    def execute_with_timeout_monitoring(self, operation_func, operation_name, timeout_seconds=300):
        """Execute operation with timeout monitoring and progress tracking"""
        
        self.current_status = ProcessingStatus(
            step=operation_name,
            progress=0.0,
            message=f"Starting {operation_name}...",
            start_time=time.time(),
            timeout_seconds=timeout_seconds
        )
        
        # Start timeout monitor
        self.timeout_monitor = threading.Thread(target=self._monitor_timeout, daemon=True)
        self.timeout_monitor.start()
        
        try:
            result = operation_func()
            self.current_status = None
            return result
            
        except TimeoutError:
            raise Exception(f"Operation '{operation_name}' timed out after {timeout_seconds} seconds")
        except Exception as e:
            self.current_status = None
            raise e
    
    def _monitor_timeout(self):
        """Monitor for operation timeout"""
        while self.current_status:
            elapsed = time.time() - self.current_status.start_time
            if elapsed > self.current_status.timeout_seconds:
                # Log timeout
                print(f"⚠️  TIMEOUT: {self.current_status.step} exceeded {self.current_status.timeout_seconds} seconds")
                
                # Create timeout error popup
                self.show_timeout_error(self.current_status.step, elapsed)
                
                # Force termination
                raise TimeoutError(f"Operation timed out: {self.current_status.step}")
            
            time.sleep(1)
    
    def show_timeout_error(self, operation, elapsed_time):
        """Show timeout error to user"""
        # This would be integrated with the confirmation popup system
        error_message = f"""
        ⚠️ Operation Timeout
        
        Operation: {operation}
        Time Elapsed: {elapsed_time:.1f} seconds
        
        The operation appears to be stuck. This usually indicates:
        • Network connectivity issues
        • Invalid Google Drive links
        • Missing or corrupted files
        • API service problems
        
        Please check your inputs and try again.
        """
        print(error_message)  # For now, we'll just print. Later integrate with GUI popup
    
    def detect_instruction_conflicts(self, description):
        """Detect conflicting instructions in card description"""
        conflicts = []
        
        # Check for save vs process conflicts
        save_patterns = ["save as is", "save them as is", "just save", "save and rename"]
        process_patterns = ["attach to quiz", "connect to quiz", "add connector", "quiz outro"]
        
        has_save = any(pattern in description.lower() for pattern in save_patterns)
        has_process = any(pattern in description.lower() for pattern in process_patterns)
        
        if has_save and has_process:
            conflicts.append("Save vs Process instructions")
        
        # Check for multiple processing modes
        if "connector" in description.lower() and "only quiz" in description.lower():
            conflicts.append("Connector vs Quiz-only instructions")
        
        return conflicts
    
    def extract_gdrive_link(self, description):
        """Extract Google Drive link from description"""
        import re
        gdrive_pattern = r'https?://drive\.google\.com/drive/folders/[\w-]+'
        match = re.search(gdrive_pattern, description)
        return match.group(0) if match else None
    
    def validate_gdrive_link(self, link):
        """Basic validation of Google Drive link format"""
        return "drive.google.com/drive/folders/" in link and len(link.split('/')[-1]) > 10
    
    def extract_project_from_title(self, title):
        """Extract project name from card title"""
        # Implementation depends on your title format
        # This is a placeholder
        return title.split('-')[0].strip() if title and '-' in title else None
    
    def extract_project_from_description(self, description):
        """Extract project name from description files"""
        # Implementation depends on your description format
        # This is a placeholder  
        return None

# Enhanced main automation function with validation
def main_with_validation(trello_card_id):
    """Main automation function with comprehensive validation"""
    
    engine = RobustAutomationEngine()
    all_issues = []
    
    try:
        # Step 1: Fetch and validate Trello card
        print("🔍 Validating Trello card...")
        card_data, error = get_trello_card_data(trello_card_id)
        if error:
            raise Exception(f"Failed to fetch Trello card: {error}")
        
        # Comprehensive validation
        validation_issues = engine.validate_trello_card(card_data)
        all_issues.extend(validation_issues)
        
        # Check for critical issues
        critical_issues = [i for i in validation_issues if i.severity == ErrorSeverity.CRITICAL]
        if critical_issues:
            # Show validation popup with issues
            show_validation_popup(all_issues)
            return  # Stop execution
        
        # Step 2: Parse processing mode
        processing_mode = parse_card_instructions(card_data.get('desc', ''))
        
        # Step 3: Validate Google Drive access
        gdrive_link = engine.extract_gdrive_link(card_data.get('desc', ''))
        if gdrive_link:
            creds = get_google_creds()
            if creds:
                gdrive_issues = engine.validate_google_drive_access(gdrive_link, creds)
                all_issues.extend(gdrive_issues)
        
        # Step 4: Validate required assets
        asset_issues = engine.validate_assets(processing_mode)
        all_issues.extend(asset_issues)
        
        # Step 5: Show confirmation popup with all validation results
        user_approved = show_confirmation_popup(card_data, processing_mode, all_issues)
        if not user_approved:
            print("❌ User cancelled operation")
            return
        
        # Step 6: Execute with monitoring
        def execute_automation():
            # Your existing automation logic here
            return execute_original_automation(trello_card_id)
        
        result = engine.execute_with_timeout_monitoring(
            execute_automation, 
            "Video Processing",
            timeout_seconds=600  # 10 minutes
        )
        
        print("✅ Automation completed successfully!")
        
    except Exception as e:
        error_details = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'context': 'Main automation execution',
            'card_id': trello_card_id
        }
        
        # Show error popup with details
        show_error_popup(error_details)
        
def show_validation_popup(issues):
    """Show validation issues to user"""
    # This will be integrated with the confirmation popup system
    print("⚠️ Validation Issues Found:")
    for issue in issues:
        print(f"  {issue.severity.value.upper()}: {issue.message}")
        print(f"    Suggestion: {issue.suggestion}")

def show_confirmation_popup(card_data, processing_mode, issues):
    """Enhanced confirmation popup with validation results"""
    # This will be the main confirmation popup we build in Slice 3
    # For now, return True to continue
    return True

def show_error_popup(error_details):
    """Show error popup with detailed information"""
    print(f"❌ Error: {error_details['error']}")
    print(f"Context: {error_details['context']}")
    print("Full traceback saved to error log.")

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main_with_validation(sys.argv[1])
    else:
        print("Usage: python script.py <TRELLO_CARD_ID>")