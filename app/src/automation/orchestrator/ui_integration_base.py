# app/src/automation/orchestrator/ui_integration_base.py - COMPLETE FIXED VERSION
"""
UI Integration Base Module - Main orchestrator
Fixed version with breakdown report location fix AND multi-mode support
"""

import time
import os

from ..workflow_dialog.helpers import create_processing_result_from_orchestrator
from .ui_preparation import UIPreparation
from .ui_processing import UIProcessing
from .ui_progress import UIProgress
from .ui_sheets import UISheets

class UIIntegration:
    """Main UI Integration orchestrator - delegates to specialized modules"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        
        # Initialize specialized modules
        self.preparation = UIPreparation(orchestrator)
        self.processing = UIProcessing(orchestrator)
        self.progress = UIProgress(orchestrator)
        self.sheets = UISheets(orchestrator)
    
    def prepare_confirmation_data(self):
        """Prepare data for the confirmation dialog"""
        return self.preparation.prepare_confirmation_data()
    
    def ui_processing_callback(self, confirmation_data, progress_callback, use_transitions=True):
        """Main processing callback - orchestrates the workflow"""
        
        # Configure transitions
        from ..video_processor import configure_transitions
        configure_transitions(use_transitions)
        print(f"🎬 Processing with transitions: {'ENABLED' if use_transitions else 'DISABLED'}")
        
        try:
            self.orchestrator.start_time = time.time()
            
            # NEW: Check for multi-mode processing
            selected_modes = getattr(confirmation_data, 'selected_processing_modes', None)
            if selected_modes and len(selected_modes) > 1:
                print(f"🔄 Multi-mode processing detected: {selected_modes}")
                return self._process_multiple_modes(confirmation_data, selected_modes, progress_callback, use_transitions)
            
            # EXISTING SINGLE-MODE PROCESSING CONTINUES UNCHANGED
            # Step 1: Check and update project name
            final_project_name = self.progress.check_and_update_project_name(progress_callback)
            
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
            
            # Step 3: Process videos
            total_videos = len(self.orchestrator.downloaded_videos)
            progress_callback(60, f"📹 Processing {total_videos} files...")
            
            self.orchestrator.video_paths_tracking = []
            
            print(f"🔍 PASSING UPDATED PROJECT_INFO TO PROCESS_VIDEOS: '{self.orchestrator.project_info['project_name']}'")
            
            # Set account and platform for video processor before processing
            account_code = self.orchestrator.project_info.get('account_code') or \
                          self.orchestrator.project_info.get('detected_account_code')
            platform_code = self.orchestrator.project_info.get('platform_code') or \
                           self.orchestrator.project_info.get('detected_platform_code')
            
            if account_code and platform_code:
                print(f"🎯 Setting processor context: Account={account_code}, Platform={platform_code}")
                from ..video_processor import set_processor_account_platform
                set_processor_account_platform(account_code, platform_code)
            
            # Process videos
            self.orchestrator.processed_files = self.orchestrator.processing_steps.process_videos(
                self.orchestrator.downloaded_videos,
                self.orchestrator.project_paths,
                self.orchestrator.project_info,
                self.orchestrator.processing_mode,
                self.orchestrator.creds
            )
            
            # Step 4: Write to Google Sheets (wrapped in try/except so cleanup always runs)
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
                # Continue - don't let sheets failure stop cleanup
            
            # Step 5: Generate reports FIRST (while files are still in temp_downloads)
            progress_callback(93, "📄 Generating reports...")

            # Generate breakdown report BEFORE moving files
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
                
                # Generate report WHILE files are still in original location
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
                import traceback
                traceback.print_exc()

            # Step 6: NOW organize and move files (AFTER breakdown report is done)
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

            # Final progress update
            if sheets_success:
                progress_callback(100, "✅ Processing complete!")
            else:
                progress_callback(100, "⚠️ Processing complete (Google Sheets failed)")
            
            # Create success result
            result = create_processing_result_from_orchestrator(
                self.orchestrator.processed_files,
                self.orchestrator.start_time,
                self.orchestrator.project_paths.get('project_root', '.'),
                success=True
            )
            
            return result
            
        except Exception as e:
            print(f"❌ PROCESSING ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            # Create error result
            from ..workflow_data_models import ProcessingResult
            return ProcessingResult(
                success=False,
                duration='',
                processed_files=[],
                output_folder='',
                error_message=str(e),
                error_solution=(
                    "1. Check your internet connection\n"
                    "2. Verify all API credentials are correct\n"
                    "3. Ensure input files and links are accessible\n"
                    "4. Try restarting the application\n"
                    "5. Check the error log for more details"
                )
            )
    
    def _process_multiple_modes(self, confirmation_data, selected_modes, progress_callback, use_transitions):
        """NEW METHOD: Process multiple modes sequentially"""
        
        all_processed_files = []
        all_output_folders = []
        original_project_name = self.orchestrator.project_info.get('project_name', '')
        
        # Download assets only once
        downloaded_once = False
        
        for i, mode in enumerate(selected_modes, 1):
            print(f"\n{'='*60}")
            print(f"🔄 Processing mode {i}/{len(selected_modes)}: {mode.upper()}")
            print(f"{'='*60}")
            
            # Update progress
            mode_progress = int((i - 1) / len(selected_modes) * 100)
            progress_callback(mode_progress, f"Processing mode {i}/{len(selected_modes)}: {mode}")
            
            # Update mode for this iteration
            self.orchestrator.processing_mode = mode
            confirmation_data.processing_mode = mode
            
            # Add mode suffix to project name
            mode_suffix = self._get_mode_suffix(mode)
            self.orchestrator.project_info['project_name'] = f"{original_project_name} {mode_suffix}"
            
            # Step 1: Check and update project name
            final_project_name = self.progress.check_and_update_project_name(progress_callback)
            
            # Step 2: Download assets (only first time)
            if not downloaded_once:
                progress_callback(25, "📥 Downloading Assets from Google Drive...")
                print(f"🔍 PASSING UPDATED PROJECT_INFO TO SETUP: '{self.orchestrator.project_info['project_name']}'")
                
                self.orchestrator.creds, self.orchestrator.downloaded_videos, _ = \
                    self.orchestrator.processing_steps.download_and_setup(
                        self.orchestrator.card_data, 
                        self.orchestrator.project_info
                    )
                downloaded_once = True
            
            # Create project structure for this mode
            # Use the same method that works in download_and_setup
            from ..workflow_utils import create_project_structure
            
            # Store original mode if exists
            original_mode = self.orchestrator.project_info.get('processing_mode', None)
            
            # Set the current mode in project_info temporarily
            self.orchestrator.project_info['processing_mode'] = self.orchestrator.processing_mode
            
            # Create structure (it will use the mode from project_info)
            self.orchestrator.project_paths = create_project_structure(self.orchestrator.project_info)
            
            # Restore original mode
            if original_mode:
                self.orchestrator.project_info['processing_mode'] = original_mode
            
            print(f"📁 Created folder structure for {self.orchestrator.processing_mode} at: {self.orchestrator.project_paths['project_root']}")
            
            # Store generated folder name
            self.orchestrator.generated_folder_name = os.path.basename(
                self.orchestrator.project_paths['project_root']
            )
            all_output_folders.append(self.orchestrator.generated_folder_name)
            print(f"📁 GENERATED FOLDER NAME FOR {mode}: '{self.orchestrator.generated_folder_name}'")
            
            # Step 3: Process videos for this mode
            progress_percent = 30 + (i * 30 / len(selected_modes))
            progress_callback(progress_percent, f"📹 Processing {len(self.orchestrator.downloaded_videos)} files for {mode}...")
            
            # Set account and platform for video processor
            account_code = self.orchestrator.project_info.get('account_code') or \
                          self.orchestrator.project_info.get('detected_account_code')
            platform_code = self.orchestrator.project_info.get('platform_code') or \
                           self.orchestrator.project_info.get('detected_platform_code')
            
            if account_code and platform_code:
                print(f"🎯 Setting processor context: Account={account_code}, Platform={platform_code}")
                from ..video_processor import set_processor_account_platform
                set_processor_account_platform(account_code, platform_code)
            
            # Process videos
            self.orchestrator.processed_files = self.orchestrator.processing_steps.process_videos(
                self.orchestrator.downloaded_videos,
                self.orchestrator.project_paths,
                self.orchestrator.project_info,
                self.orchestrator.processing_mode,
                self.orchestrator.creds
            )
            
            all_processed_files.extend(self.orchestrator.processed_files)
            
            # Step 4: Write to Google Sheets for each mode
            try:
                sheets_progress = 70 + (i * 15 / len(selected_modes))
                progress_callback(sheets_progress, f"📊 Updating Google Sheets for {mode}...")
                
                self.orchestrator.processing_steps.write_to_sheets(
                    self.orchestrator.project_info,
                    self.orchestrator.processed_files,
                    self.orchestrator.creds
                )
                print(f"✅ Google Sheets updated for {mode}")
                
            except Exception as sheets_error:
                print(f"⚠️ Google Sheets update failed for {mode}: {sheets_error}")
            
            # Step 5: Generate breakdown report for this mode
            try:
                from automation.reports.breakdown_report import generate_breakdown_report
                
                output_folder = self.orchestrator.project_paths.get('project_root')
                if not output_folder or not os.path.exists(output_folder):
                    ame_folder = self.orchestrator.project_paths.get('_AME', '')
                    if ame_folder and os.path.exists(ame_folder):
                        output_folder = os.path.dirname(ame_folder)
                
                print(f"📄 Generating breakdown report for {mode} in: {output_folder}")
                
                duration_seconds = time.time() - self.orchestrator.start_time
                duration_str = f"{int(duration_seconds // 60)}m {int(duration_seconds % 60)}s"
                
                breakdown_path = generate_breakdown_report(
                    self.orchestrator.processed_files,
                    output_folder,
                    duration_str,
                    use_transitions
                )
                
                if breakdown_path and os.path.exists(breakdown_path):
                    print(f"✅ Breakdown report saved for {mode}: {breakdown_path}")
                    
            except Exception as e:
                print(f"⚠️ Could not generate breakdown report for {mode}: {e}")
            
            # Step 6: Cleanup for this mode
            try:
                print(f"🧹 Running file cleanup for {mode}...")
                self.orchestrator.processing_steps.finalize_and_cleanup(
                    self.orchestrator.processed_files,
                    self.orchestrator.project_info, 
                    self.orchestrator.creds,
                    self.orchestrator.project_paths
                )
                print(f"✅ File cleanup completed for {mode}")
                
            except Exception as cleanup_error:
                print(f"⚠️ File cleanup failed for {mode}: {cleanup_error}")
        
        # Reset to original project name
        self.orchestrator.project_info['project_name'] = original_project_name
        
        # Final progress update
        progress_callback(100, f"✅ Completed all {len(selected_modes)} processing modes!")
        
        # Create combined result
        result = create_processing_result_from_orchestrator(
            all_processed_files,
            self.orchestrator.start_time,
            ', '.join(all_output_folders),  # Multiple folders
            success=True
        )
        
        # Store additional info for results display
        result.multi_mode_folders = all_output_folders
        result.multi_mode_count = len(selected_modes)
        
        return result
    
    def _get_mode_suffix(self, mode):
        """Get appropriate suffix for mode"""
        mode_suffixes = {
            'quiz_only': 'Quiz',
            'vsl_only': 'VSL',
            'svsl_only': 'SVSL',
            'connector_quiz': 'Connector Quiz',
            'connector_vsl': 'Connector VSL',
            'connector_svsl': 'Connector SVSL',
            'save_only': 'Original'
        }
        return mode_suffixes.get(mode, mode.upper())