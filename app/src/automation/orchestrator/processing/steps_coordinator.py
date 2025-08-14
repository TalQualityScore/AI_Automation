# app/src/automation/orchestrator/processing/steps_coordinator.py - REFACTORED
"""
Main ProcessingSteps coordinator class - REFACTORED
Now uses modular components for file organization
"""

from .project_setup import ProjectSetup
from .video_processor import VideoProcessingOrchestrator
from .sheets_writer import SheetsWriter
from .video_sorter import VideoSorter
from .coordinator_modules import (
    PathResolver,
    FileOrganizer,
    CleanupManager,
    DownloadFinder,
    SummaryReporter
)

class ProcessingSteps:
    """Coordinates all processing steps for the orchestrator - REFACTORED"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        
        # Initialize specialized modules
        self.project_setup = ProjectSetup(orchestrator)
        self.video_processor = VideoProcessingOrchestrator(orchestrator)
        self.sheets_writer = SheetsWriter(orchestrator)
        self.video_sorter = VideoSorter()
        
        # Initialize coordinator modules
        self.path_resolver = PathResolver(orchestrator)
        self.file_organizer = FileOrganizer()
        self.cleanup_manager = CleanupManager()
        self.download_finder = DownloadFinder()
        self.summary_reporter = SummaryReporter()
    
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
    
    def write_to_sheets(self, project_info, processed_files, creds, current_mode=None):
        """Step 5: Write results to Google Sheets"""
        return self.sheets_writer.write_to_sheets(project_info, processed_files, creds, current_mode)
    
    def finalize_and_cleanup(self, processed_files, project_info, creds, project_paths):
        """
        Step 6: Organize files and cleanup - REFACTORED
        Now ~40 lines instead of 174 lines
        """
        print("\n--- Step 6: Organizing Files & Cleanup ---")
        
        try:
            # Import config for downloads directory
            from ...api_clients.config import DOWNLOADS_DIR
            
            # Step 1: Resolve client videos path
            client_videos_path = self.path_resolver.resolve_client_videos_path(project_paths)
            if not client_videos_path:
                print("❌ Could not resolve client videos path, skipping file organization")
                return
            
            # Ensure client directory exists
            self.path_resolver.ensure_directory_exists(client_videos_path)
            
            # Step 2: Find downloads directory
            downloads_path = self.download_finder.find_downloads_directory(DOWNLOADS_DIR)
            if not downloads_path:
                print("❌ No downloads directory found, skipping cleanup")
                return
            
            # Step 3: Find video files to move
            video_files = self.download_finder.list_video_files(downloads_path)
            if not video_files:
                # Try to clean up empty directory anyway
                self.cleanup_manager.cleanup_directory(downloads_path)
                return
            
            # Step 4: Move video files
            moved_count, failed_moves = self.file_organizer.move_videos_to_client_folder(
                video_files, downloads_path, client_videos_path
            )
            
            # Step 5: Clean up downloads directory
            self.cleanup_manager.cleanup_directory(downloads_path)
            
            # Step 6: Generate summary
            self.summary_reporter.generate_summary(
                moved_count, failed_moves, client_videos_path
            )
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR during file organization: {e}")
            import traceback
            print(f"   Full traceback: {traceback.format_exc()}")
            # Don't fail the entire automation for cleanup issues
    
    # Utility methods for backward compatibility
    def extract_version_letter(self, filename):
        """Extract version letter from filename"""
        return self.video_sorter.extract_version_letter(filename)
    
    def sort_videos_by_version_letter(self, videos):
        """Sort videos by version letter"""
        return self.video_sorter.sort_videos_by_version_letter(videos)