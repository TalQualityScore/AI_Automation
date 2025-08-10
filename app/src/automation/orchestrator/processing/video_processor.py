# app/src/automation/orchestrator/processing/video_processor.py
"""
Video Processor Module - Handles actual video processing operations
"""

import os
import shutil
from ...api_clients import write_to_google_sheets
from ...video_processor import (get_video_dimensions, process_video_sequence,
                               set_processor_account_platform, _get_connector_video, 
                               _get_quiz_video, _get_svsl_video, _get_vsl_video)
from ....naming_generator import generate_output_name, get_image_description
from .video_sorter import VideoSorter

class VideoProcessor:
    """Handles video processing operations"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.video_sorter = VideoSorter()
    
    def process_all_videos(self, sorted_client_videos, project_paths, project_info, 
                          processing_mode, creds):
        """Process all videos based on mode
        
        Args:
            sorted_client_videos: Pre-sorted list of video paths
            project_paths: Dictionary of project paths
            project_info: Project information dictionary
            processing_mode: Processing mode string
            creds: Google credentials
            
        Returns:
            List of processed file information dictionaries
        """
        print(f"\n--- Step 4: Processing Videos ---")
        
        # Set account and platform for video processor
        account_code = project_info.get('account_code') or project_info.get('detected_account_code')
        platform_code = project_info.get('platform_code') or project_info.get('detected_platform_code')
        
        if account_code and platform_code:
            print(f"🎯 Setting processor context: Account={account_code}, Platform={platform_code}")
            set_processor_account_platform(account_code, platform_code)
        
        # Get video dimensions if needed
        target_width = None
        target_height = None
        
        if processing_mode != "save_only" and sorted_client_videos:
            def get_dimensions():
                width, height, error = get_video_dimensions(sorted_client_videos[0])
                if error:
                    raise Exception(f"Failed to get video dimensions: {error}")
                return width, height
            
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
        
        # Get starting version number from Google Sheets
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
            letter = self.video_sorter.extract_version_letter(os.path.basename(client_video))
            if letter:
                print(f"\n--- Processing Version {version_num:02d} (Letter {letter}) ({processing_mode}) ---")
            else:
                print(f"\n--- Processing Version {version_num:02d} ({processing_mode}) ---")
            
            processed_file = self.process_single_video(
                client_video, project_paths, project_info, processing_mode,
                version_num, target_width, target_height
            )
            
            # Store the actual letter that was processed with this version
            processed_file['version_letter'] = letter if letter else ''
            processed_files.append(processed_file)
        
        return processed_files
    
# CHANGES FOR: app/src/automation/orchestrator/processing/video_processor.py
# Replace the process_single_video method (starting at line 103) with this fixed version:

    def process_single_video(self, client_video, project_paths, project_info, processing_mode,
                        version_num, target_width, target_height):
        """Process a single video file
        
        Args:
            client_video: Path to the client video file
            project_paths: Dictionary of project paths
            project_info: Project information dictionary
            processing_mode: Processing mode string
            version_num: Version number for this video
            target_width: Target video width
            target_height: Target video height
            
        Returns:
            Dictionary with processed file information
        """
        
        # Convert to absolute path if needed
        if not os.path.isabs(client_video):
            client_video = os.path.abspath(client_video)
            print(f"📁 Converted to absolute path: {client_video}")
        
        image_desc = get_image_description(client_video)
        
        # Extract the actual version letter from this specific video file
        actual_letter = self.video_sorter.extract_version_letter(os.path.basename(client_video))
        
        # Determine the type designation based on processing mode
        if "quiz" in processing_mode:
            type_designation = "quiz"
        elif "svsl" in processing_mode:
            type_designation = "svsl"
        elif "vsl" in processing_mode:
            type_designation = "vsl"
        else:
            type_designation = "quiz"  # Default
        
        # Generate output name
        output_name = generate_output_name(
            project_name=project_info['project_name'], 
            first_client_video=client_video,
            ad_type_selection=type_designation,
            image_desc=image_desc, 
            version_num=version_num,
            version_letter=actual_letter or project_info.get('version_letter', '')
        )
        
        # FIXED: Always use _AME folder for output
        ame_folder = project_paths.get('_AME', os.path.join(project_paths['project_root'], '_AME'))
        
        # Ensure _AME folder exists
        if not os.path.exists(ame_folder):
            os.makedirs(ame_folder)
            print(f"📁 Created _AME folder: {ame_folder}")
        
        output_path = os.path.join(ame_folder, f"{output_name}.mp4")
        
        # Store original filename for sheets
        original_filename = os.path.basename(client_video)
        
        # Store paths for breakdown report
        processed_file_info = {
            "version": version_num,  # Store as number for sorting
            "version_letter": actual_letter if actual_letter else '',
            "source_file": original_filename,
            "output_name": output_name,  # Just the name without .mp4
            "client_video_path": client_video,
            "output_path": output_path,
            "original_filename": original_filename  # Store for sheets formatting
        }
        
        if processing_mode == "save_only":
            # Just copy the file
            def save_video():
                shutil.copy(client_video, output_path)
                return f"Saved: {output_name}.mp4"
            
            result = self.orchestrator.monitor.execute_with_activity_monitoring(
                save_video,
                f"Save Video v{version_num:02d}",
                no_activity_timeout=120
            )
            
            # Format description for sheets
            description = f"Copy of OO_{original_filename}"
            endpoint_type = ""
            
        else:
            # Process with transitions and endpoint
            endpoint_type = ""
            
            # FIX #2: VALIDATE VIDEOS EXIST BEFORE PROCESSING
            missing_videos = []
            
            # Store the paths of additional videos for the breakdown report
            if processing_mode == "connector_quiz":
                connector_video = _get_connector_video()
                quiz_video = _get_quiz_video()
                
                if not connector_video:
                    missing_videos.append("connector")
                if not quiz_video:
                    missing_videos.append("quiz")
                
                if not missing_videos:  # Only add if both exist
                    processed_file_info['connector_path'] = connector_video
                    processed_file_info['quiz_path'] = quiz_video
                    endpoint_type = "quiz"
                    
            elif processing_mode == "quiz_only":
                quiz_video = _get_quiz_video()
                
                if not quiz_video:
                    missing_videos.append("quiz")
                else:
                    processed_file_info['quiz_path'] = quiz_video
                    endpoint_type = "quiz"
                    
            elif processing_mode == "connector_svsl":
                connector_video = _get_connector_video()
                svsl_video = _get_svsl_video()
                
                if not connector_video:
                    missing_videos.append("connector")
                if not svsl_video:
                    missing_videos.append("SVSL")
                
                if not missing_videos:  # Only add if both exist
                    processed_file_info['connector_path'] = connector_video
                    processed_file_info['svsl_path'] = svsl_video
                    endpoint_type = "svsl"
                    
            elif processing_mode == "svsl_only":
                svsl_video = _get_svsl_video()
                
                if not svsl_video:
                    missing_videos.append("SVSL")
                else:
                    processed_file_info['svsl_path'] = svsl_video
                    endpoint_type = "svsl"
                    
            elif processing_mode == "connector_vsl":
                connector_video = _get_connector_video()
                vsl_video = _get_vsl_video()
                
                if not connector_video:
                    missing_videos.append("connector")
                if not vsl_video:
                    missing_videos.append("VSL")
                
                if not missing_videos:  # Only add if both exist
                    processed_file_info['connector_path'] = connector_video
                    processed_file_info['vsl_path'] = vsl_video
                    endpoint_type = "vsl"
                    
            elif processing_mode == "vsl_only":
                vsl_video = _get_vsl_video()
                
                if not vsl_video:
                    missing_videos.append("VSL")
                else:
                    processed_file_info['vsl_path'] = vsl_video
                    endpoint_type = "vsl"
            
            # Check if videos are missing
            if missing_videos:
                # Build detailed error message
                account_code = project_info.get('account_code', 'OO')
                platform_code = project_info.get('platform_code', 'FB')
                
                error_message = f"❌ MISSING REQUIRED VIDEO FILES\n\n"
                error_message += f"Cannot process in '{processing_mode}' mode.\n"
                error_message += f"Missing: {', '.join(missing_videos)} video(s)\n\n"
                error_message += "Please add the missing video(s) to:\n"
                
                # Add specific paths for each missing video type
                for video_type in missing_videos:
                    if video_type.lower() == "connector":
                        path = f"Assets/Videos/{account_code}/{platform_code}/Connector/"
                    elif video_type.lower() == "quiz":
                        path = f"Assets/Videos/{account_code}/{platform_code}/Quiz/"
                    elif video_type.upper() == "VSL":
                        path = f"Assets/Videos/{account_code}/{platform_code}/VSL/"
                    elif video_type.upper() == "SVSL":
                        path = f"Assets/Videos/{account_code}/{platform_code}/SVSL/"
                    else:
                        path = f"Assets/Videos/{account_code}/{platform_code}/{video_type}/"
                    
                    full_path = os.path.join(os.path.dirname(project_paths['project_root']), path)
                    error_message += f"\n{video_type.upper()}:\n  {full_path}"
                    
                    # Check if folder exists and is empty
                    if not os.path.exists(full_path):
                        error_message += f"\n  ⚠️ Folder doesn't exist - create it first!"
                    else:
                        files = [f for f in os.listdir(full_path) if f.endswith(('.mp4', '.mov', '.avi'))]
                        if not files:
                            error_message += f"\n  ⚠️ Folder is empty - add {video_type.upper()} videos!"
                    error_message += "\n"
                
                error_message += "\n📌 Action Required:\n"
                error_message += "1. Add the missing video files to the folders above\n"
                error_message += "2. Run the automation again\n"
                
                print(f"\n{error_message}")
                
                # CRITICAL: RAISE EXCEPTION TO STOP PROCESSING AND SHOW ERROR DIALOG
                raise Exception(error_message)
            
            # Format description for sheets
            description = f"Copy of OO_{original_filename}"
            
            # Process with FFmpeg
            def process_with_ffmpeg():
                error = process_video_sequence(
                    client_video, output_path, target_width, target_height, processing_mode
                )
                if error:
                    raise Exception(error)
                return f"Processed: {output_name}.mp4"
            
            # FIX #1: DYNAMIC TIMEOUT BASED ON PROCESSING MODE
            if "vsl" in processing_mode.lower():
                # VSL videos can be up to 50 minutes long
                timeout_seconds = 3600  # 60 minutes
                print(f"⏱️ Using extended timeout for VSL: {timeout_seconds} seconds (60 minutes)")
            elif "svsl" in processing_mode.lower():
                # SVSL videos are typically 10-30 minutes
                timeout_seconds = 1800  # 30 minutes
                print(f"⏱️ Using extended timeout for SVSL: {timeout_seconds} seconds (30 minutes)")
            else:
                # Quiz and connector videos are shorter
                timeout_seconds = 600  # 10 minutes (increased from 300)
                print(f"⏱️ Using standard timeout: {timeout_seconds} seconds (10 minutes)")
            
            result = self.orchestrator.monitor.execute_with_activity_monitoring(
                process_with_ffmpeg,
                f"Process Video v{version_num:02d}",
                no_activity_timeout=timeout_seconds  # CHANGED FROM 300 to dynamic
            )
        
        # Store formatted description and endpoint type
        processed_file_info['description'] = description
        processed_file_info['endpoint_type'] = endpoint_type
        
        # Add file size if available
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            processed_file_info['size_mb'] = round(size_mb, 2)
        
        print(f"✅ {result}")
        print(f"📁 Output saved to: {output_path}")
        
        return processed_file_info
