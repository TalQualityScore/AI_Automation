# app/src/automation/orchestrator/integration/single_mode_processor.py
"""
Single Mode Processing Logic
Extracted from ui_integration_base.py for better maintainability
"""

import time
import os
from ...workflow_dialog.helpers import create_processing_result_from_orchestrator

class SingleModeProcessor:
    """Handles single-mode processing workflow"""
    
    def __init__(self, ui_integration):
        self.ui = ui_integration
        self.orchestrator = ui_integration.orchestrator
    
    def process_single_mode(self, confirmation_data, progress_callback, use_transitions):
        """Process single mode - original working logic"""
        
        # Step 1: Check and update project name
        final_project_name = self.ui.progress.check_and_update_project_name(progress_callback)
        
        # Step 2: Download assets
        progress_callback(25, "📥 Downloading Assets from Google Drive...")
        print(f"🔍 PASSING UPDATED PROJECT_INFO TO SETUP: '{self.orchestrator.project_info['project_name']}'")
        
        # Call download_and_setup
        self.orchestrator.creds, self.orchestrator.downloaded_videos, self.orchestrator.project_paths = \
            self.orchestrator.processing_steps.download_and_setup(
                self.orchestrator.card_data, 
                self.orchestrator.project_info
            )
        
        # Store generated folder name
        self.orchestrator.generated_folder_name = os.path.basename(
            self.orchestrator.project_paths['project_root']
        )
        print(f"📁 GENERATED FOLDER NAME: '{self.orchestrator.generated_folder_name}'")
        
        # Step 3: Process videos with improved error handling
        total_videos = len(self.orchestrator.downloaded_videos)
        progress_callback(60, f"📹 Processing {total_videos} files...")
        
        self.orchestrator.video_paths_tracking = []
        
        print(f"🔍 PASSING UPDATED PROJECT_INFO TO PROCESS_VIDEOS: '{self.orchestrator.project_info['project_name']}'")
        
        # Set account and platform for video processor before processing
        self._configure_video_processor()
        
        # Process videos with enhanced error handling
        try:
            self.orchestrator.processed_files = self.orchestrator.processing_steps.process_videos(
                self.orchestrator.downloaded_videos,
                self.orchestrator.project_paths,
                self.orchestrator.project_info,
                self.orchestrator.processing_mode,
                self.orchestrator.creds
            )
        except Exception as video_error:
            print(f"❌ Video processing failed: {video_error}")
            # Check if it's a video dimension issue
            if "video dimensions" in str(video_error).lower():
                print("🔧 Attempting video dimension fix...")
                return self._handle_video_dimension_error(video_error, progress_callback)
            else:
                raise video_error
        
        # Step 4: Write to Google Sheets
        self._update_google_sheets(progress_callback)
        
        # Step 5: Generate reports
        self._generate_reports(progress_callback, use_transitions)
        
        # Step 6: Cleanup and organize files
        self._finalize_processing(progress_callback)
        
        # Final progress and result
        progress_callback(100, "✅ Processing complete!")
        
        return create_processing_result_from_orchestrator(
            self.orchestrator.processed_files,
            self.orchestrator.start_time,
            self.orchestrator.project_paths.get('project_root', '.'),
            success=True
        )
    
    def _configure_video_processor(self):
        """Configure video processor with account and platform"""
        account_code = self.orchestrator.project_info.get('account_code') or \
                      self.orchestrator.project_info.get('detected_account_code')
        platform_code = self.orchestrator.project_info.get('platform_code') or \
                       self.orchestrator.project_info.get('detected_platform_code')
        
        if account_code and platform_code:
            print(f"🎯 Setting processor context: Account={account_code}, Platform={platform_code}")
            from ...video_processor import set_processor_account_platform
            set_processor_account_platform(account_code, platform_code)
    
    def _handle_video_dimension_error(self, error, progress_callback):
        """Handle video dimension analysis errors"""
        print("🔧 Implementing video dimension fallback...")
        
        # Try to get dimensions using alternative method
        try:
            # Use a fallback dimension detection
            fallback_dimensions = self._get_fallback_dimensions()
            print(f"✅ Using fallback dimensions: {fallback_dimensions}")
            
            # Set fallback dimensions in video processor
            from ...video_processor import set_fallback_dimensions
            set_fallback_dimensions(*fallback_dimensions)
            
            # Retry processing with fallback
            self.orchestrator.processed_files = self.orchestrator.processing_steps.process_videos(
                self.orchestrator.downloaded_videos,
                self.orchestrator.project_paths,
                self.orchestrator.project_info,
                self.orchestrator.processing_mode,
                self.orchestrator.creds
            )
            
            progress_callback(100, "✅ Processing complete (using fallback dimensions)")
            
            return create_processing_result_from_orchestrator(
                self.orchestrator.processed_files,
                self.orchestrator.start_time,
                self.orchestrator.project_paths.get('project_root', '.'),
                success=True
            )
            
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            raise error  # Re-raise original error
    
    def _get_fallback_dimensions(self):
        """Get fallback dimensions based on common video formats"""
        # Return common mobile video dimensions as fallback
        return (1080, 1920)  # 9:16 vertical format
    
    def _update_google_sheets(self, progress_callback):
        """Update Google Sheets with results"""
        sheets_success = False
        try:
            progress_callback(90, "📊 Updating Google Sheets...")
            
            self.orchestrator.processing_steps.write_to_sheets(
                self.orchestrator.project_info,
                self.orchestrator.processed_files,
                self.orchestrator.creds
            )
            sheets_success = True
            print("✅ Google Sheets update completed successfully")
            
        except Exception as sheets_error:
            print(f"⚠️ Google Sheets update failed: {sheets_error}")
            # Continue - don't let sheets failure stop processing
        
        return sheets_success
    
    def _generate_reports(self, progress_callback, use_transitions):
        """Generate breakdown reports"""
        progress_callback(93, "📄 Generating reports...")

        try:
            from automation.reports.breakdown_report import generate_breakdown_report
            
            # Get output folder
            output_folder = self.orchestrator.project_paths.get('project_root')
            if not output_folder or not os.path.exists(output_folder):
                ame_folder = self.orchestrator.project_paths.get('_AME', '')
                if ame_folder and os.path.exists(ame_folder):
                    output_folder = os.path.dirname(ame_folder)
                    print(f"📁 Using parent of _AME folder: {output_folder}")
            
            print(f"📄 Generating breakdown report in: {output_folder}")
            
            # Calculate duration
            duration_seconds = time.time() - self.orchestrator.start_time
            duration_str = f"{int(duration_seconds // 60)}m {int(duration_seconds % 60)}s"
            
            # Generate report
            self.orchestrator.breakdown_report_path = generate_breakdown_report(
                self.orchestrator.processed_files,
                output_folder,
                duration_str,
                use_transitions
            )
            
            if self.orchestrator.breakdown_report_path and os.path.exists(self.orchestrator.breakdown_report_path):
                print(f"✅ Breakdown report saved: {self.orchestrator.breakdown_report_path}")
            else:
                print(f"⚠️ Breakdown report path returned but file not found")
                
        except ImportError as e:
            print(f"⚠️ Breakdown report import failed: {e}")
        except Exception as e:
            print(f"⚠️ Could not generate breakdown report: {e}")
    
    def _finalize_processing(self, progress_callback):
        """Finalize and cleanup processing"""
        try:
            progress_callback(95, "📁 Organizing files...")
            
            print("🧹 Running file cleanup...")
            self.orchestrator.processing_steps.finalize_and_cleanup(
                self.orchestrator.processed_files,
                self.orchestrator.project_info, 
                self.orchestrator.creds,
                self.orchestrator.project_paths
            )
            print("✅ File cleanup completed")
            
        except Exception as cleanup_error:
            print(f"⚠️ File cleanup failed: {cleanup_error}")
            # Don't fail entire process for cleanup issues