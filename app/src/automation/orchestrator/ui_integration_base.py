# app/src/automation/orchestrator/ui_integration_base.py - COMPLETE FIXED VERSION
"""
UI Integration Base Module - Main orchestrator
Enhanced with multi-mode processing support - BASED ON YOUR ACTUAL FILE
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
    
    def prepare_multi_mode_confirmation_data(self):
        """NEW: Prepare confirmation data with detected modes"""
        # Get basic confirmation data
        confirmation_data = self.preparation.prepare_confirmation_data()
        
        # Detect multiple modes using enhanced parser
        if self.orchestrator.card_data:
            detected_modes = self.orchestrator.parser.parse_card_instructions_multi(
                self.orchestrator.card_data['desc']
            )
            
            # Add multi-mode data
            confirmation_data.detected_modes = detected_modes
            confirmation_data.selected_processing_modes = detected_modes
            
            print(f"🎯 Multi-mode confirmation data prepared with {len(detected_modes)} modes: {detected_modes}")
        
        return confirmation_data
    
    def ui_processing_callback(self, confirmation_data, progress_callback, use_transitions=True):
        """ENHANCED: Main processing callback - now supports multi-mode"""
        
        # Configure transitions
        from ..video_processor import configure_transitions
        configure_transitions(use_transitions)
        print(f"🎬 Processing with transitions: {'ENABLED' if use_transitions else 'DISABLED'}")
        
        try:
            self.orchestrator.start_time = time.time()
            
            # NEW: Check if multi-mode processing is needed
            selected_modes = getattr(confirmation_data, 'selected_processing_modes', [confirmation_data.processing_mode])
            
            if len(selected_modes) > 1:
                print(f"🎬 Multi-mode processing detected: {selected_modes}")
                return self._execute_multi_mode_processing(confirmation_data, selected_modes, progress_callback, use_transitions)
            else:
                print(f"🎬 Single-mode processing: {selected_modes[0]}")
                return self._execute_single_mode_processing(confirmation_data, progress_callback, use_transitions)
            
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
    
    def _execute_single_mode_processing(self, confirmation_data, progress_callback, use_transitions):
        """Execute single-mode processing - UNCHANGED from your original logic"""
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
    
    def _execute_multi_mode_processing(self, confirmation_data, selected_modes, progress_callback, use_transitions):
        """NEW: Execute multi-mode processing"""
        try:
            print(f"🔄 Starting multi-mode processing for {len(selected_modes)} modes...")
            
            # Step 1: Setup project once (download videos once)
            progress_callback(10, "📥 Setting up project and downloading videos...")
            
            final_project_name = self.progress.check_and_update_project_name(progress_callback)
            
            # Download videos once
            self.orchestrator.creds, self.orchestrator.downloaded_videos, base_project_paths = \
                self.orchestrator.processing_steps.download_and_setup(
                    self.orchestrator.card_data,
                    self.orchestrator.project_info
                )
            
            # Step 2: Process each mode
            all_processed_files = []
            completed_modes = []
            
            total_modes = len(selected_modes)
            base_progress = 30  # Start after download
            mode_progress_chunk = 60 / total_modes  # 60% for all modes
            
            for i, mode in enumerate(selected_modes, 1):
                current_progress = base_progress + (i-1) * mode_progress_chunk
                progress_callback(current_progress, f"🎬 Processing mode {i}/{total_modes}: {mode}")
                
                print(f"\n🎬 PROCESSING MODE {i}/{total_modes}: {mode.upper()}")
                
                # Create mode-specific project paths
                mode_project_paths = self._create_mode_specific_project_paths(base_project_paths, mode)
                
                # Update orchestrator with mode-specific data
                original_mode = self.orchestrator.processing_mode
                original_paths = self.orchestrator.project_paths
                
                self.orchestrator.processing_mode = mode
                self.orchestrator.project_paths = mode_project_paths
                
                # Set account and platform for video processor
                account_code = self.orchestrator.project_info.get('account_code') or \
                              self.orchestrator.project_info.get('detected_account_code')
                platform_code = self.orchestrator.project_info.get('platform_code') or \
                               self.orchestrator.project_info.get('detected_platform_code')
                
                if account_code and platform_code:
                    print(f"🎯 Setting processor context: Account={account_code}, Platform={platform_code}")
                    from ..video_processor import set_processor_account_platform
                    set_processor_account_platform(account_code, platform_code)
                
                # Process this mode
                mode_processed_files = self.orchestrator.processing_steps.process_videos(
                    self.orchestrator.downloaded_videos,
                    mode_project_paths,
                    self.orchestrator.project_info,
                    mode,
                    self.orchestrator.creds
                )
                
                if mode_processed_files:
                    # Add mode info to each file
                    for file_info in mode_processed_files:
                        file_info['processing_mode'] = mode
                    
                    all_processed_files.extend(mode_processed_files)
                    completed_modes.append(mode)
                    print(f"✅ Mode {mode} completed successfully")
                else:
                    print(f"❌ Mode {mode} failed - aborting multi-mode process")
                    # Restore original values
                    self.orchestrator.processing_mode = original_mode
                    self.orchestrator.project_paths = original_paths
                    return create_processing_result_from_orchestrator(
                        [], self.orchestrator.start_time, '', success=False
                    )
                
                # Restore original values for next iteration
                self.orchestrator.processing_mode = original_mode
                self.orchestrator.project_paths = original_paths
            
            # Step 3: Write to Google Sheets for all modes
            progress_callback(95, "📊 Updating Google Sheets for all modes...")
            
            sheets_success = self._write_multi_mode_sheets(all_processed_files, completed_modes)
            
            # Step 4: Generate breakdown reports and cleanup for each mode
            progress_callback(98, "📄 Generating reports and organizing files...")
            
            # Store all processed files in orchestrator
            self.orchestrator.processed_files = all_processed_files
            
            # Final progress
            progress_callback(100, f"✅ Multi-mode processing completed! {len(completed_modes)} folders created")
            
            # Create combined result
            result = create_processing_result_from_orchestrator(
                all_processed_files,
                self.orchestrator.start_time,
                base_project_paths.get('project_root', '.'),
                success=True
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Multi-mode processing failed: {e}")
            import traceback
            traceback.print_exc()
            return create_processing_result_from_orchestrator(
                [], self.orchestrator.start_time, '', success=False
            )
    
    def _create_mode_specific_project_paths(self, base_paths, mode):
        """Create mode-specific project paths with correct folder names"""
        import copy
        import os
        
        mode_paths = copy.deepcopy(base_paths)
        
        if 'project_root' in mode_paths:
            # Get base folder name and add mode suffix
            base_root = mode_paths['project_root']
            parent_dir = os.path.dirname(base_root)
            base_folder = os.path.basename(base_root)
            
            # Remove any existing mode suffix and add new one
            base_folder_clean = base_folder.replace(' VSL', '').replace(' Quiz', '').replace(' SVSL', '')
            mode_display = self.orchestrator.parser.get_processing_mode_display(mode)
            mode_folder = f"{base_folder_clean} {mode_display}"
            
            mode_project_root = os.path.join(parent_dir, mode_folder)
            mode_paths['project_root'] = mode_project_root
            
            # Update all other paths to use the new root
            for key in mode_paths:
                if key != 'project_root' and isinstance(mode_paths[key], str):
                    mode_paths[key] = mode_paths[key].replace(base_root, mode_project_root)
        
        return mode_paths
    
    def _write_multi_mode_sheets(self, all_processed_files, completed_modes):
        """Write results for all completed modes to Google Sheets"""
        try:
            from ..api_clients import write_to_google_sheets_with_custom_name
            
            # Group files by mode
            files_by_mode = {}
            for file_info in all_processed_files:
                mode = file_info.get('processing_mode', 'unknown')
                if mode not in files_by_mode:
                    files_by_mode[mode] = []
                files_by_mode[mode].append(file_info)
            
            # Write each mode as separate entries
            all_success = True
            for mode in completed_modes:
                if mode in files_by_mode:
                    mode_files = files_by_mode[mode]
                    
                    # Create mode-specific name for sheets
                    mode_display = self.orchestrator.parser.get_processing_mode_display(mode)
                    project_name = self.orchestrator.project_info.get('project_name', 'Unknown Project')
                    sheets_name = f"{project_name} {mode_display}"
                    
                    # Use original card title for routing
                    routing_name = self.orchestrator.card_data.get('name', project_name)
                    
                    success = write_to_google_sheets_with_custom_name(
                        routing_name,  # Routing name for worksheet selection
                        sheets_name,   # Display name in column 1
                        mode_files,
                        self.orchestrator.creds
                    )
                    
                    if success:
                        print(f"✅ Wrote {len(mode_files)} {mode} entries to sheets")
                    else:
                        print(f"❌ Failed to write {mode} results to sheets")
                        all_success = False
            
            return all_success
            
        except Exception as e:
            print(f"❌ Multi-mode sheets writing failed: {e}")
            return False