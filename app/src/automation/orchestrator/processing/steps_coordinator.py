# app/src/automation/orchestrator/processing/steps_coordinator.py
"""
Main ProcessingSteps coordinator class
Orchestrates all processing steps using specialized modules
"""

from .project_setup import ProjectSetup
from .video_processor import VideoProcessor
from .sheets_writer import SheetsWriter
from .video_sorter import VideoSorter

class ProcessingSteps:
    """Coordinates all processing steps for the orchestrator"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        
        # Initialize specialized modules
        self.project_setup = ProjectSetup(orchestrator)
        self.video_processor = VideoProcessor(orchestrator)
        self.sheets_writer = SheetsWriter(orchestrator)
        self.video_sorter = VideoSorter()
    
    def fetch_and_validate_card(self, trello_card_id):
        """Step 1: Fetch Trello card and validate basic data"""
        return self.project_setup.fetch_and_validate_card(trello_card_id)
    
    def parse_and_validate(self, card_data):
        """Step 2: Parse instructions and validate assets"""
        return self.project_setup.parse_and_validate(card_data)
    
    def download_and_setup(self, card_data, project_info):
        """Step 3: Download videos and set up project structure"""
        return self.project_setup.download_and_setup(card_data, project_info)
    
    def process_videos(self, client_videos, project_paths, project_info, processing_mode, creds):
        """Step 4: Process all videos based on mode"""
        # Sort videos first
        sorted_videos = self.video_sorter.sort_videos_by_version_letter(client_videos)
        
        # Process them
        return self.video_processor.process_all_videos(
            sorted_videos, project_paths, project_info, processing_mode, creds
        )
    
    def process_single_video(self, client_video, project_paths, project_info, processing_mode, 
                           version_num, target_width, target_height):
        """Process a single video file"""
        return self.video_processor.process_single_video(
            client_video, project_paths, project_info, processing_mode,
            version_num, target_width, target_height
        )
    
    def write_to_sheets(self, project_info, processed_files, creds):
        """Step 5: Write results to Google Sheets"""
        return self.sheets_writer.write_to_sheets(project_info, processed_files, creds)
    
    # Utility methods for backward compatibility
    def extract_version_letter(self, filename):
        """Extract version letter from filename"""
        return self.video_sorter.extract_version_letter(filename)
    
    def sort_videos_by_version_letter(self, videos):
        """Sort videos by version letter"""
        return self.video_sorter.sort_videos_by_version_letter(videos)
    
    def finalize_and_cleanup(self, processed_files, project_info, creds, project_paths):
        """Step 6: Move downloaded videos and cleanup temp files"""
        print("\n--- Step 6: Organizing Files & Cleanup ---")
        
        try:
            # Import the cleanup utilities
            import os
            import shutil
            from ...api_clients.config import DOWNLOADS_DIR
            
            # Get the client videos folder path
            client_videos_path = project_paths.get('client_videos')
            if not client_videos_path:
                print("⚠️ Client videos path not found, skipping file organization")
                return
            
            # Check if temp downloads directory exists
            if not os.path.exists(DOWNLOADS_DIR):
                print("⚠️ No temp downloads found, skipping cleanup")
                return
            
            # Move all downloaded videos to _Footage/Video/Client
            moved_count = 0
            for filename in os.listdir(DOWNLOADS_DIR):
                if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
                    source_path = os.path.join(DOWNLOADS_DIR, filename)
                    dest_path = os.path.join(client_videos_path, filename)
                    
                    try:
                        shutil.move(source_path, dest_path)
                        print(f"📁 Moved: {filename} → _Footage/Video/Client/")
                        moved_count += 1
                    except Exception as move_error:
                        print(f"⚠️ Could not move {filename}: {move_error}")
            
            # Clean up temp directory
            try:
                if os.path.exists(DOWNLOADS_DIR):
                    shutil.rmtree(DOWNLOADS_DIR)
                    print(f"🧹 Cleaned up temp downloads directory")
            except Exception as cleanup_error:
                print(f"⚠️ Could not clean up temp directory: {cleanup_error}")
            
            print(f"✅ File organization complete: {moved_count} videos moved to project folder")
            
        except Exception as e:
            print(f"⚠️ Error during file organization: {e}")
            # Don't fail the entire automation for cleanup issues
