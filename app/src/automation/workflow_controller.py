# app/src/automation/workflow_controller.py
"""
Complete workflow controller that orchestrates the entire user journey:
Confirmation → Processing → Results/Error
"""

import tkinter as tk
import time
import threading
from typing import Callable, Optional, Dict, Any

# Import our modular components
from .confirmation_dialog import ConfirmationDialog, ConfirmationData, ValidationIssue
from .processing_dialog import ProcessingDialog
from .results_dialog import ResultsDialog, ProcessingResult, NotificationSettings

class AutomationWorkflowController:
    """
    Main controller that orchestrates the complete automation workflow UI.
    Handles: Confirmation → Processing → Results/Error with proper state management.
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        self.confirmation_data = None
        self.processing_callback = None
        self.notification_settings = None
        self.current_dialog = None
        
    def start_workflow(self, 
                      confirmation_data: ConfirmationData, 
                      processing_callback: Callable,
                      estimated_duration: str = "5-8 minutes") -> bool:
        """
        Start the complete workflow with confirmation, processing, and results.
        
        Args:
            confirmation_data: Data for the confirmation dialog
            processing_callback: Function to call for actual processing
            estimated_duration: Expected processing time for user display
            
        Returns:
            bool: True if user completed workflow, False if cancelled
        """
        self.confirmation_data = confirmation_data
        self.processing_callback = processing_callback
        
        try:
            # Step 1: Show confirmation dialog
            if not self._show_confirmation():
                return False  # User cancelled
            
            # Step 2: Show processing dialog and execute
            processing_result = self._show_processing(estimated_duration)
            
            # Step 3: Show results (success or error)
            self._show_results(processing_result)
            
            return processing_result.success if processing_result else False
            
        except Exception as e:
            # Handle any unexpected errors in the workflow
            self._show_error("Workflow Error", str(e), 
                           "An unexpected error occurred in the automation workflow.")
            return False
    
    def _show_confirmation(self) -> bool:
        """Show confirmation dialog and handle user response"""
        try:
            dialog = ConfirmationDialog(self.parent)
            user_confirmed, notifications = dialog.show_confirmation(self.confirmation_data)
            
            if user_confirmed:
                # Store notification settings for later use
                self.notification_settings = NotificationSettings(
                    email_enabled=notifications['email']['enabled'],
                    email_address=notifications['email']['address'],
                    slack_enabled=notifications['slack']['enabled'],
                    slack_webhook=notifications['slack']['webhook']
                )
                return True
            else:
                return False
                
        except Exception as e:
            self._show_error("Confirmation Error", str(e), 
                           "Failed to show confirmation dialog. Please try again.")
            return False
    
    def _show_processing(self, estimated_duration: str) -> Optional[ProcessingResult]:
        """Show processing dialog and execute the processing callback"""
        processing_result = None
        processing_error = None
        
        def processing_wrapper(progress_callback):
            """Wrapper that executes processing and captures results"""
            nonlocal processing_result, processing_error
            
            try:
                # Execute the actual processing callback
                result = self.processing_callback(progress_callback)
                
                if isinstance(result, ProcessingResult):
                    processing_result = result
                else:
                    # If callback doesn't return ProcessingResult, create success result
                    processing_result = ProcessingResult(
                        success=True,
                        duration="Processing completed",
                        processed_files=result if isinstance(result, list) else [],
                        output_folder=getattr(result, 'output_folder', 'Unknown'),
                    )
                    
            except Exception as e:
                processing_error = e
                processing_result = ProcessingResult(
                    success=False,
                    duration="",
                    processed_files=[],
                    output_folder="",
                    error_message=str(e),
                    error_solution=self._generate_error_solution(str(e))
                )
        
        try:
            dialog = ProcessingDialog(self.parent)
            dialog.show_processing(processing_wrapper, estimated_duration)
            
            return processing_result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                duration="",
                processed_files=[],
                output_folder="",
                error_message=f"Processing dialog error: {str(e)}",
                error_solution="Please try restarting the application and try again."
            )
    
    def _show_results(self, result: ProcessingResult):
        """Show results dialog (success or error)"""
        try:
            dialog = ResultsDialog(self.parent)
            
            if result.success:
                dialog.show_success(result, self.notification_settings)
            else:
                dialog.show_error(result.error_message, result.error_solution, bring_to_front=True)
                
        except Exception as e:
            # Fallback error display if results dialog fails
            self._show_error("Results Display Error", str(e), 
                           "Failed to show results. Processing may have completed successfully.")
    
    def _show_error(self, title: str, error_message: str, solution: str = ""):
        """Show a simple error dialog as fallback"""
        try:
            dialog = ResultsDialog(self.parent)
            dialog.show_error(error_message, solution, bring_to_front=True)
        except:
            # Ultimate fallback - basic messagebox
            import tkinter.messagebox as msgbox
            msgbox.showerror(title, f"{error_message}\n\nSuggested solution:\n{solution}")
    
    def _generate_error_solution(self, error_message: str) -> str:
        """Generate helpful error solutions based on error message content"""
        error_lower = error_message.lower()
        
        if "google drive" in error_lower and "404" in error_lower:
            return """1. Check if the Google Drive folder link is correct and accessible
