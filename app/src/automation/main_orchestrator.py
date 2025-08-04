# app/src/automation/main_orchestrator.py
import os
import shutil
import sys
import traceback
from datetime import datetime
import time

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

# Import UI components
from .unified_workflow_dialog import (UnifiedWorkflowDialog, create_confirmation_data_from_orchestrator, 
                                     create_processing_result_from_orchestrator)

class AutomationOrchestrator:
    """Enhanced orchestrator with UI integration"""
    
    def __init__(self):
        self.monitor = RobustMonitoringSystem()
        self.validator = ValidationEngine()
        self.parser = InstructionParser()
        self.trello_card_id = None
        self.start_time = None
        
        # Data for UI integration
        self.card_data = None
        self.processing_mode = None
        self.project_info = None
        self.downloaded_videos = None
        self.project_paths = None
        self.creds = None
        self.processed_files = None
    
    def execute_with_ui(self, trello_card_id=None):
        """Execute automation with UI workflow"""
        
        # If no card ID provided, show popup to get it
        if not trello_card_id:
            print("🎬 Starting AI Automation Suite - Getting Trello Card...")
            trello_card_id = UnifiedWorkflowDialog.get_trello_card_id()
            if not trello_card_id:
                print("❌ No Trello card ID provided. Automation cancelled.")
                return False
        
        self.trello_card_id = trello_card_id
        self.start_time = time.time()
        
        try:
            print("🚀 Starting AI Automation with UI Workflow")
            print(f"Card ID: {trello_card_id}")
            print("="*60)
            
            # Prepare data for confirmation dialog
            confirmation_data = self._prepare_confirmation_data()
            
            # Show unified workflow dialog
            dialog = UnifiedWorkflowDialog()
            success = dialog.show_workflow(
                confirmation_data=confirmation_data,
                processing_callback=self._ui_processing_callback
            )
            
            if success:
                print("\n" + "="*60)
                print("🎉 Automation completed successfully with UI!")
                print(f"📁 Project folder: {self.project_paths['project_root'] if self.project_paths else 'Unknown'}")
                print(f"📊 Processed {len(self.processed_files) if self.processed_files else 0} video(s)")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("❌ Automation cancelled by user")
                print("="*60)
            
            return success
            
        except Exception as e:
            self._handle_error(e, trello_card_id)
            return False
    
    def execute(self, trello_card_id):
        """Legacy headless execution - fallback for command line"""
        self.trello_card_id = trello_card_id
        self.start_time = time.time()
        
        try:
            print("🚀 Starting AI Automation (Headless Mode)")
            print(f"Card ID: {trello_card_id}")
            print("="*60)
            
            # Step 1: Fetch and Validate Card Data
            self.card_data = self._fetch_and_validate_card(trello_card_id)
            
            # Step 2: Parse Instructions and Validate Assets
            self.processing_mode, self.project_info = self._parse_and_validate(self.card_data)
            
            # Step 3: Setup Project and Download Files
            self.creds, self.downloaded_videos, self.project_paths = self._setup_project(self.card_data, self.project_info)
            
            # Step 4: Process Videos
            self.processed_files = self._process_videos(
                self.downloaded_videos, self.project_paths, self.project_info, 
                self.processing_mode, self.creds
            )
            
            # Step 5: Log Results and Cleanup
            self._finalize_and_cleanup(self.processed_files, self.project_info, self.creds, self.project_paths)
            
            print("\n" + "="*60)
            print("🎉 Automation finished successfully!")
            print(f"📁 Project folder: {self.project_paths['project_root']}")
            print(f"📊 Processed {len(self.processed_files)} video(s)")
            print("="*60)
            
        except Exception as e:
            self._handle_error(e, trello_card_id)
    
    def _prepare_confirmation_data(self):
        """Prepare data for the confirmation dialog"""
        # Fetch basic card data for validation
        self.card_data = self._fetch_and_validate_card(self.trello_card_id)
        
        # Parse project info
        self.project_info = self._parse_project_info_for_ui(self.card_data)
        
        # Determine processing mode
        self.processing_mode = self.parser.parse_card_instructions(self.card_data.get('desc', ''))
        
        # Validate assets
        asset_issues = self.validator.validate_assets(self.processing_mode)
        
        # Mock downloaded videos for UI (we'll download them during processing)
        mock_videos = ["video1.mp4", "video2.mp4", "video3.mp4"]  # Placeholder
        
        # Create confirmation data
        return create_confirmation_data_from_orchestrator(
            card_data=self.card_data,
            processing_mode=self.processing_mode,
            project_info=self.project_info,
            downloaded_videos=mock_videos,
            validation_issues=asset_issues
        )
    
    def _parse_project_info_for_ui(self, card_data):
        """Parse project info with fallback for UI"""
        project_info = parse_project_info(card_data['name'])
        if not project_info:
            # Fallback for UI
            project_info = {
                'project_name': card_data.get('name', 'Unknown Project'),
                'ad_type': 'VTD',
                'test_name': '0000',
                'version_letter': '',
                'account_code': 'OO'
            }
        return project_info
    
