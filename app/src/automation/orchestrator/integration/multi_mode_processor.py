# app/src/automation/orchestrator/integration/multi_mode_processor.py
"""
Multi-Mode Processing Logic
Extracted from ui_integration_base.py for better maintainability
Enhanced with improved video dimension handling
"""

import time
import os
from ...workflow_dialog.helpers import create_processing_result_from_orchestrator
from .mode_utilities import ModeUtilities

class MultiModeProcessor:
    """Handles multi-mode processing workflow"""
    
    def __init__(self, ui_integration):
        self.ui = ui_integration
        self.orchestrator = ui_integration.orchestrator
        self.mode_utils = ModeUtilities()
    
    def process_multiple_modes(self, confirmation_data, selected_modes, progress_callback, use_transitions):
        """Process multiple modes sequentially with enhanced error handling"""
        
        all_processed_files = []
        all_output_folders = []
        original_project_name = self.orchestrator.project_info.get('project_name', '')
        
        # Download assets only once
        downloaded_once = False
        
        for i, mode in enumerate(selected_modes, 1):
            print(f"\n{'='*60}")
            print(f"🔄 Processing mode {i}/{len(selected_modes)}: {mode.upper()}")
            print(f"{'='*60}")
            
            try:
                # Update progress
                mode_progress = int((i - 1) / len(selected_modes) * 100)
                progress_callback(mode_progress, f"Processing mode {i}/{len(selected_modes)}: {mode}")
                
                # Process this mode
                mode_result = self._process_single_mode_iteration(
                    mode, i, len(selected_modes), confirmation_data, 
                    progress_callback, use_transitions, original_project_name,
                    downloaded_once
                )
                
                # Update tracking
                all_processed_files.extend(mode_result['processed_files'])
                all_output_folders.append(mode_result['output_folder'])
                downloaded_once = mode_result['downloaded_once']
                
            except Exception as mode_error:
                print(f"❌ Error processing mode {mode}: {mode_error}")
                
                # Check if it's a video dimension issue
                if "video dimensions" in str(mode_error).lower():
                    print(f"🔧 Attempting video dimension fix for {mode}...")
                    try:
                        mode_result = self._handle_mode_video_dimension_error(
                            mode, mode_error, i, len(selected_modes), 
                            confirmation_data, progress_callback, use_transitions,
                            original_project_name, downloaded_once
                        )
                        all_processed_files.extend(mode_result['processed_files'])
                        all_output_folders.append(mode_result['output_folder'])
                        downloaded_once = mode_result['downloaded_once']
                        continue
                    except Exception as fallback_error:
                        print(f"❌ Fallback failed for {mode}: {fallback_error}")
                
                # If we can't recover, continue with other modes
                print(f"⚠️ Skipping mode {mode} due to error: {mode_error}")
                continue
        
        # Reset to original project name
        self.orchestrator.project_info['project_name'] = original_project_name
        
        # Final progress update
        success_count = len(all_output_folders)
        progress_callback(100, f"✅ Completed {success_count}/{len(selected_modes)} processing modes!")
        
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
        result.success_count = success_count
        
        return result
    
    def _process_single_mode_iteration(self, mode, mode_index, total_modes, 
                                     confirmation_data, progress_callback, 
                                     use_transitions, original_project_name, downloaded_once):
        """Process a single mode within multi-mode workflow"""
        
        # Update mode for this iteration
        self.orchestrator.processing_mode = mode
        confirmation_data.processing_mode = mode
        
        # Add mode suffix to project name
        mode_suffix = self.mode_utils.get_mode_suffix(mode)
        self.orchestrator.project_info['project_name'] = f"{original_project_name} {mode_suffix}"
        
        # Step 1: Check and update project name
        final_project_name = self.ui.progress.check_and_update_project_name(progress_callback)
        
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
        
        # Step 3: Create project structure for this mode
        self._create_mode_project_structure()
        
        # Step 4: Process videos for this mode
        progress_percent = 30 + (mode_index * 30 / total_modes)
        progress_callback(progress_percent, f"📹 Processing {len(self.orchestrator.downloaded_videos)} files for {mode}...")
        
        # Configure video processor
        self._configure_video_processor()
        
        # Process videos with error handling
        self.orchestrator.processed_files = self.orchestrator.processing_steps.process_videos(
            self.orchestrator.downloaded_videos,
            self.orchestrator.project_paths,
            self.orchestrator.project_info,
            self.orchestrator.processing_mode,
            self.orchestrator.creds
        )
        
        # Step 5: Write to Google Sheets
        self._update_mode_google_sheets(mode, mode_index, total_modes, progress_callback)
        
        # Step 6: Generate reports
        self._generate_mode_reports(mode, use_transitions)
        
        # Step 7: Cleanup
        self._cleanup_mode_processing(mode)
        
        return {
            'processed_files': self.orchestrator.processed_files,
            'output_folder': self.orchestrator.generated_folder_name,
            'downloaded_once': downloaded_once
        }
    
    def _handle_mode_video_dimension_error(self, mode, error, mode_index, total_modes,
                                         confirmation_data, progress_callback, 
                                         use_transitions, original_project_name, downloaded_once):
        """Handle video dimension errors for specific mode"""
        
        print(f"🔧 Implementing video dimension fallback for {mode}...")
        
        # Set fallback dimensions
        fallback_dimensions = self._get_fallback_dimensions()
        print(f"✅ Using fallback dimensions for {mode}: {fallback_dimensions}")
        
        from ...video_processor import set_fallback_dimensions
        set_fallback_dimensions(*fallback_dimensions)
        
        # Retry the mode processing
        return self._process_single_mode_iteration(
            mode, mode_index, total_modes, confirmation_data, 
            progress_callback, use_transitions, original_project_name, downloaded_once
        )
    
    def _create_mode_project_structure(self):
        """Create project structure for current mode"""
        from ...workflow_utils import create_project_structure
        from app.src.naming_generator import generate_project_folder_name

        # Generate the folder name
        project_name = self.orchestrator.project_info.get('project_name', '')
        first_video = self.orchestrator.downloaded_videos[0] if self.orchestrator.downloaded_videos else ''
        
        folder_type = self.mode_utils.get_folder_type(self.orchestrator.processing_mode)
        
        # Generate the folder name (returns a string)
        generated_folder_name = generate_project_folder_name(
            project_name, 
            first_video, 
            folder_type
        )

        print(f"📁 Generated folder name for {self.orchestrator.processing_mode}: {generated_folder_name}")

        # Create structure with the string name (not the dict)
        self.orchestrator.project_paths = create_project_structure(generated_folder_name)
        
        print(f"📁 Created folder structure for {self.orchestrator.processing_mode} at: {self.orchestrator.project_paths['project_root']}")
        
        # Store generated folder name
        self.orchestrator.generated_folder_name = os.path.basename(
            self.orchestrator.project_paths['project_root']
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
    
    def _get_fallback_dimensions(self):
        """Get fallback dimensions based on common video formats"""
        return (1080, 1920)  # 9:16 vertical format
    
    def _update_mode_google_sheets(self, mode, mode_index, total_modes, progress_callback):
        """Update Google Sheets for specific mode"""
        try:
            sheets_progress = 70 + (mode_index * 15 / total_modes)
            progress_callback(sheets_progress, f"📊 Updating Google Sheets for {mode}...")
            
            self.orchestrator.processing_steps.write_to_sheets(
                self.orchestrator.project_info,
                self.orchestrator.processed_files,
                self.orchestrator.creds
            )
            print(f"✅ Google Sheets updated for {mode}")
            
        except Exception as sheets_error:
            print(f"⚠️ Google Sheets update failed for {mode}: {sheets_error}")
    
    def _generate_mode_reports(self, mode, use_transitions):
        """Generate breakdown reports for specific mode"""
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
    
    def _cleanup_mode_processing(self, mode):
        """Cleanup processing for specific mode"""
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