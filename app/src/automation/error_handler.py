# app/src/automation/error_handler.py
"""
Unified error handling system for the entire application
Single source of truth for error handling and solution generation
"""

import sys
import traceback
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import Optional, Dict, Any

class ErrorHandler:
    """Unified error handler for the entire application"""
    
    def __init__(self):
        self.last_error: Optional[Exception] = None
        self.error_count: int = 0
        
    def handle_error(self, error: Exception, context: str = "Unknown", 
                    show_dialog: bool = True) -> str:
        """
        Handle an error with appropriate logging and user feedback
        
        Args:
            error: The exception that occurred
            context: Context where the error occurred
            show_dialog: Whether to show a dialog to the user
            
        Returns:
            Solution text for the error
        """
        self.last_error = error
        self.error_count += 1
        
        error_message = str(error)
        solution = self.generate_error_solution(error_message)
        
        # Log the error
        print(f"\n❌ ERROR in {context}:")
        print(f"   {error_message}")
        if solution:
            print(f"\n💡 Suggested solution:")
            print(f"   {solution}")
        
        # Show dialog if requested
        if show_dialog:
            self.show_error_dialog(error, context, solution)
        
        return solution
    
    def generate_error_solution(self, error_message: str) -> str:
        """
        Generate helpful error solutions based on error message content
        
        Args:
            error_message: The error message to analyze
            
        Returns:
            Suggested solution for the error
        """
        error_lower = error_message.lower()
        
        # Google Drive errors
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
        
        # Trello errors
        elif "trello" in error_lower:
            if "401" in error_lower or "unauthorized" in error_lower:
                return """1. Verify your Trello API key is correct
2. Check that your Trello token hasn't expired
3. Regenerate your Trello credentials at https://trello.com/app-key
4. Update the .env file with new credentials"""
            else:
                return """1. Verify your Trello API key and token are correct
2. Check if the Trello card ID exists and is accessible
3. Ensure the Trello card has a proper description with Google Drive link
4. Try refreshing your Trello API credentials"""
        
        # FFmpeg errors
        elif "ffmpeg" in error_lower:
            if "not found" in error_lower or "not recognized" in error_lower:
                return """1. Install FFmpeg from https://ffmpeg.org/download.html
2. Add FFmpeg to your system PATH
3. Restart your terminal/IDE after installation
4. Verify installation with 'ffmpeg -version' command"""
            else:
                return """1. Ensure FFmpeg is installed and available in your system PATH
2. Check if input video files are not corrupted
3. Verify you have enough disk space for processing
4. Try processing with smaller video files first"""
        
        # Timeout errors
        elif "timeout" in error_lower or "stuck" in error_lower:
            return """1. Check your internet connection stability
2. Try with smaller video files to test connectivity
3. Ensure Google Drive links are accessible
4. Increase timeout values in configuration
5. Restart the application and try again"""
        
        # Permission errors
        elif "permission" in error_lower or "access" in error_lower:
            return """1. Run the application as administrator if needed
2. Check file and folder permissions
3. Ensure output directory is writable
4. Verify service account credentials have proper access"""
        
        # Network errors
        elif "connection" in error_lower or "network" in error_lower:
            return """1. Check your internet connection
2. Verify firewall settings aren't blocking the app
3. Check if VPN is interfering with connections
4. Try again after a few moments"""
        
        # File not found
        elif "file not found" in error_lower or "no such file" in error_lower:
            return """1. Verify the file path is correct
2. Check if the file was moved or deleted
3. Ensure you have read permissions for the file
4. Check if the path contains special characters"""
        
        # Memory errors
        elif "memory" in error_lower or "ram" in error_lower:
            return """1. Close unnecessary applications
2. Process smaller video files
3. Reduce video quality settings
4. Restart your computer to free up memory"""
        
        # Generic fallback
        else:
            return """1. Check your internet connection
2. Verify all API credentials are correct
3. Ensure input files and links are accessible
4. Check available disk space
5. Try restarting the application
6. Check the logs for more details"""
    
    def show_error_dialog(self, error: Exception, context: str, solution: str):
        """Show error dialog with copy-to-clipboard functionality"""
        try:
            root = tk.Tk()
            root.withdraw()
            
            # Create error details
            error_details = f"""Error Context: {context}
Error Type: {type(error).__name__}
Error Message: {str(error)}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Suggested Solution:
{solution}

Full Traceback:
{traceback.format_exc()}"""
            
            # Show message box
            result = messagebox.showerror(
                f"Error in {context}",
                f"{str(error)}\n\nClick OK to copy error details to clipboard.",
                parent=root
            )
            
            # Copy to clipboard
            self.copy_to_clipboard(error_details)
            
            root.destroy()
            
        except Exception as e:
            print(f"Could not show error dialog: {e}")
    
    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        try:
            # Try using pyperclip if available
            import pyperclip
            pyperclip.copy(text)
            print("✅ Error details copied to clipboard")
        except ImportError:
            # Fallback to tkinter clipboard
            try:
                root = tk.Tk()
                root.withdraw()
                root.clipboard_clear()
                root.clipboard_append(text)
                root.update()
                root.destroy()
                print("✅ Error details copied to clipboard")
            except Exception as e:
                print(f"Could not copy to clipboard: {e}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "error_count": self.error_count,
            "last_error": str(self.last_error) if self.last_error else None
        }
    
    def reset_stats(self):
        """Reset error statistics"""
        self.error_count = 0
        self.last_error = None

# Global error handler instance - single source of truth
error_handler = ErrorHandler()

# Convenience functions for backward compatibility
def handle_error(error: Exception, context: str = "Unknown", show_dialog: bool = True) -> str:
    """Handle an error using the global error handler"""
    return error_handler.handle_error(error, context, show_dialog)

def generate_error_solution(error_message: str) -> str:
    """Generate error solution using the global error handler"""
    return error_handler.generate_error_solution(error_message)