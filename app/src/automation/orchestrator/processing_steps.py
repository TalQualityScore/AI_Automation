# app/src/automation/orchestrator/processing_steps.py
# Updated to support SVSL/VSL processing modes and new asset structure

import os
import shutil
import time
import re

from ..api_clients import (get_trello_card_data, download_files_from_gdrive, 
                         write_to_google_sheets, get_google_creds)

# Import the correct functions and set account/platform function
from ..video_processor import (get_video_dimensions, process_video_sequence,
                              set_processor_account_platform, _get_connector_video, 
                              _get_quiz_video, _get_svsl_video, _get_vsl_video)

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
        print("\n--- Step 2: Parsing Instructions & Validating Assets ---")
        
        processing_mode = self.orchestrator.parser.parse_card_instructions(card_data.get('desc', ''))
        
        # Validate required assets exist
        asset_issues = self.orchestrator.validator.validate_assets(processing_mode)
        
        if not self.orchestrator.validator.show_validation_results(asset_issues):
            raise Exception("Required assets missing - cannot proceed")
        
        return processing_mode
    
    def download_and_setup(self, card_data, project_info):
        """Step 3: Download videos and set up project structure"""
        print("\n--- Step 3: Downloading Videos & Setting Up Project ---")
        
        # Get Google credentials - FIX: get_google_creds returns just creds, not tuple
        def get_creds():
            creds = get_google_creds()  # Returns Credentials object directly
            if not creds:
                raise Exception("Failed to get Google credentials")
            return creds
        
        creds = self.orchestrator.monitor.execute_with_activity_monitoring(
            get_creds,
            "Google Authentication",
            no_activity_timeout=60
        )
        
        # Extract Google Drive link
        gdrive_link = self.orchestrator.validator.extract_gdrive_link(card_data.get('desc', ''))
        
        # Download videos - Pass creds to download function
        def download_videos():
            videos, error = download_files_from_gdrive(gdrive_link, creds)
            if error:
                raise Exception(f"Failed to download videos: {error}")
            return videos
        
        downloaded_videos = self.orchestrator.monitor.execute_with_activity_monitoring(
            download_videos,
            "Video Download",
            no_activity_timeout=300
        )
        
        # Create project structure
        def create_structure():
            # CRITICAL FIX: Get processing mode from orchestrator, not project_info
            processing_mode = getattr(self.orchestrator, 'processing_mode', '')
            
            # Determine ad_type_selection based on the actual processing mode
            ad_type_selection = "Quiz"  # Default
            
            if 'svsl' in processing_mode.lower():
                ad_type_selection = "SVSL"
            elif 'vsl' in processing_mode.lower():
                ad_type_selection = "VSL"
            else:
                ad_type_selection = "Quiz"
            
            print(f"📁 Creating folder with type: {ad_type_selection} (based on mode: {processing_mode})")
            
            # Use first downloaded video if available, otherwise use placeholder
            first_video = downloaded_videos[0] if downloaded_videos else "placeholder.mp4"
            
            # Generate folder name with all required arguments
            project_folder = generate_project_folder_name(
                project_info['project_name'],
                first_video,
                ad_type_selection
            )
            
            # Call create_project_structure - it returns just a paths dictionary
            paths = create_project_structure(project_folder)
            
            # Validate we got a valid result
            if not paths:
                raise Exception("Failed to create project structure: No paths returned")
            
            return paths
        
        project_paths = self.orchestrator.monitor.execute_with_activity_monitoring(
            create_structure,
            "Project Structure Creation",
            no_activity_timeout=60
        )
        
        print(f"✅ Downloaded {len(downloaded_videos)} videos")
        print(f"✅ Project structure created at: {project_paths['project_root']}")
        
        return creds, downloaded_videos, project_paths
    
    def extract_version_letter(self, filename):
        """Extract version letter (A, B, C, etc.) from filename"""
        patterns = [
            r'_([A-Z])\.mp4$',
            r'-([A-Z])\.mp4$',
            r'([A-Z])\.mp4$',
            r'_([A-Z])_\d+\.mp4$',
            r'-([A-Z])_\d+\.mp4$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return None
    
    def sort_videos_by_version_letter(self, videos):
        """Sort videos alphabetically by version letter (A → B → C)"""
        videos_with_letters = []
        videos_without_letters = []
        
        for video in videos:
            filename = os.path.basename(video)
            letter = self.extract_version_letter(filename)
            if letter:
                videos_with_letters.append((video, letter))
            else:
                videos_without_letters.append(video)
        
        # Sort by letter
        videos_with_letters.sort(key=lambda x: x[1])
        
        # Combine: lettered videos first, then non-lettered
        sorted_videos = [v[0] for v in videos_with_letters] + videos_without_letters
        
        # Print sorting results
        print("\n📄 Video sorting results:")
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
        
        # Set account and platform for video processor
        account_code = project_info.get('account_code') or project_info.get('detected_account_code')
        platform_code = project_info.get('platform_code') or project_info.get('detected_platform_code')
        
        if account_code and platform_code:
            print(f"🎯 Setting processor context: Account={account_code}, Platform={platform_code}")
            set_processor_account_platform(account_code, platform_code)
        
        # Sort videos alphabetically by version letter
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
        
        # Determine the type suffix based on processing mode
        if "quiz" in processing_mode:
            type_suffix = "Quiz"
        elif "svsl" in processing_mode:
            type_suffix = "SVSL"
        elif "vsl" in processing_mode:
            type_suffix = "VSL"
        else:
            type_suffix = "Quiz"  # Default
        
        # Get starting version number
        concept_name = f"GH {project_info['project_name']} {project_info['ad_type']} {project_info['test_name']} {type_suffix}"
        
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
        
        # Convert client_video to absolute path if it's relative
        import os
        if not os.path.isabs(client_video):
            # If it's a relative path, make it absolute
            client_video = os.path.abspath(client_video)
            print(f"📁 Converted to absolute path: {client_video}")
        
        image_desc = get_image_description(client_video)
        
        # Extract the actual version letter from this specific video file
        actual_letter = self.extract_version_letter(os.path.basename(client_video))
        
        # Determine the type designation based on processing mode
        if "quiz" in processing_mode:
            type_designation = "quiz"
        elif "svsl" in processing_mode:
            type_designation = "svsl"
        elif "vsl" in processing_mode:
            type_designation = "vsl"
        else:
            type_designation = "quiz"  # Default
        
        output_name = generate_output_name(
            project_name=project_info['project_name'], 
            first_client_video=client_video,
            ad_type_selection=type_designation,  # Pass the type designation
            image_desc=image_desc, 
            version_num=version_num,
            version_letter=actual_letter or project_info.get('version_letter', '')
        )
        output_path = os.path.join(project_paths['ame'], f"{output_name}.mp4")
        
        # Store paths for breakdown report
        processed_file_info = {
            "version": f"v{version_num:02d}",
            "source_file": os.path.basename(client_video),
            "output_name": output_name,
            "client_video_path": client_video,
            "output_path": output_path
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
                processed_file_info['connector_path'] = _get_connector_video()
                processed_file_info['quiz_path'] = _get_quiz_video()
                description = f"New Ad from {os.path.basename(client_video)} + connector + quiz"
            elif processing_mode == "quiz_only":
                processed_file_info['quiz_path'] = _get_quiz_video()
                description = f"New Ad from {os.path.basename(client_video)} + quiz"
            elif processing_mode == "connector_svsl":
                processed_file_info['connector_path'] = _get_connector_video()
                processed_file_info['svsl_path'] = _get_svsl_video()
                description = f"New Ad from {os.path.basename(client_video)} + connector + SVSL"
            elif processing_mode == "svsl_only":
                processed_file_info['svsl_path'] = _get_svsl_video()
                description = f"New Ad from {os.path.basename(client_video)} + SVSL"
            elif processing_mode == "connector_vsl":
                processed_file_info['connector_path'] = _get_connector_video()
                processed_file_info['vsl_path'] = _get_vsl_video()
                description = f"New Ad from {os.path.basename(client_video)} + connector + VSL"
            elif processing_mode == "vsl_only":
                processed_file_info['vsl_path'] = _get_vsl_video()
                description = f"New Ad from {os.path.basename(client_video)} + VSL"
            else:
                description = f"New Ad from {os.path.basename(client_video)}"
            
            # Process with FFmpeg - ensure absolute path is passed
            def process_with_ffmpeg():
                error = process_video_sequence(
                    client_video, output_path, target_width, target_height, processing_mode
                )
                if error:
                    raise Exception(error)
                return f"Processed: {output_name}.mp4"
            
            result = self.orchestrator.monitor.execute_with_activity_monitoring(
                process_with_ffmpeg,
                f"Process Video v{version_num:02d}",
                no_activity_timeout=300
            )
        
        processed_file_info['description'] = description
        
        # Add file size if available
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            processed_file_info['size_mb'] = round(size_mb, 2)
        
        print(f"✅ {result}")
        
        return processed_file_info
    
    def write_to_sheets(self, project_info, processed_files, creds):
        """Step 5: Write results to Google Sheets"""
        print("\n--- Step 5: Writing to Google Sheets ---")
        
        # Determine the type suffix based on what was processed
        type_suffix = "Quiz"  # Default
        if processed_files and len(processed_files) > 0:
            first_file = processed_files[0]
            if 'svsl_path' in first_file:
                type_suffix = "SVSL"
            elif 'vsl_path' in first_file:
                type_suffix = "VSL"
        
        # Build concept name for display in column 1
        concept_name = f"GH {project_info['project_name']} {project_info['ad_type']} {project_info['test_name']} {type_suffix}"
        
        # For worksheet routing, we need to use the original card title that has account/platform
        # This should be stored in the orchestrator
        routing_name = None
        if hasattr(self.orchestrator, 'original_card_title'):
            routing_name = self.orchestrator.original_card_title
            print(f"📋 Using original card title for routing: '{routing_name}'")
        else:
            # Fallback to concept name if no original title stored
            routing_name = concept_name
            print(f"⚠️ Original card title not found, using concept name for routing")
        
        # Convert output names to list of lists (each name becomes a row with one column)
        output_names = []
        for f in processed_files:
            # Each row should be a list, even if it has just one element
            output_names.append([f['output_name']])  # Make it a list with one element
        
        def write_sheets():
            # Use write_to_google_sheets_with_custom_name if available
            try:
                from ..api_clients import write_to_google_sheets_with_custom_name
                error, _ = write_to_google_sheets_with_custom_name(
                    routing_name,  # For finding worksheet (has account/platform)
                    concept_name,  # For column 1 display
                    output_names, 
                    creds
                )
            except ImportError:
                # Fallback to regular write function
                error, _ = write_to_google_sheets(concept_name, output_names, creds)
            
            if error:
                raise Exception(f"Failed to write to Google Sheets: {error}")
            return "Success"
        
        self.orchestrator.monitor.execute_with_activity_monitoring(
            write_sheets,
            "Google Sheets Update",
            no_activity_timeout=120
        )
        
        print(f"✅ Successfully wrote {len(output_names)} entries to Google Sheets")