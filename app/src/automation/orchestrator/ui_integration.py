# app/src/automation/orchestrator/ui_integration.py
import os
import shutil
import time

from ..api_clients import get_google_creds, download_files_from_gdrive, write_to_google_sheets
from ..video_processor import get_video_dimensions
from ..workflow_utils import parse_project_info, create_project_structure
from ...naming_generator import generate_project_folder_name

from ..workflow_dialog.helpers import create_confirmation_data_from_orchestrator, create_processing_result_from_orchestrator

class UIIntegration:
    """Handles UI-specific integration methods for the orchestrator"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def prepare_confirmation_data(self):
        """Prepare data for the confirmation dialog"""
        # Fetch basic card data for validation
        self.orchestrator.card_data = self.orchestrator.processing_steps.fetch_and_validate_card(self.orchestrator.trello_card_id)
        
        # Parse project info
        self.orchestrator.project_info = self._parse_project_info_for_ui(self.orchestrator.card_data)
        
        # Determine processing mode
        self.orchestrator.processing_mode = self.orchestrator.parser.parse_card_instructions(self.orchestrator.card_data.get('desc', ''))
        
        # Validate assets
        asset_issues = self.orchestrator.validator.validate_assets(self.orchestrator.processing_mode)
        
        # Mock downloaded videos for UI (we'll download them during processing)
        mock_videos = ["video1.mp4", "video2.mp4", "video3.mp4"]  # Placeholder
        
        # Create confirmation data
        return create_confirmation_data_from_orchestrator(
            card_data=self.orchestrator.card_data,
            processing_mode=self.orchestrator.processing_mode,
            project_info=self.orchestrator.project_info,
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
    
    def ui_processing_callback(self, progress_callback):
        """Processing callback that provides UI updates"""
        try:
            # Step 1: Already done in preparation
            progress_callback(15, "🔍 Fetching Data from Trello...")
            time.sleep(0.5)  # Brief pause for UI update
            
            # Step 2: Downloading Assets from Google Drive
            progress_callback(25, "📥 Downloading Assets from Google Drive...")
            self.orchestrator.creds, self.orchestrator.downloaded_videos, self.orchestrator.project_paths = self._setup_project_with_progress(
                self.orchestrator.card_data, self.orchestrator.project_info, progress_callback
            )
            
            # Step 3: Processing Videos 
            progress_callback(60, "🎬 Processing videos...")
            self.orchestrator.processed_files = self._process_videos_with_progress(
                self.orchestrator.downloaded_videos, self.orchestrator.project_paths, self.orchestrator.project_info,
                self.orchestrator.processing_mode, self.orchestrator.creds, progress_callback
            )
            
            # Step 4: Updating Google Sheets
            progress_callback(90, "📊 Updating Google Sheets...")
            self.orchestrator.processing_steps.finalize_and_cleanup(
                self.orchestrator.processed_files, self.orchestrator.project_info, 
                self.orchestrator.creds, self.orchestrator.project_paths
            )
            
            # Step 5: Finalizing
            progress_callback(100, "🎉 Processing complete!")
            print("🔍 DEBUG: About to return result to UI")

            # Return results
            return create_processing_result_from_orchestrator(
                processed_files=self.orchestrator.processed_files,
                start_time=self.orchestrator.start_time,
                output_folder=self.orchestrator.project_paths['project_root'],
                success=True
            )
            
        except Exception as e:
            from ..workflow_data_models import ProcessingResult
            return ProcessingResult(
                success=False,
                duration="",
                processed_files=[],
                output_folder="",
                error_message=str(e),
                error_solution=self.orchestrator.error_handler.generate_error_solution(str(e))
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
        gdrive_link = self.orchestrator.validator.extract_gdrive_link(card_data.get('desc', ''))
        downloaded_videos, error = download_files_from_gdrive(gdrive_link, creds, self.orchestrator.monitor)
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
            
            processed_file = self.orchestrator.processing_steps.process_single_video(
                client_video, project_paths, project_info, processing_mode,
                version_num, target_width if processing_mode != "save_only" else None,
                target_height if processing_mode != "save_only" else None
            )
            processed_files.append(processed_file)
        
        progress_callback(85, f"✅ Completed processing {total_videos} video(s)")
        return processed_files