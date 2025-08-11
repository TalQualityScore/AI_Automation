# app/src/automation/orchestrator/processing/coordinator_modules/cleanup_manager.py
"""
Cleanup Manager Module
Handles cleanup of temporary directories
"""

import os
import shutil

class CleanupManager:
    """Manages cleanup of temporary files and directories"""
    
    def cleanup_directory(self, directory_path):
        """
        Clean up a directory if empty
        
        Args:
            directory_path: Path to directory to clean
            
        Returns:
            True if cleaned, False otherwise
        """
        if not directory_path or not os.path.exists(directory_path):
            return False
        
        try:
            # Check if directory is empty
            remaining_files = os.listdir(directory_path)
            
            if not remaining_files:
                shutil.rmtree(directory_path)
                print(f"🧹 ✅ Cleaned up downloads directory")
                return True
            else:
                print(f"⚠️ Directory not empty, contains: {remaining_files}")
                return False
                
        except Exception as e:
            print(f"⚠️ Could not clean up directory: {e}")
            return False
    
    def cleanup_empty_directories(self, directories):
        """
        Clean up multiple directories if empty
        
        Args:
            directories: List of directory paths
            
        Returns:
            Number of directories cleaned
        """
        cleaned = 0
        
        for directory in directories:
            if self.cleanup_directory(directory):
                cleaned += 1
        
        return cleaned