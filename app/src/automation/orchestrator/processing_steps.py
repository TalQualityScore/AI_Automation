# app/src/automation/orchestrator/processing_steps.py - FIXED IMPORTS AND ALPHABETICAL ORDER

import os
import shutil
import time
import re

from ..api_clients import (get_trello_card_data, download_files_from_gdrive, 
                         write_to_google_sheets, get_google_creds)

# FIXED: Import the correct functions from video_processor
from ..video_processor import get_video_dimensions, process_video_sequence

from ..workflow_utils import parse_project_info, create_project_structure
from ...naming_generator import generate_project_folder_name, generate_output_name, get_image_description

class ProcessingSteps:
    """Handles all the individual processing steps for the orchestrator"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def fetch_and_validate_card(self, trello_card_id):
        """Step 1: Fetch Trello card and validate basic data"""
        print("\n--- Step 1: Fetching Trello & Parsing Project Info ---")
        
        def fetch_card_data():
            card_data, error = get_trello_card_data(trello_card_id)
            if error:
                raise Exception(f"Failed to fetch Trello card: {error}")
            return card_data
        
        card_data = self.orchestrator.monitor.execute_with_activity_monitoring(
            fetch_card_data, 
            "Trello Card Fetch", 
            no_activity_timeout=60
        )
        
        # Validate card data
        validation_issues = self.orchestrator.validator.validate_trello_card(card_data)
        
        if not self.orchestrator.validator.show_validation_results(validation_issues):
            raise Exception("Validation failed - cannot proceed")
        
        return card_data
    
    def parse_and_validate(self, card_data):
        """Step 2: Parse instructions and validate assets"""
        
        # Parse processing mode
        processing_mode = self.orchestrator.parser.parse_card_instructions(card_data.get('desc', ''))
        print(f"Processing mode detected: {processing_mode}")
        
        # Validate required assets
        asset_issues = self.orchestrator.validator.validate_assets(processing_mode)
        
        if not self.orchestrator.validator.show_validation_results(asset_issues):
            raise Exception("Asset validation failed - cannot proceed")
        
        # Parse project info
        def parse_project():
            project_info = parse_project_info(card_data['name'])
            if not project_info:
                raise Exception("Could not parse project info from card name")
            return project_info
        
        project_info = self.orchestrator.monitor.execute_with_activity_monitoring(
            parse_project,
            "Project Info Parsing",
            no_activity_timeout=30
        )
        
        print(f"Successfully parsed project: {project_info['project_name']}")
        print(f"Version letter: {project_info.get('version_letter', 'Not found')}")
        
        return processing_mode, project_info
    
    def setup_project(self, card_data, project_info):
        """Step 3: Setup credentials, download files, create project structure"""
        print("\n--- Step 2: Downloading & Setting Up Project ---")
        
        # Setup credentials
        def setup_credentials():
            creds = get_google_creds()
            if not creds:
                raise Exception("Google credentials not available")
            return creds
        
        creds = self.orchestrator.monitor.execute_with_activity_monitoring(
            setup_credentials,
            "Google Credentials Setup",
            no_activity_timeout=30
        )
        
        # Download videos
        def download_videos():
            # FIXED: Use the new API clients approach
            from ..api_clients import TrelloClient
            trello_client = TrelloClient()
            gdrive_link = trello_client.extract_gdrive_link(card_data.get('desc', ''))
            
            downloaded_videos, error = download_files_from_gdrive(gdrive_link, creds, self.orchestrator.monitor)
            if error:
                raise Exception(f"Failed to download videos: {error}")
            if not downloaded_videos:
                raise Exception("No video files were downloaded")
            return downloaded_videos
        
        downloaded_videos = self.orchestrator.monitor.execute_with_activity_monitoring(
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
            print(f"🔍 Available project_paths keys: {list(project_paths.keys())}")
            final_path = os.path.join(project_paths['client_videos'], os.path.basename(video_path))
            shutil.move(video_path, final_path)
            client_video_final_paths.append(final_path)
        
        return creds, client_video_final_paths, project_paths
    
    def extract_version_letter(self, filename):
        """Extract version letter (A, B, C, etc.) from filename"""
        # Pattern 1: Date followed by letter (250721A)
        pattern1 = r'(\d{6})([A-Z])(?:[_\.]|$)'
        match = re.search(pattern1, filename)
        if match:
            return match.group(2)
        
        # Pattern 2: Test number followed by letter (12036A)
        pattern2 = r'(\d{4,5})([A-Z])(?:[_\.]|$)'
        match = re.search(pattern2, filename)
        if match:
            return match.group(2)
        
        # Pattern 3: Underscore followed by single letter before extension
        pattern3 = r'_([A-Z])_?\d*\.\w+$'
        match = re.search(pattern3, filename)
        if match:
            return match.group(1)
        
        return None
    
    def sort_videos_by_version_letter(self, video_paths):
        """Sort videos by their version letters (A, B, C, etc.)"""
        videos_with_letters = []
        videos_without_letters = []
        
        for video_path in video_paths:
            filename = os.path.basename(video_path)
            letter = self.extract_version_letter(filename)
            
            if letter:
                videos_with_letters.append((video_path, letter))
                print(f"📝 Found version letter '{letter}' in: {filename}")
            else:
                videos_without_letters.append(video_path)
                print(f"⚠️ No version letter found in: {filename}")
        
        # Sort videos with letters alphabetically
        videos_with_letters.sort(key=lambda x: x[1])
        
        # Combine sorted videos with letters first, then videos without letters
        sorted_videos = [video for video, letter in videos_with_letters] + videos_without_letters
        
        # Print the final order
        print("\n📊 Final video processing order:")
        for i, video in enumerate(sorted_videos, 1):
            filename = os.path.basename(video)
            letter = self.extract_version_letter(filename)
            if letter:
                print(f"   {i}. {filename} (Version {letter})")
            else:
                print(f"   {i}. {filename} (No version)")
        
        return sorted_videos
    
    def process_videos(self, client_videos, project_paths, project_info, processing_mode, creds):
        """Step 4: Process all videos based on mode"""
        print(f"\n--- Step 4: Processing Videos ---")
        
        # CRITICAL FIX: Sort videos alphabetically by version letter
        print("\n🔤 Sorting videos by version letter (A → Z)...")
        sorted_client_videos = self.sort_videos_by_version_letter(client_videos)
        
        # Get video dimensions if needed
        if processing_mode != "save_only":
            def get_dimensions():
                target_width, target_height, error = get_video_dimensions(sorted_client_videos[0])
                if error:
                    raise Exception(f"Failed to get video dimensions: {error}")
                return target_width, target_height
            
            target_width, target_height = self.orchestrator.monitor.execute_with_activity_monitoring(
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
        
        start_version = self.orchestrator.monitor.execute_with_activity_monitoring(
            check_sheets,
            "Google Sheets Version Check",
            no_activity_timeout=120
        )
        
        # Process each video in sorted order
        processed_files = []
        for i, client_video in enumerate(sorted_client_videos):
            version_num = start_version + i
            
            # Show which letter is being processed
            letter = self.extract_version_letter(os.path.basename(client_video))
            if letter:
                print(f"\n--- Processing Version {version_num:02d} (Letter {letter}) ({processing_mode}) ---")
            else:
                print(f"\n--- Processing Version {version_num:02d} ({processing_mode}) ---")
            
            processed_file = self.process_single_video(
                client_video, project_paths, project_info, processing_mode,
                version_num, target_width if processing_mode != "save_only" else None,
                target_height if processing_mode != "save_only" else None
            )
            
            # Store the actual letter that was processed with this version
            processed_file['version_letter'] = letter if letter else ''
            processed_files.append(processed_file)
        
        return processed_files
    
    def process_single_video(self, client_video, project_paths, project_info, processing_mode, version_num, target_width, target_height):
        """Process a single video file"""
        
        image_desc = get_image_description(client_video)
        
        # Extract the actual version letter from this specific video file
        actual_letter = self.extract_version_letter(os.path.basename(client_video))
        
        output_name = generate_output_name(
            project_name=project_info['project_name'], 
            first_client_video=client_video,
            ad_type_selection="quiz", 
            image_desc=image_desc, 
            version_num=version_num,
            version_letter=actual_letter or project_info.get('version_letter', '')  # Use actual letter from file
        )
        output_path = os.path.join(project_paths['ame'], f"{output_name}.mp4")
        
        # Store paths for breakdown report
        processed_file_info = {
            "version": f"v{version_num:02d}",
            "source_file": os.path.basename(client_video),
            "output_name": output_name,
            "client_video_path": client_video,  # Store full path for duration calculation
            "output_path": output_path  # Store output path
        }
        
        if processing_mode == "save_only":
            def save_video():
                shutil.copy(client_video, output_path)
                return f"Saved: {output_name}.mp4"
            
            result = self.orchestrator.monitor.execute_with_activity_monitoring(
                save_video,
                f"Save Video v{version_num:02d}",
                no_activity_timeout=120
            )
            
            description = f"Saved as is from {os.path.basename(client_video)}"
        else:
            # Store the paths of additional videos for the breakdown report
            if processing_mode == "connector_quiz":
                # Get connector and quiz paths
                from ..video_processor import _get_connector_video, _get_quiz_video
                processed_file_info['connector_path'] = _get_connector_video()
                processed_file_info['quiz_path'] = _get_quiz_video()
                description = f"New Ad from {os.path.basename(client_video)} + connector + quiz"
            elif processing_mode == "quiz_only":
                # Get quiz path
                from ..video_processor import _get_quiz_video
                processed_file_info['quiz_path'] = _get_quiz_video()
                description = f"New Ad from {os.path.basename(client_video)} + quiz"
            else:
                description = f"New Ad from {os.path.basename(client_video)}"
            
            def process_video():
                error = process_video_sequence(client_video, output_path, target_width, target_height, processing_mode)
                if error:
                    raise Exception(f"Video processing failed: {error}")
                return f"Processed: {output_name}.mp4"
            
            result = self.orchestrator.monitor.execute_with_activity_monitoring(
                process_video,
                f"Process Video v{version_num:02d}",
                no_activity_timeout=1800  # 30 minutes of no FFmpeg progress
            )
        
        print(result)
        
        processed_file_info["description"] = description
        return processed_file_info
    
    def finalize_and_cleanup(self, processed_files, project_info, creds, project_paths):
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
            
            result = self.orchestrator.monitor.execute_with_activity_monitoring(
                write_results,
                "Google Sheets Logging",
                no_activity_timeout=120
            )
            print(result)
        else:
            print("No files were processed, skipping log.")
        
        # Step 6: Cleanup temporary files
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