# app/src/automation/workflow_ui_components/helpers.py
import os
import subprocess
import platform
from tkinter import messagebox

def open_folder(folder_path: str):
    """Open output folder in file explorer"""
    try:
        if platform.system() == "Windows":
            os.startfile(folder_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", folder_path])
        else:  # Linux
            subprocess.run(["xdg-open", folder_path])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open folder:\n{e}")

def copy_to_clipboard(root, text: str):
    """Copy text to clipboard"""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        messagebox.showinfo("Copied", "Error details copied to clipboard!")
    except Exception as e:
        messagebox.showerror("Error", f"Could not copy to clipboard:\n{e}")

def generate_error_solution(error_message: str) -> str:
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