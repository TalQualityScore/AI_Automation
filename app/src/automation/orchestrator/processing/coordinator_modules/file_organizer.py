# app/src/automation/orchestrator/processing/coordinator_modules/file_organizer.py
"""
File Organizer Module
Moves and organizes video files
"""

import os
import shutil

class FileOrganizer:
    """Organizes and moves video files to appropriate locations"""
    
    def __init__(self):
        self.moved_count = 0
        self.failed_moves = []
    
    def move_videos_to_client_folder(self, video_files, source_dir, dest_dir):
        """
        Move video files from source to destination
        
        Args:
            video_files: List of video filenames
            source_dir: Source directory path
            dest_dir: Destination directory path
            
        Returns:
            Tuple of (moved_count, failed_moves)
        """
        if not video_files:
            print("⚠️ No video files to move")
            return 0, []
        
        self.moved_count = 0
        self.failed_moves = []
        
        for filename in video_files:
            success = self._move_single_file(filename, source_dir, dest_dir)
            if success:
                self.moved_count += 1
        
        return self.moved_count, self.failed_moves
    
    def _move_single_file(self, filename, source_dir, dest_dir):
        """Move a single file with error handling"""
        source_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(dest_dir, filename)
        
        try:
            # Check if source exists
            if not os.path.exists(source_path):
                print(f"⚠️ Source file not found: {source_path}")
                return False
            
            # Handle destination conflicts
            dest_path = self._handle_destination_conflict(dest_path, filename, dest_dir)
            
            # Perform the move
            shutil.move(source_path, dest_path)
            print(f"📁 ✅ Moved: {filename} → _Footage/Video/Client/")
            return True
            
        except Exception as e:
            print(f"❌ Failed to move {filename}: {e}")
            self.failed_moves.append((filename, str(e)))
            return False
    
    def _handle_destination_conflict(self, dest_path, filename, dest_dir):
        """Handle case where destination file already exists"""
        if not os.path.exists(dest_path):
            return dest_path
        
        # Create unique name
        base, ext = os.path.splitext(filename)
        counter = 1
        
        while os.path.exists(dest_path):
            new_name = f"{base}_{counter}{ext}"
            dest_path = os.path.join(dest_dir, new_name)
            counter += 1
        
        print(f"   Destination exists, using: {os.path.basename(dest_path)}")
        return dest_path
    
    def get_summary(self):
        """Get movement summary"""
        return {
            'moved': self.moved_count,
            'failed': len(self.failed_moves),
            'failed_details': self.failed_moves
        }