2. Verify the folder is shared with your service account email  
3. Ensure the folder contains video files (.mp4 or .mov)
4. Try opening the Google Drive link in your browser to confirm access"""
        
        elif "google drive" in error_lower and "403" in error_lower:
            return """1. Check if your service account has permission to access the folder
2. Re-share the Google Drive folder with your service account email
3. Verify the service account credentials are correct
4. Make sure the folder is not restricted by organization policies"""
        
        elif "trello" in error_lower:
            return """1. Verify your Trello API key and token are correct
2. Check if the Trello card ID exists and is accessible
3. Ensure the Trello card has a proper description with Google Drive link
4. Try refreshing your Trello API credentials"""
        
        elif "ffmpeg" in error_lower:
            return """1. Ensure FFmpeg is installed and available in your system PATH
2. Check if input video files are not corrupted
3. Verify you have enough disk space for processing
4. Try processing with smaller video files first"""
        
        elif "timeout" in error_lower or "stuck" in error_lower:
            return """1. Check your internet connection stability
2. Try with smaller video files to test connectivity
3. Ensure Google Drive links are accessible
4. Restart the application and try again"""
        
        elif "permission" in error_lower or "access" in error_lower:
            return """1. Run the application as administrator if needed
2. Check file and folder permissions
3. Ensure output directory is writable
4. Verify service account credentials have proper access"""
        
        else:
            return """1. Check your internet connection