def _ui_processing_callback(self, progress_callback):
    """Processing callback that provides UI updates"""
    try:
        # Step 1: Fetching Data from Trello (10-20%)
        progress_callback(10, "🔍 Fetching Data from Trello...")
        # Card data already fetched in _prepare_confirmation_data
        
        # Step 2: Downloading Assets from Google Drive (20-50%)
        progress_callback(20, "📥 Downloading Assets from Google Drive...")
        self.creds, self.downloaded_videos, self.project_paths = self._setup_project_with_progress(
            self.card_data, self.project_info, progress_callback
        )
        
        # Step 3: Initializing Process and Creating Folder (50-60%)
        progress_callback(55, "📁 Initializing process and creating project folder...")
        # Already done in _setup_project_with_progress
        
        # Step 4: Processing Videos (60-80%)
        progress_callback(65, "🎬 Processing videos with FFmpeg...")
        self.processed_files = self._process_videos_with_progress(
            self.downloaded_videos, self.project_paths, self.project_info,
            self.processing_mode, self.creds, progress_callback
        )
        
        # Step 5: Updating Google Sheets (80-90%)
        progress_callback(85, "📊 Updating Google Sheets...")
        self._finalize_and_cleanup(self.processed_files, self.project_info, self.creds, self.project_paths)
        
        # Step 6: Finalizing (90-100%)
        progress_callback(95, "🧹 Finalizing and cleaning up...")
        
        progress_callback(100, "🎉 Processing complete!")
        
        # Return results in UI format
        return create_processing_result_from_orchestrator(
            processed_files=self.processed_files,
            start_time=self.start_time,
            output_folder=self.project_paths['project_root'],
            success=True
        )
        
    except Exception as e:
        # Return error result
        from .unified_workflow_dialog import ProcessingResult
        return ProcessingResult(
            success=False,
            duration="",
            processed_files=[],
            output_folder="",
            error_message=str(e),
            error_solution=self._generate_error_solution(str(e))
        )
    
