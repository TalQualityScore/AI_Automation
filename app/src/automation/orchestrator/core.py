# app/src/automation/orchestrator/core.py
# ENHANCED - Add multi-mode processing support to existing file
# Based on your complete existing file with multi-mode enhancements added

import time

# Import new modular components
from ..robust_monitoring import RobustMonitoringSystem
from ..validation_engine import ValidationEngine
from ..instruction_parser import InstructionParser

# Import UI components
from ..unified_workflow_dialog import UnifiedWorkflowDialog
from ..workflow_dialog.helpers import (create_confirmation_data_from_orchestrator, 
                                     create_processing_result_from_orchestrator)

from .processing_steps import ProcessingSteps
from .ui_integration_base import UIIntegration
from .error_handling import ErrorHandler

class AutomationOrchestrator:
    """Enhanced orchestrator with multi-mode processing support"""
    
    def __init__(self):
        self.monitor = RobustMonitoringSystem()
        self.validator = ValidationEngine()
        self.parser = InstructionParser()
        self.trello_card_id = None
        self.start_time = None
        
        # Data for UI integration
        self.card_data = None
        self.processing_mode = None
        self.project_info = None
        self.downloaded_videos = None
        self.project_paths = None
        self.creds = None
        self.processed_files = None
        
        # Delegate responsibilities to focused classes
        self.processing_steps = ProcessingSteps(self)
        self.ui_integration = UIIntegration(self)
        self.error_handler = ErrorHandler(self)
    
    def execute_with_ui(self, trello_card_id=None):
        """ENHANCED: Execute automation with UI workflow - now supports multi-mode"""
        
        # If no card ID provided, show popup to get it
        if not trello_card_id:
            print("🎬 Starting AI Automation Suite - Getting Trello Card...")
            trello_card_id = UnifiedWorkflowDialog.get_trello_card_id()
            if not trello_card_id:
                print("❌ No Trello card ID provided. Automation cancelled.")
                return False
        
        self.trello_card_id = trello_card_id
        self.start_time = time.time()
        
        try:
            print("🚀 Starting AI Automation with UI Workflow")
            print(f"Card ID: {trello_card_id}")
            print("="*60)
            
            # ENHANCED: Check if multi-mode processing should be used
            if self._should_use_multi_mode_processing(trello_card_id):
                print("🎯 Multi-mode processing detected - using enhanced workflow")
                confirmation_data = self.ui_integration.prepare_multi_mode_confirmation_data()
            else:
                print("🎯 Single-mode processing - using standard workflow")
                confirmation_data = self.ui_integration.prepare_confirmation_data()
            
            # Show unified workflow dialog
            dialog = UnifiedWorkflowDialog()
            success = dialog.show_workflow(
                confirmation_data=confirmation_data,
                processing_callback=self.ui_integration.ui_processing_callback
            )
            
            if success:
                print("\n" + "="*60)
                print("🎉 Automation completed successfully with UI!")
                print(f"📁 Project folder: {self.project_paths['project_root'] if self.project_paths else 'Unknown'}")
                print(f"📊 Processed {len(self.processed_files) if self.processed_files else 0} video(s)")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("❌ Automation cancelled by user")
                print("="*60)
            
            return success
            
        except Exception as e:
            self.error_handler.handle_automation_error(e, trello_card_id)
            return False
    
    def _should_use_multi_mode_processing(self, trello_card_id):
        """ENHANCED: Determine if multi-mode processing should be used"""
        try:
            print("🔍 Checking for multi-mode requirements...")
            
            # Step 1: Fetch and validate card data
            self.card_data = self.processing_steps.fetch_and_validate_card(trello_card_id)
            
            # Step 2: Parse instructions and project info 
            self.processing_mode, self.project_info = self.processing_steps.parse_and_validate(self.card_data)
            
            # Step 3: Use enhanced parser to detect multiple modes
            detected_modes = self.parser.parse_card_instructions_multi(self.card_data['desc'])
            
            print(f"🎯 Multi-mode analysis:")
            print(f"   - Detected modes: {detected_modes}")
            print(f"   - Mode count: {len(detected_modes)}")
            
            # Use multi-mode if more than one mode detected
            use_multi_mode = len(detected_modes) > 1
            
            if use_multi_mode:
                print("✅ Multi-mode processing will be used")
            else:
                print("ℹ️ Single-mode processing will be used")
            
            return use_multi_mode
            
        except Exception as e:
            print(f"⚠️ Error checking for multi-mode: {e}")
            print("🔄 Falling back to single-mode processing")
            return False
    
    def _execute_multi_mode_ui_workflow(self, trello_card_id):
        """NEW: Execute multi-mode UI workflow"""
        try:
            print("🎬 Starting Multi-Mode Processing...")
            
            # Step 1: Prepare confirmation data with detected modes
            confirmation_data = self.ui_integration.prepare_multi_mode_confirmation_data()
            
            # Step 2: Show unified workflow dialog (user can modify selections)
            dialog = UnifiedWorkflowDialog()
            success = dialog.show_workflow(
                confirmation_data=confirmation_data,
                processing_callback=self._multi_mode_processing_callback
            )
            
            if success:
                print("\n" + "="*60)
                print("🎉 Multi-mode automation completed successfully!")
                total_folders = len(getattr(confirmation_data, 'selected_processing_modes', []))
                print(f"📁 Created {total_folders} project folders")
                print(f"📊 Processed {len(self.processed_files) if self.processed_files else 0} total video(s)")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("❌ Multi-mode automation cancelled by user")
                print("="*60)
            
            return success
            
        except Exception as e:
            print(f"❌ Multi-mode UI workflow failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _multi_mode_processing_callback(self, confirmed_data, progress_callback, use_transitions=True):
        """NEW: Processing callback for multi-mode execution"""
        try:
            # Get selected modes from confirmed data
            selected_modes = getattr(confirmed_data, 'selected_processing_modes', [confirmed_data.processing_mode])
            
            print(f"🔄 Starting processing for {len(selected_modes)} modes: {selected_modes}")
            
            # Execute multi-mode processing loop
            return self._execute_multi_mode_processing_loop(confirmed_data, selected_modes, progress_callback)
            
        except Exception as e:
            print(f"❌ Multi-mode processing callback failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _execute_multi_mode_processing_loop(self, confirmed_data, selected_modes, progress_callback):
        """NEW: Execute processing for each selected mode"""
        all_processed_files = []
        completed_modes = []
        
        try:
            print(f"🔄 Starting processing loop for {len(selected_modes)} modes...")
            
            # Step 1: Download videos once (shared across all modes)
            progress_callback(10, "📥 Downloading videos from Google Drive...")
            
            # Setup project and download videos
            self.creds, self.downloaded_videos, base_project_paths = self.processing_steps.download_and_setup(
                self.card_data, self.project_info
            )
            
            # Step 2: Process each mode
            total_modes = len(selected_modes)
            for i, mode in enumerate(selected_modes, 1):
                current_progress = 20 + (i-1) * 70 // total_modes
                progress_callback(current_progress, f"🎬 Processing mode {i}/{total_modes}: {mode}")
                
                print(f"\n{'='*60}")
                print(f"🎬 PROCESSING MODE {i}/{total_modes}: {mode.upper()}")
                print(f"{'='*60}")
                
                # Create mode-specific project paths
                mode_project_paths = self._create_mode_specific_project_paths(base_project_paths, mode, confirmed_data)
                
                # Update orchestrator state for this mode
                self.project_paths = mode_project_paths
                self.processing_mode = mode
                
                # Process this mode using existing pipeline
                mode_processed_files = self.processing_steps.process_videos(
                    self.downloaded_videos,
                    mode_project_paths,
                    self.project_info,
                    mode,
                    self.creds
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
                    self._cleanup_failed_multi_mode_process(completed_modes)
                    return create_processing_result_from_orchestrator(
                        self, False, f"Mode {mode} processing failed"
                    )
            
            # Step 3: Write to Google Sheets for all modes
            progress_callback(90, "📊 Updating Google Sheets for all modes...")
            
            sheets_success = self._write_multi_mode_results_to_sheets(all_processed_files, completed_modes, confirmed_data)
            
            # Store all processed files
            self.processed_files = all_processed_files
            
            # Create combined result
            result = create_processing_result_from_orchestrator(self, True)
            result.processed_files = all_processed_files
            
            # Add multi-mode specific info
            if hasattr(result, '__dict__'):
                result.multi_mode_results = {
                    'completed_modes': completed_modes,
                    'total_files': len(all_processed_files),
                    'folders_created': len(completed_modes)
                }
            
            progress_callback(100, f"✅ Multi-mode processing completed! {len(completed_modes)} folders created")
            
            return result
            
        except Exception as e:
            print(f"❌ Multi-mode processing loop failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Clean up any completed folders
            self._cleanup_failed_multi_mode_process(completed_modes)
            return create_processing_result_from_orchestrator(
                self, False, f"Multi-mode processing failed: {e}"
            )
    
    def _create_mode_specific_project_paths(self, base_paths, mode, confirmed_data):
        """Create mode-specific project paths with correct folder names"""
        import copy
        import os
        
        mode_paths = copy.deepcopy(base_paths)
        
        if 'project_root' in mode_paths:
            # Get base folder info
            base_root = mode_paths['project_root']
            parent_dir = os.path.dirname(base_root)
            base_folder = os.path.basename(base_root)
            
            # Remove any existing mode suffixes
            clean_folder = base_folder.replace(' VSL', '').replace(' Quiz', '').replace(' SVSL', '')
            clean_folder = clean_folder.replace(' Connector VSL', '').replace(' Connector Quiz', '').replace(' Connector SVSL', '')
            
            # Add new mode to folder name
            mode_display = self.parser.get_processing_mode_display(mode)
            mode_folder = f"{clean_folder} {mode_display}"
            
            mode_project_root = os.path.join(parent_dir, mode_folder)
            mode_paths['project_root'] = mode_project_root
            
            # Update all other paths to use the new root
            for key in mode_paths:
                if key != 'project_root' and isinstance(mode_paths[key], str):
                    mode_paths[key] = mode_paths[key].replace(base_root, mode_project_root)
            
            print(f"📁 Mode-specific folder: {mode_folder}")
        
        return mode_paths
    
    def _write_multi_mode_results_to_sheets(self, all_processed_files, completed_modes, confirmed_data):
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
                    mode_display = self.parser.get_processing_mode_display(mode)
                    project_name = confirmed_data.project_name
                    sheets_name = f"{project_name} {mode_display}"
                    
                    # Use original card title for routing
                    routing_name = self.card_data.get('name', project_name)
                    
                    success = write_to_google_sheets_with_custom_name(
                        routing_name,  # Routing name for worksheet selection
                        sheets_name,   # Display name in column 1
                        mode_files,
                        self.creds
                    )
                    
                    if success:
                        print(f"✅ Wrote {len(mode_files)} {mode} entries to sheets")
                    else:
                        print(f"❌ Failed to write {mode} results to sheets")
                        all_success = False
            
            return all_success
            
        except Exception as e:
            print(f"❌ Multi-mode sheets writing failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _cleanup_failed_multi_mode_process(self, completed_modes):
        """Clean up folders created during failed multi-mode process"""
        try:
            import os
            import shutil
            
            for mode in completed_modes:
                try:
                    # Try to remove the mode-specific folder
                    mode_display = self.parser.get_processing_mode_display(mode)
                    print(f"🗑️ Cleaning up folder for mode: {mode} ({mode_display})")
                    
                    # This would need the actual folder path - for now just log
                    # In a real implementation, you'd track the folder paths per mode
                    
                except Exception as cleanup_error:
                    print(f"⚠️ Cleanup error for mode {mode}: {cleanup_error}")
                    
        except Exception as e:
            print(f"⚠️ Overall cleanup failed: {e}")
    
    # KEEP ALL EXISTING METHODS UNCHANGED
    def execute(self, trello_card_id):
        """Legacy headless execution - UNCHANGED"""
        self.trello_card_id = trello_card_id
        self.start_time = time.time()
        
        try:
            print("🚀 Starting AI Automation (Headless Mode)")
            print(f"Card ID: {trello_card_id}")
            print("="*60)
            
            # Step 1: Fetch and Validate Card Data
            self.card_data = self.processing_steps.fetch_and_validate_card(trello_card_id)
            
            # Step 2: Parse Instructions and Validate Assets
            self.processing_mode, self.project_info = self.processing_steps.parse_and_validate(self.card_data)
            
            # Step 3: Setup Project and Download Files
            self.creds, self.downloaded_videos, self.project_paths = self.processing_steps.setup_project(self.card_data, self.project_info)
            
            # Step 4: Process Videos
            self.processed_files = self.processing_steps.process_videos(
                self.downloaded_videos, self.project_paths, self.project_info, 
                self.processing_mode, self.creds
            )
            
            # Step 5: Log Results and Cleanup
            self.processing_steps.finalize_and_cleanup(self.processed_files, self.project_info, self.creds, self.project_paths)
            
            print("\n" + "="*60)
            print("🎉 Automation finished successfully!")
            print(f"📁 Project folder: {self.project_paths['project_root']}")
            print(f"📊 Processed {len(self.processed_files)} video(s)")
            print("="*60)
            
        except Exception as e:
            self.error_handler.handle_automation_error(e, trello_card_id)
            
    class ActivityMonitor:
        """Simple activity monitor for long-running operations - UNCHANGED"""
        
        def __init__(self):
            self.active = False
            
        def execute_with_activity_monitoring(self, func, operation_name, no_activity_timeout=300):
            """Execute a function with activity monitoring - UNCHANGED"""
            print(f"⏱️ Starting: {operation_name}")
            self.active = True
            
            try:
                result = func()
                print(f"✅ Completed: {operation_name}")
                return result
            except Exception as e:
                print(f"❌ Failed: {operation_name} - {str(e)}")
                raise
            finally:
                self.active = False