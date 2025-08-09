# app/src/automation/orchestrator/ui_integration_base.py
"""
UI Integration Base Module - Main orchestrator
This is the refactored version of ui_integration.py
Delegates to specialized modules for better organization
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
            
            # Step 1: Check and update project name
            final_project_name = self.progress.check_and_update_project_name(progress_callback)
            
            # Step 2: Download assets
            progress_callback(25, "📥 Downloading Assets from Google Drive...")
            print(f"🔍 PASSING UPDATED PROJECT_INFO TO SETUP: '{self.orchestrator.project_info['project_name']}'")
            
            self.orchestrator.creds, self.orchestrator.downloaded_videos, self.orchestrator.project_paths = \
                self.processing.setup_project_with_progress(
                    self.orchestrator.card_data, 
                    self.orchestrator.project_info, 
                    progress_callback
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
            
            print(f"🔍 PASSING UPDATED PROJECT_INFO TO PROCESSING: '{self.orchestrator.project_info['project_name']}'")
            self.orchestrator.processed_files = self.processing.process_videos_with_progress(
                self.orchestrator.downloaded_videos,
                self.orchestrator.project_paths,
                self.orchestrator.project_info,
                self.orchestrator.processing_mode,
                self.orchestrator.creds,
                progress_callback,
                use_transitions
            )
            
            # Step 4: Update Google Sheets
            sheets_routing_name = self.orchestrator.original_card_title
            sheets_column1_name = self.orchestrator.generated_folder_name
            
            self.sheets.update_google_sheets(
                self.orchestrator.processed_files,
                self.orchestrator.project_info,
                self.orchestrator.creds,
                self.orchestrator.project_paths,
                sheets_routing_name,
                sheets_column1_name,
                progress_callback
            )
            
            # Step 5: Generate report
            self.sheets.generate_breakdown_report(
                self.orchestrator.processed_files,
                self.orchestrator.project_paths,
                use_transitions,
                progress_callback
            )
            
            # Step 6: Complete
            progress_callback(100, "🎉 Processing complete!")
            
            return create_processing_result_from_orchestrator(
                processed_files=self.orchestrator.processed_files,
                start_time=self.orchestrator.start_time,
                output_folder=self.orchestrator.project_paths['project_root'],
                success=True
            )
            
        except Exception as e:
            return self._handle_processing_error(e)
    
    def _handle_processing_error(self, error):
        """Handle processing errors"""
        print(f"❌ PROCESSING ERROR: {error}")
        import traceback
        traceback.print_exc()
        
        from ..workflow_data_models import ProcessingResult
        return ProcessingResult(
            success=False,
            duration="",
            processed_files=[],
            output_folder="",
            error_message=str(error),
            error_solution=self.orchestrator.error_handler.generate_error_solution(str(error))
        )
    
    # Keep these delegation methods for backward compatibility
    def _setup_project_with_progress(self, card_data, project_info, progress_callback):
        """Delegate to processing module"""
        return self.processing.setup_project_with_progress(card_data, project_info, progress_callback)
    
    def _process_videos_with_progress(self, downloaded_videos, project_paths, project_info, 
                                     processing_mode, creds, progress_callback, use_transitions=True):
        """Delegate to processing module"""
        return self.processing.process_videos_with_progress(
            downloaded_videos, project_paths, project_info, 
            processing_mode, creds, progress_callback, use_transitions
        )
    
    def _finalize_with_correct_names(self, processed_files, project_info, creds, project_paths, 
                                   routing_name, column1_name):
        """Delegate to sheets module"""
        self.sheets.finalize_with_correct_names(
            processed_files, project_info, creds, project_paths, 
            routing_name, column1_name
        )