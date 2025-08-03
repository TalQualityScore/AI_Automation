# app/src/automation/main_orchestrator.py
import os
import shutil
import sys
import traceback
from datetime import datetime

# Import existing modules
from .api_clients import (get_trello_card_data, download_files_from_gdrive, 
                         write_to_google_sheets, get_google_creds)
from .video_processor import get_video_dimensions, process_video_sequence
from .workflow_utils import parse_project_info, create_project_structure
from .timing_report import generate_timing_report, prepare_video_sequence_info
from ..naming_generator import generate_project_folder_name, generate_output_name, get_image_description

# Import new modular components
from .robust_monitoring import RobustMonitoringSystem
from .validation_engine import ValidationEngine
from .instruction_parser import InstructionParser

class AutomationOrchestrator:
    """Clean orchestrator that delegates to specialized modules"""
    
    def __init__(self):
        self.monitor = RobustMonitoringSystem()
        self.validator = ValidationEngine()
        self.parser = InstructionParser()
    
    def execute(self, trello_card_id):
        """Main execution flow with clean separation of concerns"""
        
        try:
            print("🚀 Starting AI Automation with Enhanced Monitoring")
            print(f"Card ID: {trello_card_id}")
            print("="*60)
            
            # Step 1: Fetch and Validate Card Data
            card_data = self._fetch_and_validate_card(trello_card_id)
            
            # Step 2: Parse Instructions and Validate Assets
            processing_mode, project_info = self._parse_and_validate(card_data)
            
            # Step 3: Setup Project and Download Files
            creds, downloaded_videos, project_paths = self._setup_project(card_data, project_info)
            
            # Step 4: Process Videos
            processed_files = self._process_videos(
                downloaded_videos, project_paths, project_info, 
                processing_mode, creds
            )
            
            # Step 5: Log Results and Cleanup
            self._finalize_and_cleanup(processed_files, project_info, creds, project_paths)
            
            print("\n" + "="*60)
            print("🎉 Automation finished successfully!")
            print(f"📁 Project folder: {project_paths['project_root']}")
            print(f"📊 Processed {len(processed_files)} video(s)")
            print("="*60)
            
        except Exception as e:
            self._handle_error(e, trello_card_id)
    
    def _fetch_and_validate_card(self, trello_card_id):
        """Step 1: Fetch Trello card and validate basic data"""
        print("\n--- Step 1: Fetching Trello & Parsing Project Info ---")
        
        def fetch_card_data():
            card_data, error = get_trello_card_data(trello_card_id)
            if error:
                raise Exception(f"Failed to fetch Trello card: {error}")
            return card_data
        
        card_data = self.monitor.execute_with_activity_monitoring(
            fetch_card_data, 
            "Trello Card Fetch", 
            no_activity_timeout=60
        )
        
        # Validate card data
        validation_issues = self.validator.validate_trello_card(card_data)
        
        if not self.validator.show_validation_results(validation_issues):
            raise Exception("Validation failed - cannot proceed")
        
        return card_data
    
    def _parse_and_validate(self, card_data):
        """Step 2: Parse instructions and validate assets"""
        
        # Parse processing mode
        processing_mode = self.parser.parse_card_instructions(card_data.get('desc', ''))
        print(f"Processing mode detected: {processing_mode}")
        
        # Validate required assets
        asset_issues = self.validator.validate_assets(processing_mode)
        
        if not self.validator.show_validation_results(asset_issues):
            raise Exception("Asset validation failed - cannot proceed")
        
        # Parse project info
        def parse_project():
            project_info = parse_project_info(card_data['name'])
            if not project_info:
                raise Exception("Could not parse project info from card name")
            return project_info
        
        project_info = self.monitor.execute_with_activity_monitoring(
            parse_project,
            "Project Info Parsing",
            no_activity_timeout=30
        )
        
        print(f"Successfully parsed project: {project_info['project_name']}")
        print(f"Version letter: {project_info.get('version_letter', 'Not found')}")
        
        return processing_mode, project_info
    
    def _setup_project(self, card_data, project_info):
        """Step 3: Setup credentials, download files, create project structure"""
        print("\n--- Step 2: Downloading & Setting Up Project ---")
        
        # Setup credentials
        def setup_credentials():
            creds = get_google_creds()
            if not creds:
                raise Exception("Google credentials not available")
            return creds
        
        creds = self.monitor.execute_with_activity_monitoring(
            setup_credentials,
            "Google Credentials Setup",
            no_activity_timeout=30
        )
        
        # Download videos
        def download_videos():
            gdrive_link = self.validator.extract_gdrive_link(card_data.get('desc', ''))
            downloaded_videos, error = download_files_from_gdrive(gdrive_link, creds, self.monitor)
            if error:
                raise Exception(f"Failed to download videos: {error}")
            if not downloaded_videos:
                raise Exception("No video files were downloaded")
            return downloaded_videos
        
        downloaded_videos = self.monitor.execute_with_activity_monitoring(
            download_videos,
            "Google Drive Download",
            no_activity_timeout=600  # 10 minutes of no download progress
        )
        
        # Create project structure
        naming_suffix = "quiz"
        project_folder_name = generate_project_folder_name(
            project_name=project_info['project_name'],
            first_client_video=downloaded_videos[0],
            ad_type_selection=naming_suffix.title()
        )
        project_paths = create_project_structure(project_folder_name)
        
        # Move files to project structure
        client_video_final_paths = []
        for video_path in downloaded_videos:
            final_path = os.path.join(project_paths['client_footage'], os.path.basename(video_path))
            shutil.move(video_path, final_path)
            client_video_final_paths.append(final_path)
        
        return creds, client_video_final_paths, project_paths
    
    def _process_videos(self, client_videos, project_paths, project_info, processing_mode, creds):
        """Step 4: Process all videos based on mode"""
        print(f"\n--- Step 4: Processing Videos ---")
        
        # Get video dimensions if needed
        if processing_mode != "save_only":
            def get_dimensions():
                target_width, target_height, error = get_video_dimensions(client_videos[0])
                if error:
                    raise Exception(f"Failed to get video dimensions: {error}")
                return target_width, target_height
            
            target_width, target_height = self.monitor.execute_with_activity_monitoring(
                get_dimensions,
                "Video Dimension Analysis",
                no_activity_timeout=60
            )
            print(f"Target resolution set to {target_width}x{target_height}")
        
        # Get starting version number
        concept_name = f"GH {project_info['project_name']} {project_info['ad_type']} {project_info['test_name']} Quiz"
        
        def check_sheets():
            error, start_version = write_to_google_sheets(concept_name, [], creds)
            if error:
                raise Exception(f"Failed to check Google Sheets: {error}")
            return start_version
        
        start_version = self.monitor.execute_with_activity_monitoring(
            check_sheets,
            "Google Sheets Version Check",
            no_activity_timeout=120
        )
        
        # Process each video
        processed_files = []
        for i, client_video in enumerate(client_videos):
            version_num = start_version + i
            print(f"\n--- Processing Version {version_num:02d} ({processing_mode}) ---")
            
            processed_file = self._process_single_video(
                client_video, project_paths, project_info, processing_mode,
                version_num, target_width if processing_mode != "save_only" else None,
                target_height if processing_mode != "save_only" else None
            )
            processed_files.append(processed_file)
        
        return processed_files
    
    def _process_single_video(self, client_video, project_paths, project_info, processing_mode, version_num, target_width, target_height):
        """Process a single video file"""
        
        image_desc = get_image_description(client_video)
        output_name = generate_output_name(
            project_name=project_info['project_name'], 
            first_client_video=client_video,
            ad_type_selection="quiz", 
            image_desc=image_desc, 
            version_num=version_num,
            version_letter=project_info.get('version_letter', '')
        )
        output_path = os.path.join(project_paths['ame'], f"{output_name}.mp4")
        
        if processing_mode == "save_only":
            def save_video():
                shutil.copy(client_video, output_path)
                return f"Saved: {output_name}.mp4"
            
            result = self.monitor.execute_with_activity_monitoring(
                save_video,
                f"Save Video v{version_num:02d}",
                no_activity_timeout=120
            )
            
            description = f"Saved as is from {os.path.basename(client_video)}"
        else:
            def process_video():
                error = process_video_sequence(client_video, output_path, target_width, target_height, processing_mode)
                if error:
                    raise Exception(f"Video processing failed: {error}")
                return f"Processed: {output_name}.mp4"
            
            result = self.monitor.execute_with_activity_monitoring(
                process_video,
                f"Process Video v{version_num:02d}",
                no_activity_timeout=1800  # 30 minutes of no FFmpeg progress
            )
            
            if processing_mode == "connector_quiz":
                description = f"New Ad from {os.path.basename(client_video)} + connector + quiz"
            else:
                description = f"New Ad from {os.path.basename(client_video)} + quiz"
        
        print(result)
        
        return {
            "version": f"v{version_num:02d}",
            "source_file": os.path.basename(client_video),
            "output_name": output_name,
            "description": description
        }
    
    def _finalize_and_cleanup(self, processed_files, project_info, creds, project_paths):
        """Step 5: Log results to Google Sheets and cleanup"""
        print("\n--- Step 5: Logging to Google Sheets ---")
        
        if processed_files:
            concept_name = f"GH {project_info['project_name']} {project_info['ad_type']} {project_info['test_name']} Quiz"
            data_to_write = [
                [pf['version'], pf['description'], pf['output_name']]
                for pf in processed_files
            ]
            
            def write_results():
                error, _ = write_to_google_sheets(concept_name, data_to_write, creds)
                if error:
                    raise Exception(f"Failed to write to Google Sheets: {error}")
                return "Results logged successfully"
            
            result = self.monitor.execute_with_activity_monitoring(
                write_results,
                "Google Sheets Logging",
                no_activity_timeout=120
            )
            print(result)
        else:
            print("No files were processed, skipping log.")
        
        # Cleanup temporary files
        print("\n--- Step 6: Cleaning up temporary files ---")
        temp_dir = "temp_downloads"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def _handle_error(self, error, trello_card_id):
        """Handle and log errors with detailed information"""
        print("\n" + "="*60)
        print("❌ AUTOMATION FAILED")
        print("="*60)
        print(f"Error: {str(error)}")
        print("\nFull error details:")
        print(traceback.format_exc())
        print("\n💡 Common solutions:")
        print("• Check your internet connection")
        print("• Verify Google Drive link is accessible")
        print("• Ensure all required asset files exist")
        print("• Check Trello card has proper title and description")
        print("="*60)
        
        # Log error for debugging
        error_log_path = "automation_error.log"
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(f"Card ID: {trello_card_id}\n")
            f.write(f"Error: {str(error)}\n")
            f.write(f"Traceback:\n{traceback.format_exc()}\n")
        
        print(f"📝 Error logged to: {error_log_path}")

def main(trello_card_id):
    """Main entry point for automation"""
    orchestrator = AutomationOrchestrator()
    orchestrator.execute(trello_card_id)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main_orchestrator.py <TRELLO_CARD_ID>")
        print("Example: python main_orchestrator.py 'abc123xyz'")
    else:
        main(sys.argv[1])