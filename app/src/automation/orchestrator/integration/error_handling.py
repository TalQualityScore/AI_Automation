# app/src/automation/orchestrator/integration/error_handling.py
"""
Integration Error Handling - Centralized error management
Extracted from ui_integration_base.py for better error handling
"""

import traceback
from ...workflow_data_models import ProcessingResult

class IntegrationErrorHandler:
    """Centralized error handling for integration processes"""
    
    def __init__(self, ui_integration):
        self.ui = ui_integration
        self.orchestrator = ui_integration.orchestrator
    
    def handle_processing_error(self, error):
        """Handle general processing errors with specific solutions"""
        
        print(f"❌ PROCESSING ERROR: {error}")
        traceback.print_exc()
        
        # Analyze error type and provide specific solutions
        error_str = str(error).lower()
        
        if "video dimensions" in error_str:
            return self._handle_video_dimension_error(error)
        elif "ffmpeg" in error_str or "ffprobe" in error_str:
            return self._handle_ffmpeg_error(error)
        elif "google" in error_str and "api" in error_str:
            return self._handle_google_api_error(error)
        elif "permission" in error_str or "access" in error_str:
            return self._handle_permission_error(error)
        elif "network" in error_str or "connection" in error_str:
            return self._handle_network_error(error)
        elif "file not found" in error_str or "path" in error_str:
            return self._handle_file_error(error)
        else:
            return self._handle_generic_error(error)
    
    def _handle_video_dimension_error(self, error):
        """Handle video dimension analysis errors"""
        return ProcessingResult(
            success=False,
            duration='',
            processed_files=[],
            output_folder='',
            error_message="Video dimension analysis failed",
            error_solution=(
                "VIDEO DIMENSION FIX:\n"
                "1. Check FFmpeg installation: Run 'ffmpeg -version' in command prompt\n"
                "2. Verify video file isn't corrupted\n"
                "3. Try with a different video file\n"
                "4. Check if video path contains special characters\n"
                "5. Install/reinstall FFmpeg from https://ffmpeg.org/download.html\n"
                "6. Ensure FFmpeg is in your system PATH\n\n"
                "QUICK FIX: Place ffmpeg.exe in the same folder as your application"
            )
        )
    
    def _handle_ffmpeg_error(self, error):
        """Handle FFmpeg-related errors"""
        return ProcessingResult(
            success=False,
            duration='',
            processed_files=[],
            output_folder='',
            error_message="FFmpeg processing error",
            error_solution=(
                "FFMPEG INSTALLATION FIX:\n"
                "1. Download FFmpeg from https://ffmpeg.org/download.html\n"
                "2. Extract ffmpeg.exe to your application folder\n"
                "3. OR add FFmpeg to your system PATH\n"
                "4. Restart the application\n"
                "5. Test with: 'ffmpeg -version' in command prompt\n\n"
                "ALTERNATIVE: Use portable FFmpeg in app folder"
            )
        )
    
    def _handle_google_api_error(self, error):
        """Handle Google API errors"""
        return ProcessingResult(
            success=False,
            duration='',
            processed_files=[],
            output_folder='',
            error_message="Google API connection failed",
            error_solution=(
                "GOOGLE API FIX:\n"
                "1. Check your internet connection\n"
                "2. Verify credentials.json file exists and is valid\n"
                "3. Re-authenticate Google Drive access\n"
                "4. Check Google Drive folder permissions\n"
                "5. Ensure Google Drive API is enabled\n"
                "6. Try refreshing your authentication tokens"
            )
        )
    
    def _handle_permission_error(self, error):
        """Handle permission and access errors"""
        return ProcessingResult(
            success=False,
            duration='',
            processed_files=[],
            output_folder='',
            error_message="Permission or access denied",
            error_solution=(
                "PERMISSION FIX:\n"
                "1. Run the application as Administrator\n"
                "2. Check folder write permissions\n"
                "3. Ensure no files are open in other applications\n"
                "4. Check antivirus software isn't blocking access\n"
                "5. Verify Google Drive folder sharing permissions\n"
                "6. Close any video editing software that might lock files"
            )
        )
    
    def _handle_network_error(self, error):
        """Handle network and connection errors"""
        return ProcessingResult(
            success=False,
            duration='',
            processed_files=[],
            output_folder='',
            error_message="Network connection error",
            error_solution=(
                "NETWORK FIX:\n"
                "1. Check your internet connection\n"
                "2. Try again in a few minutes (temporary outage)\n"
                "3. Check if firewall is blocking the application\n"
                "4. Verify proxy settings if applicable\n"
                "5. Try using a different network connection\n"
                "6. Check Google Drive service status"
            )
        )
    
    def _handle_file_error(self, error):
        """Handle file system errors"""
        return ProcessingResult(
            success=False,
            duration='',
            processed_files=[],
            output_folder='',
            error_message="File system error",
            error_solution=(
                "FILE SYSTEM FIX:\n"
                "1. Check if all files exist and are accessible\n"
                "2. Verify folder paths don't contain special characters\n"
                "3. Ensure sufficient disk space\n"
                "4. Check if files are locked by other applications\n"
                "5. Try moving files to a simpler path (no spaces/symbols)\n"
                "6. Verify read/write permissions on all folders"
            )
        )
    
    def _handle_generic_error(self, error):
        """Handle generic errors"""
        return ProcessingResult(
            success=False,
            duration='',
            processed_files=[],
            output_folder='',
            error_message=str(error),
            error_solution=(
                "GENERAL TROUBLESHOOTING:\n"
                "1. Restart the application\n"
                "2. Check your internet connection\n"
                "3. Verify all API credentials are correct\n"
                "4. Ensure input files and links are accessible\n"
                "5. Check the error log for more details\n"
                "6. Try with a smaller/simpler test case\n"
                "7. Contact support if the problem persists"
            )
        )
    
    def log_error_details(self, error, context=""):
        """Log detailed error information for debugging"""
        print(f"\n{'='*80}")
        print(f"🔍 ERROR ANALYSIS - {context}")
        print(f"{'='*80}")
        print(f"Error Type: {type(error).__name__}")
        print(f"Error Message: {str(error)}")
        print(f"Traceback:")
        traceback.print_exc()
        
        # Log orchestrator state
        if hasattr(self.orchestrator, 'project_info'):
            print(f"\nProject Info: {self.orchestrator.project_info}")
        if hasattr(self.orchestrator, 'processing_mode'):
            print(f"Processing Mode: {self.orchestrator.processing_mode}")
        if hasattr(self.orchestrator, 'downloaded_videos'):
            print(f"Downloaded Videos: {len(self.orchestrator.downloaded_videos) if self.orchestrator.downloaded_videos else 0}")
        
        print(f"{'='*80}")
    
    def create_recovery_suggestions(self, error_type):
        """Create specific recovery suggestions based on error type"""
        
        suggestions = {
            "video_dimension": [
                "Install FFmpeg properly",
                "Check video file integrity", 
                "Use fallback dimensions",
                "Try with different video format"
            ],
            "ffmpeg": [
                "Install/reinstall FFmpeg",
                "Add FFmpeg to PATH",
                "Use portable FFmpeg build",
                "Check FFmpeg permissions"
            ],
            "google_api": [
                "Re-authenticate Google Drive",
                "Check credentials.json",
                "Verify API quotas",
                "Check network connectivity"
            ],
            "permission": [
                "Run as Administrator",
                "Check file permissions",
                "Close conflicting applications",
                "Check antivirus settings"
            ]
        }
        
        return suggestions.get(error_type, ["Contact support for assistance"])