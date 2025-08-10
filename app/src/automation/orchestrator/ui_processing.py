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
        """
        Process videos with progress updates - FIXED to ensure cleanup always runs
        """
        
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
        
        # CRITICAL FIX: Use try/finally to ensure cleanup ALWAYS runs
        sheets_success = False
        try:
            progress_callback(95, "📊 Updating Google Sheets...")
            
            # Write to sheets - this might fail due to protection errors
            self.orchestrator.processing_steps.write_to_sheets(
                project_info,
                processed_files,
                creds
            )
            sheets_success = True
            print("✅ Google Sheets update completed successfully")
            
        except Exception as sheets_error:
            print(f"⚠️ Google Sheets update failed: {sheets_error}")
            # Continue processing - don't let sheets failure stop file cleanup
            
        finally:
            # CRITICAL: Always run cleanup regardless of sheets success/failure
            try:
                progress_callback(97, "📁 Organizing files...")
                
                print("🧹 Running file cleanup (regardless of sheets status)...")
                self.orchestrator.processing_steps.finalize_and_cleanup(
                    processed_files,
                    project_info, 
                    creds,
                    project_paths
                )
                print("✅ File cleanup completed")
                
            except Exception as cleanup_error:
                print(f"⚠️ File cleanup failed: {cleanup_error}")
                # Don't fail the entire process for cleanup issues
        
        # Update progress based on overall success
        if sheets_success:
            progress_callback(100, "✅ Processing complete!")
        else:
            progress_callback(100, "⚠️ Processing complete (Google Sheets failed)")
        
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
            
            # Create concept name for version lookup
            project_name = project_info.get('project_name', 'Unknown Project')
            account_name = project_info.get('account_code', 'GH')
            ad_type = project_info.get('ad_type', 'VTD')
            test_name = project_info.get('test_name', '0000')
            
            concept_name = f"{account_name} {project_name} {ad_type} {test_name} {endpoint_type}"
            
            print(f"🔍 Looking up starting version for: '{concept_name}'")
            
            # Get next version from sheets
            start_version = write_to_google_sheets(
                project_info, [], creds, 
                routing_name=concept_name,
                column1_name=concept_name,
                dry_run=True  # Just get version, don't write
            )
            
            print(f"📊 Starting version from sheets: {start_version}")
            
        except Exception as version_error:
            print(f"⚠️ Could not get starting version from sheets: {version_error}")
            print("📊 Using default starting version: 1")
        
        return start_version