2. Verify all API credentials are correct
3. Ensure input files and links are accessible
4. Try restarting the application
5. Check the error log for more details"""

# Integration helper functions for easy use with existing orchestrator

def create_confirmation_data_from_orchestrator(card_data: dict, 
                                             processing_mode: str,
                                             project_info: dict,
                                             downloaded_videos: list,
                                             validation_issues: list = None) -> ConfirmationData:
    """
    Helper function to convert orchestrator data into ConfirmationData format.
    Makes it easy to integrate with existing main_orchestrator.py
    """
    
    # Extract project details
    project_name = project_info.get('project_name', 'Unknown Project')
    account = f"{project_info.get('account_code', 'Unknown')} Account"
    platform = "YouTube"  # Default, could be extracted from card or config
    
    # Determine templates to add based on processing mode
    templates = []
    if processing_mode == "connector_quiz":
        templates = [
            "Add Blake connector (YT/Connectors/)",
            "Add quiz outro (YT/Quiz/)",
            "Apply slide transition effects"
        ]
    elif processing_mode == "quiz_only":
        templates = [
            "Add quiz outro (YT/Quiz/)",
            "Apply slide transition effects"  
        ]
    elif processing_mode == "save_only":
        templates = ["Save and rename videos"]
    
    # Generate output location
    output_location = f"GH {project_name} {project_info.get('ad_type', '')} {project_info.get('test_name', '')} Quiz"
    
    # Estimate processing time based on file count and mode
    file_count = len(downloaded_videos)
    if processing_mode == "save_only":
        estimated_time = f"{file_count * 30} seconds - {file_count * 60} seconds"
    else:
        estimated_time = f"{file_count * 2}-{file_count * 3} minutes"
    
    # Calculate file sizes (placeholder - would need actual file size calculation)
    file_sizes = [(os.path.basename(video), 150) for video in downloaded_videos]  # Default 150MB
    
    # Convert validation issues
    issues = []
    if validation_issues:
        for issue in validation_issues:
            issues.append(ValidationIssue(
                severity=issue.get('severity', 'info'),
                message=issue.get('message', str(issue))
            ))
    
    return ConfirmationData(
        project_name=project_name,
        account=account,
        platform=platform,
        processing_mode=processing_mode.replace('_', ' ').upper(),
        client_videos=[os.path.basename(video) for video in downloaded_videos],
        templates_to_add=templates,
        output_location=output_location,
        estimated_time=estimated_time,
        issues=issues,
        file_sizes=file_sizes
    )

def create_processing_result_from_orchestrator(processed_files: list,
                                             start_time: float,
                                             output_folder: str,
                                             success: bool = True) -> ProcessingResult:
    """
    Helper function to convert orchestrator results into ProcessingResult format.
    """
    
    duration_seconds = time.time() - start_time
    duration_minutes = int(duration_seconds // 60)
    duration_secs = int(duration_seconds % 60)
    duration_str = f"{duration_minutes} minutes {duration_secs} seconds"
    
    # Convert processed files to expected format
    result_files = []
    for file_info in processed_files:
        result_files.append({
            'version': file_info.get('version', 'v01'),
            'source_file': file_info.get('source_file', 'unknown'),
            'output_name': file_info.get('output_name', 'processed_video'),
            'description': file_info.get('description', 'Processed video'),
            'duration': file_info.get('duration', 'Unknown')
        })
    
    return ProcessingResult(
        success=success,
        duration=duration_str,
        processed_files=result_files,
        output_folder=output_folder
    )

# Example integration function - shows how to use with existing orchestrator
def integrate_with_existing_orchestrator(orchestrator_instance, trello_card_id: str):
    """
    Example of how to integrate the workflow controller with existing main_orchestrator.py
    This shows the integration pattern - you'd adapt this to your actual orchestrator.
    """
    
    def processing_callback(progress_callback):
        """Wrapper for existing orchestrator that provides progress updates"""
        
        # You would replace this with calls to your actual orchestrator methods
        # and add progress_callback calls at appropriate points
        
        progress_callback(10, "Fetching Trello card data...")
        # result = orchestrator_instance._fetch_and_validate_card(trello_card_id)
        
        progress_callback(30, "Downloading videos from Google Drive...")
        # videos = orchestrator_instance._setup_project(card_data, project_info)
        
        progress_callback(60, "Processing videos with FFmpeg...")
        # processed = orchestrator_instance._process_videos(videos, ...)
        
        progress_callback(90, "Logging results to Google Sheets...")
        # orchestrator_instance._finalize_and_cleanup(processed, ...)
        
        progress_callback(100, "Processing complete!")
        
        # Return the results in the expected format
        return ProcessingResult(
            success=True,
            duration="2 minutes 34 seconds", 
            processed_files=[],  # Your actual processed files
            output_folder="C:\\Users\\Desktop\\Output"  # Your actual output folder
        )
    
    # Create workflow controller
    controller = AutomationWorkflowController()
    
    # Create confirmation data (you'd get this from your orchestrator)
    confirmation_data = ConfirmationData(
        project_name="Example Project",
        account="OO (Olive Oil)",
        platform="YouTube",
        processing_mode="CONNECTOR + QUIZ",
        client_videos=["video1.mp4", "video2.mp4"],
        templates_to_add=["Add connector", "Add quiz outro"],
        output_location="Desktop/Output",
        estimated_time="3-5 minutes",
        issues=[],
        file_sizes=[("video1.mp4", 200), ("video2.mp4", 350)]
    )
    
    # Start the workflow
    success = controller.start_workflow(
        confirmation_data=confirmation_data,
        processing_callback=processing_callback,
        estimated_duration="3-5 minutes"
    )
    
    return success

# Test function for the complete workflow
def test_complete_workflow():
    """Test the complete workflow with simulated data"""
    
    def mock_processing_callback(progress_callback):
        """Mock processing that simulates real work"""
        import time
        
        steps = [
            (15, "Validating inputs..."),
            (30, "Downloading video files..."),
            (50, "Processing video 1 of 2..."),
            (70, "Processing video 2 of 2..."),
            (85, "Applying effects and transitions..."),
            (95, "Saving outputs..."),
            (100, "Complete!")
        ]
        
        for progress, message in steps:
            progress_callback(progress, message)
            time.sleep(1)  # Simulate work
        
        # Return successful result
        return ProcessingResult(
            success=True,
            duration="2 minutes 15 seconds",
            processed_files=[
                {
                    'version': 'v01',
                    'source_file': 'test_video1.mp4',
                    'output_name': 'GH-testproject_v01-m01-f00-c00',
                    'description': 'Test video with connector and quiz',
                    'duration': '1:45'
                }
            ],
            output_folder=r"C:\Users\Desktop\Test Output Folder"
        )
    
    # Create test data
    test_data = ConfirmationData(
        project_name="Test Project VTD 12345",
        account="OO (Olive Oil)",
        platform="YouTube",
        processing_mode="CONNECTOR + QUIZ",
        client_videos=["test_video1.mp4", "test_video2.mp4"],
        templates_to_add=[
            "Add Blake connector (YT/Connectors/)",
            "Add quiz outro (YT/Quiz/)",
            "Apply slide transition effects"
        ],
        output_location="Test Project VTD 12345 Quiz",
        estimated_time="2-3 minutes",
        issues=[
            ValidationIssue("info", "Processing will create high-quality output")
        ],
        file_sizes=[("test_video1.mp4", 250), ("test_video2.mp4", 1200)]  # One large file
    )
    
    # Start the workflow
    controller = AutomationWorkflowController()
    success = controller.start_workflow(
        confirmation_data=test_data,
        processing_callback=mock_processing_callback,
        estimated_duration="2-3 minutes"
    )
    
    print(f"Workflow completed: {'Success' if success else 'Cancelled/Failed'}")
    return success

if __name__ == "__main__":
    # Test the complete workflow
    test_complete_workflow()