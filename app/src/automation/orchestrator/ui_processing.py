# app/src/automation/orchestrator/ui_processing.py
"""
UI Processing Module
Handles video processing with progress updates
Split from ui_integration.py for better organization
"""

import time
import os

class UIProcessing:
    """Handles video processing with UI updates"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def setup_project_with_progress(self, card_data, project_info, progress_callback):
        """Setup project with progress updates"""
        progress_callback(30, "🔑 Setting up credentials...")
        print(f"🔍 SETUP_PROJECT RECEIVED PROJECT_INFO: '{project_info['project_name']}'")
        
        # This will create folders using the updated project name
        creds, downloaded_videos, project_paths = self.orchestrator.processing_steps.setup_project(
            card_data, project_info
        )
        
        progress_callback(50, "📁 Project structure created...")
        print(f"📁 PROJECT STRUCTURE CREATED AT: '{project_paths['project_root']}'")
        
        return creds, downloaded_videos, project_paths
    
    def process_videos_with_progress(self, downloaded_videos, project_paths, project_info, 
                                    processing_mode, creds, progress_callback, use_transitions=True):
        """Process videos with progress updates showing video X of Y"""
        
        total_videos = len(downloaded_videos)
        processed_files = []
        
        progress_callback(70, f"🎬 Starting video processing... ({total_videos} files)")
        print(f"🔍 PROCESS_VIDEOS RECEIVED PROJECT_INFO: '{project_info['project_name']}'")
        
        # Determine target dimensions
        target_width, target_height = self._get_target_dimensions(downloaded_videos, processing_mode)
        
        # Get starting version number
        start_version = self._get_starting_version(project_info, creds)
        
        # Process each video with counter
        for i, client_video in enumerate(downloaded_videos):
            version_num = start_version + i
            current_video = i + 1
            
            # Update progress with "Processing video X of Y"
            progress_percentage = 70 + (20 * current_video / total_videos)
            progress_callback(
                progress_percentage, 
                f"--- Processing Version {version_num:02d} ({processing_mode}) --- Video {current_video} of {total_videos}"
            )
            
            processed_file = self.orchestrator.processing_steps.process_single_video(
                client_video, project_paths, project_info, processing_mode,
                version_num, target_width, target_height
            )
            
            # Track video paths for breakdown report
            self._add_video_paths_to_file(processed_file, client_video, processing_mode, project_info)
            
            processed_files.append(processed_file)
        
        progress_callback(85, "✅ Video processing complete...")
        print(f"✅ PROCESSED {len(processed_files)} FILES")
        
        return processed_files
    
    def _get_target_dimensions(self, downloaded_videos, processing_mode):
        """Get target video dimensions"""
        if processing_mode == "save_only":
            return None, None
        
        from ..video_processor import get_video_dimensions
        target_width, target_height, _ = get_video_dimensions(downloaded_videos[0])
        return target_width, target_height
    
    def _get_starting_version(self, project_info, creds):
        """Get starting version number from Google Sheets"""
        start_version = 1  # Default
        
        try:
            # Try to import the function from various locations
            from ..api_clients import check_google_sheet_for_project
            _, start_version = check_google_sheet_for_project(
                project_info['project_name'], 
                creds
            )
            print(f"📊 Starting from version: {start_version}")
        except ImportError:
            try:
                from ..api_clients.google_sheets import check_google_sheet_for_project
                _, start_version = check_google_sheet_for_project(
                    project_info['project_name'], 
                    creds
                )
                print(f"📊 Starting from version: {start_version}")
            except ImportError:
                try:
                    from ..workflow_utils import check_google_sheet_for_project
                    _, start_version = check_google_sheet_for_project(
                        project_info['project_name'], 
                        creds
                    )
                    print(f"📊 Starting from version: {start_version}")
                except ImportError:
                    print("⚠️ check_google_sheet_for_project not found, using default start version 1")
                    start_version = 1
        except Exception as e:
            print(f"⚠️ Error checking Google Sheet: {e}, using default start version 1")
            start_version = 1
        
        return start_version
    
    def _add_video_paths_to_file(self, processed_file, client_video, processing_mode, project_info):
        """Add video paths to processed file for breakdown report"""
        processed_file['client_video_path'] = client_video
        
        if 'connector' in processing_mode:
            platform = project_info.get('detected_platform_code', 'FB')
            processed_file['connector_path'] = f"Assets/Videos/connectors/{platform}/connector.mp4"
        
        if 'quiz' in processing_mode:
            platform = project_info.get('detected_platform_code', 'FB')
            processed_file['quiz_path'] = f"Assets/Videos/quiz_outro/{platform}/quiz_outro.mp4"