def _setup_project_with_progress(self, card_data, project_info, progress_callback):
    """Setup project with progress updates"""
    # Setup credentials
    progress_callback(25, "🔑 Setting up Google credentials...")
    creds = get_google_creds()
    if not creds:
        raise Exception("Google credentials not available")
    
    # Download videos
    progress_callback(30, "📥 Downloading Assets from Google Drive...")
    gdrive_link = self.validator.extract_gdrive_link(card_data.get('desc', ''))
    downloaded_videos, error = download_files_from_gdrive(gdrive_link, creds, self.monitor)
    if error:
        raise Exception(f"Failed to download videos: {error}")
    if not downloaded_videos:
        raise Exception("No video files were downloaded")
    
    progress_callback(45, "📁 Creating project structure...")
    
    # Create project structure
    naming_suffix = "quiz"
    project_folder_name = generate_project_folder_name(
        project_name=project_info['project_name'],
        first_client_video=downloaded_videos[0],
        ad_type_selection=naming_suffix.title()
    )
    project_paths = create_project_structure(project_folder_name)
    
    # Move files to project structure
    progress_callback(50, "📂 Organizing downloaded files...")
    client_video_final_paths = []
    for video_path in downloaded_videos:
        final_path = os.path.join(project_paths['client_footage'], os.path.basename(video_path))
        shutil.move(video_path, final_path)
        client_video_final_paths.append(final_path)
    
    return creds, client_video_final_paths, project_paths
    
    def _process_videos_with_progress(self, client_videos, project_paths, project_info, processing_mode, creds, progress_callback):
        """Process videos with progress updates"""
        
        # Get video dimensions if needed
        if processing_mode != "save_only":
            progress_callback(62, "📐 Analyzing video dimensions...")
            target_width, target_height, error = get_video_dimensions(client_videos[0])
            if error:
                raise Exception(f"Failed to get video dimensions: {error}")
            print(f"Target resolution set to {target_width}x{target_height}")
        
        # Get starting version number
        progress_callback(65, "📊 Checking version numbers...")
        concept_name = f"GH {project_info['project_name']} {project_info['ad_type']} {project_info['test_name']} Quiz"
        
        error, start_version = write_to_google_sheets(concept_name, [], creds)
        if error:
            raise Exception(f"Failed to check Google Sheets: {error}")
        
        # Process each video
        processed_files = []
        total_videos = len(client_videos)
        
        for i, client_video in enumerate(client_videos):
            version_num = start_version + i
            progress_step = 70 + (i * 15 // total_videos)  # Spread across 70-85%
            
            progress_callback(progress_step, f"🎬 Processing video {i+1} of {total_videos} (v{version_num:02d})...")
            
            processed_file = self._process_single_video(
                client_video, project_paths, project_info, processing_mode,
                version_num, target_width if processing_mode != "save_only" else None,
                target_height if processing_mode != "save_only" else None
            )
            processed_files.append(processed_file)
        
        progress_callback(85, f"✅ Completed processing {total_videos} video(s)")
        return processed_files
    
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
        
        # Step 6: Cleanup temporary files (FIXED)
    print("\n--- Step 6: Cleaning up temporary files ---")
    temp_dir = "temp_downloads"
    
    # Check if temp directory exists before trying to remove it
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            print(f"✅ Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️ Warning: Could not remove temp directory {temp_dir}: {e}")
    else:
        print(f"✅ No temporary files to clean up (temp directory {temp_dir} does not exist)")
    
    print("✅ Cleanup completed successfully")
    
    def _generate_error_solution(self, error_message: str) -> str:
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

def main(card_id=None, use_ui=True):
    """Main entry point for automation - FIXED SIGNATURE"""
    orchestrator = AutomationOrchestrator()
    
    if use_ui:
        # Try UI mode first
        try:
            return orchestrator.execute_with_ui(card_id)  # card_id can be None
        except Exception as ui_error:
            print(f"UI mode failed: {ui_error}")
            if card_id:  # Only fallback if we have a card_id
                print("Falling back to headless mode...")
                orchestrator.execute(card_id)
            else:
                print("No card ID available for headless fallback.")
                return False
    else:
        # Direct headless execution (requires card_id)
        if card_id:
            orchestrator.execute(card_id) 
            return True
        else:
            print("❌ Headless mode requires a Trello card ID")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main_orchestrator.py <TRELLO_CARD_ID> [--headless]")
        print("Example: python main_orchestrator.py 'abc123xyz'")
        print("         python main_orchestrator.py 'abc123xyz' --headless")
    else:
        card_id = sys.argv[1]
        use_ui = "--headless" not in sys.argv
        main(card_id, use_ui)