# app/src/automation/orchestrator/processing/video_processor.py - REFACTORED
"""
Video Processor Module - REFACTORED
Now uses modular components for better organization
"""

import os
from ...api_clients import write_to_google_sheets
from ...video_processor import (get_video_dimensions, set_processor_account_platform)
from ....naming_generator import generate_output_name, get_image_description
from .video_sorter import VideoSorter
from .video_processing_modules import (
    PathHandler, ModeProcessor, VideoValidator, 
    TimeoutManager, OutputBuilder
)

class VideoProcessor:
    """Handles video processing operations - REFACTORED"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.video_sorter = VideoSorter()
        
        # Initialize helper modules
        self.path_handler = PathHandler(orchestrator)
        self.mode_processor = ModeProcessor(orchestrator)
        self.timeout_manager = TimeoutManager()
        self.output_builder = OutputBuilder()
    
    def process_all_videos(self, sorted_client_videos, project_paths, project_info, 
                          processing_mode, creds):
        """Process all videos based on mode"""
        print(f"\n--- Step 4: Processing Videos ---")
        
        # Set account and platform for video processor
        account_code = project_info.get('account_code') or project_info.get('detected_account_code')
        platform_code = project_info.get('platform_code') or project_info.get('detected_platform_code')
        
        if account_code and platform_code:
            print(f"🎯 Setting processor context: Account={account_code}, Platform={platform_code}")
            set_processor_account_platform(account_code, platform_code)
        
        # Get video dimensions if needed
        target_width, target_height = self._get_target_dimensions(
            sorted_client_videos, processing_mode
        )
        
        # Get starting version number
        start_version = self._get_starting_version(project_info, processing_mode, creds)
        
        # Process each video
        processed_files = []
        for i, client_video in enumerate(sorted_client_videos):
            version_num = start_version + i
            letter = self.video_sorter.extract_version_letter(os.path.basename(client_video))
            
            print(f"\n--- Processing Version {version_num:02d} (Letter {letter or 'N/A'}) ---")
            
            processed_file = self.process_single_video(
                client_video, project_paths, project_info, processing_mode,
                version_num, target_width, target_height
            )
            
            processed_file['version_letter'] = letter if letter else ''
            processed_files.append(processed_file)
        
        return processed_files
    
    def process_single_video(self, client_video, project_paths, project_info, 
                        processing_mode, version_num, target_width, target_height):
        """
        Process a single video file - FIXED to handle video paths
        """
        
        # Step 1: Validate and prepare paths
        client_video = self.path_handler.validate_and_convert_path(client_video)
        
        # Step 2: Generate output name
        actual_letter = self.video_sorter.extract_version_letter(os.path.basename(client_video))
        image_desc = get_image_description(client_video)
        
        output_name = generate_output_name(
            project_name=project_info['project_name'],
            first_client_video=client_video,
            ad_type_selection=self._get_type_designation(processing_mode),
            image_desc=image_desc,
            version_num=version_num,
            version_letter=actual_letter or project_info.get('version_letter', '')
        )
        
        # Step 3: Prepare output path
        output_path = self.path_handler.prepare_output_path(
            project_info, output_name, version_num
        )
        
        # Step 4: Process based on mode
        video_paths = {}  # Initialize
        
        if processing_mode == "save_only":
            # Now expects 4 return values
            result, description, endpoint_type, video_paths = self.mode_processor.process_save_only(
                client_video, output_path, version_num
            )
        else:
            # Validate required videos exist
            video_validator = VideoValidator(project_info, project_paths)
            _, missing_videos = video_validator.validate_required_videos(processing_mode)
            
            if missing_videos:
                error_msg = video_validator.generate_missing_video_error(
                    missing_videos, processing_mode
                )
                print(f"\n{error_msg}")
                raise Exception(error_msg)
            
            # Get appropriate timeout
            timeout = self.timeout_manager.get_processing_timeout(processing_mode)
            
            # Process with transitions - now returns video_paths
            result, description, endpoint_type, video_paths = self.mode_processor.process_with_transitions(
                client_video, output_path, target_width, target_height,
                processing_mode, timeout, version_num
            )
        
        # Step 5: Build output information with actual video paths
        processed_file_info = self.output_builder.build_processed_file_info(
            client_video, output_path, output_name, version_num,
            actual_letter, video_paths,  # Now contains actual paths used
            description, endpoint_type
        )
        
        print(f"✅ {result}")
        print(f"📁 Output saved to: {output_path}")
        
        return processed_file_info
    
    def _get_target_dimensions(self, sorted_client_videos, processing_mode):
        """Get target video dimensions"""
        if processing_mode == "save_only" or not sorted_client_videos:
            return None, None
        
        def get_dimensions():
            width, height, error = get_video_dimensions(sorted_client_videos[0])
            if error:
                raise Exception(f"Failed to get video dimensions: {error}")
            return width, height
        
        width, height = self.orchestrator.monitor.execute_with_activity_monitoring(
            get_dimensions, "Video Dimension Analysis", no_activity_timeout=60
        )
        
        print(f"Target resolution set to {width}x{height}")
        return width, height
    
    def _get_starting_version(self, project_info, processing_mode, creds):
        """Get starting version number from Google Sheets"""
        # FIX: Use original card title for routing if available
        if hasattr(self.orchestrator, 'original_card_title'):
            routing_name = self.orchestrator.original_card_title
            print(f"📝 Using original card title for version check: '{routing_name}'")
        elif hasattr(self.orchestrator, 'card_name'):
            routing_name = self.orchestrator.card_name
            print(f"📝 Using card name for version check: '{routing_name}'")
        else:
            # Fallback to generated name
            type_suffix = self._get_type_suffix(processing_mode)
            routing_name = (f"GH {project_info['project_name']} "
                        f"{project_info.get('ad_type', '')} "
                        f"{project_info.get('test_name', '')} {type_suffix}")
            print(f"⚠️ Using generated name for version check: '{routing_name}'")
        
        def check_sheets():
            error, start_version = write_to_google_sheets(routing_name, [], creds)
            if error:
                raise Exception(f"Failed to check Google Sheets: {error}")
            return start_version
        
        return self.orchestrator.monitor.execute_with_activity_monitoring(
            check_sheets, "Google Sheets Version Check", no_activity_timeout=120
        )
    
    def _get_type_designation(self, processing_mode):
        """Get type designation for output naming"""
        if "quiz" in processing_mode:
            return "quiz"
        elif "svsl" in processing_mode:
            return "svsl"
        elif "vsl" in processing_mode:
            return "vsl"
        return "quiz"
    
    def _get_type_suffix(self, processing_mode):
        """Get type suffix for concept name"""
        if "quiz" in processing_mode:
            return "Quiz"
        elif "svsl" in processing_mode:
            return "SVSL"
        elif "vsl" in processing_mode:
            return "VSL"
        return "Quiz"