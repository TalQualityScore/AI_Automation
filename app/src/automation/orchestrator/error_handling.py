# app/src/automation/orchestrator/error_handling.py
from datetime import datetime

class ErrorHandler:
    """Handles error processing and solution generation for the orchestrator"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def generate_error_solution(self, error_message: str) -> str:
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
    
    def handle_automation_error(self, error, trello_card_id):
        """Handle and log errors with detailed information"""
        print("\n" + "="*60)
        print("❌ AUTOMATION FAILED")
        print("="*60)
        print(f"Error: {str(error)}")
        print(f"Card ID: {trello_card_id}")
        
        # Log error for debugging
        error_log_path = "automation_error.log"
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(f"Card ID: {trello_card_id}\n")
            f.write(f"Error: {str(error)}\n")
        
        print(f"📝 Error logged to: {error_log_path}")