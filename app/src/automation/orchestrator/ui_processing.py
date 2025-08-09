# app/src/automation/orchestrator/ui_processing.py
"""
UI Processing Module
Handles video processing with progress updates
Split from ui_integration.py for better organization
"""

import time
import os

class UIProcessing:
    """Handles UI processing operations"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def setup_project_with_progress(self, card_data, project_info, progress_callback):
        """Download videos and set up project structure with progress updates"""
        
        print(f"🔍 SETUP_PROJECT RECEIVED PROJECT_INFO: '{project_info['project_name']}'")
        
        progress_callback(30, "📥 Downloading videos from Google Drive...")
        
        # Use the correct method name: download_and_setup instead of setup_project
        creds, downloaded_videos, project_paths = self.orchestrator.processing_steps.download_and_setup(
            card_data,
            project_info
        )
        
        progress_callback(50, f"✅ Downloaded {len(downloaded_videos)} videos")
        
        return creds, downloaded_videos, project_paths
    
    def process_videos_with_progress(self, downloaded_videos, project_paths, project_info, 
                                    processing_mode, creds, progress_callback):
        """Process videos with progress updates"""
        
        # Set account and platform for video processor
        account_code = project_info.get('account_code') or project_info.get('detected_account_code')
        platform_code = project_info.get('platform_code') or project_info.get('detected_platform_code')
        
        if account_code and platform_code:
            print(f"🎯 Setting processor context: Account={account_code}, Platform={platform_code}")
            from ..video_processor import set_processor_account_platform
            set_processor_account_platform(account_code, platform_code)
        
        total_videos = len(downloaded_videos)
        
        for i, video in enumerate(downloaded_videos, 1):
            progress = 60 + (30 * i / total_videos)
            progress_callback(progress, f"Processing video {i}/{total_videos}...")
        
        # Process videos using the processing_steps
        processed_files = self.orchestrator.processing_steps.process_videos(
            downloaded_videos,
            project_paths,
            project_info,
            processing_mode,
            creds
        )
        
        progress_callback(95, "📊 Updating Google Sheets...")
        
        # Write to sheets
        self.orchestrator.processing_steps.write_to_sheets(
            project_info,
            processed_files,
            creds
        )
        
        progress_callback(100, "✅ Processing complete!")
        
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
            # Try to import the function from api_clients
            from ..api_clients import write_to_google_sheets
            
            # Determine endpoint type for concept name
            endpoint_type = "Quiz"  # Default
            processing_mode = project_info.get('processing_mode', '')
            if 'svsl' in processing_mode.lower():
                endpoint_type = "SVSL"
            elif 'vsl' in processing_mode.lower():
                endpoint_type = "VSL"
            
            # Build concept name with correct endpoint type
            concept_name = f"GH {project_info['project_name']} {project_info.get('ad_type', '')} {project_info.get('test_name', '')} {endpoint_type}"
            
            # Use write_to_google_sheets with empty data to check version
            error, start_version = write_to_google_sheets(concept_name, [], creds)
            if not error:
                print(f"📊 Starting from version: {start_version}")
            else:
                print(f"⚠️ Could not check sheet version: {error}")
                start_version = 1
        except ImportError as e:
            print(f"⚠️ write_to_google_sheets import error: {e}")
            start_version = 1
        except Exception as e:
            print(f"⚠️ Error checking Google Sheet: {e}, using default start version 1")
            start_version = 1
        
        return start_version
    
    def _add_video_paths_to_file(self, processed_file, client_video, processing_mode, project_info):
        """Add video paths to processed file for breakdown report"""
        processed_file['client_video_path'] = client_video
        
        # Get account and platform for correct asset paths
        account_code = project_info.get('account_code') or project_info.get('detected_account_code', 'OO')
        platform_code = project_info.get('platform_code') or project_info.get('detected_platform_code', 'FB')
        
        # Add paths based on processing mode - using new folder structure
        if 'connector' in processing_mode:
            processed_file['connector_path'] = f"Assets/Videos/{account_code}/{platform_code}/Connectors/connector.mp4"
        
        if 'quiz' in processing_mode:
            processed_file['quiz_path'] = f"Assets/Videos/{account_code}/{platform_code}/Quiz/quiz_outro.mp4"
        
        if 'svsl' in processing_mode:
            processed_file['svsl_path'] = f"Assets/Videos/{account_code}/{platform_code}/SVSL/svsl.mp4"
        
        if 'vsl' in processing_mode:
            processed_file['vsl_path'] = f"Assets/Videos/{account_code}/{platform_code}/VSL/vsl.mp4"