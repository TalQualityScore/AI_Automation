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