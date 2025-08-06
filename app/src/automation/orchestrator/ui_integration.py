# app/src/automation/orchestrator/ui_integration.py - FIXED PROJECT NAME FLOW ISSUE

import time
import os

from ..workflow_dialog.helpers import (
    create_confirmation_data_from_orchestrator,
    create_processing_result_from_orchestrator
)

class UIIntegration:
    """Handles UI-specific methods and callbacks for the orchestrator"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def prepare_confirmation_data(self):
        """Prepare data for the confirmation dialog - FIXED to preserve card title"""
        # Fetch basic card data for validation
        self.orchestrator.card_data = self.orchestrator.processing_steps.fetch_and_validate_card(self.orchestrator.trello_card_id)
        
        # IMPORTANT: Store the original card title for Google Sheets ROUTING ONLY
        self.orchestrator.original_card_title = self.orchestrator.card_data['name']
        print(f"🔍 UI INTEGRATION - Stored original card title for routing: '{self.orchestrator.original_card_title}'")
        
        # Parse project info
        self.orchestrator.project_info = self._parse_project_info_for_ui(self.orchestrator.card_data)
        
        # Determine processing mode
        self.orchestrator.processing_mode = self.orchestrator.parser.parse_card_instructions(self.orchestrator.card_data.get('desc', ''))
        
        # Validate assets
        asset_issues = self.orchestrator.validator.validate_assets(self.orchestrator.processing_mode)
        
        # Mock downloaded videos for UI (we'll download them during processing)
        mock_videos = ["video1.mp4", "video2.mp4", "video3.mp4"]  # Placeholder
        
        # Create confirmation data
        return create_confirmation_data_from_orchestrator(
            card_data=self.orchestrator.card_data,
            processing_mode=self.orchestrator.processing_mode,
            project_info=self.orchestrator.project_info,
            downloaded_videos=mock_videos,
            validation_issues=asset_issues
        )
    
    def _parse_project_info_for_ui(self, card_data):
        """Parse project info for UI display"""
        from ..workflow_utils import parse_project_info
        
        project_info = parse_project_info(card_data['name'])
        if not project_info:
            # Fallback: create basic project info from card name
            project_info = {
                'project_name': card_data['name'],
                'ad_type': 'Unknown',
                'test_name': '0000',
                'version_letter': ''
            }
        return project_info
    
    def ui_processing_callback(self, progress_callback):
        """Processing callback - COMPLETELY FIXED PROJECT NAME FLOW"""
        try:
            # Step 1: Already done in preparation
            progress_callback(15, "🔍 Fetching Data from Trello...")
            time.sleep(0.5)
            
            # CRITICAL DEBUG: Show what we're checking for
            print(f"🔍 CHECKING FOR UPDATED NAME:")
            print(f"   - hasattr(orchestrator, 'updated_project_name'): {hasattr(self.orchestrator, 'updated_project_name')}")
            if hasattr(self.orchestrator, 'updated_project_name'):
                print(f"   - orchestrator.updated_project_name: '{self.orchestrator.updated_project_name}'")
            print(f"   - Current project_info name: '{self.orchestrator.project_info['project_name']}'")
            
            # COMPLETELY FIXED: Check for updated project name from confirmation tab
            final_project_name = None
            
            if (hasattr(self.orchestrator, 'updated_project_name') and 
                self.orchestrator.updated_project_name and 
                self.orchestrator.updated_project_name.strip() != ''):
                
                # User edited the project name in confirmation tab
                final_project_name = self.orchestrator.updated_project_name.strip()
                print(f"🔄 USING UPDATED PROJECT NAME: '{final_project_name}'")
                
                # CRITICAL: Update project_info IMMEDIATELY
                self.orchestrator.project_info['project_name'] = final_project_name
                print(f"✅ PROJECT_INFO UPDATED TO: '{self.orchestrator.project_info['project_name']}'")
                
            else:
                # Use original parsed project name
                final_project_name = self.orchestrator.project_info['project_name']
                print(f"📝 USING ORIGINAL PROJECT NAME: '{final_project_name}'")
            
            print(f"🎯 FINAL PROJECT NAME FOR ALL PROCESSING: '{final_project_name}'")
            print(f"🎯 PROJECT_INFO NOW CONTAINS: '{self.orchestrator.project_info['project_name']}'")
            
            # Step 2: Downloading Assets from Google Drive
            progress_callback(25, "📥 Downloading Assets from Google Drive...")
            
            # CRITICAL: Pass the UPDATED project_info (with new name) to setup_project
            print(f"🔍 PASSING PROJECT_INFO TO SETUP: '{self.orchestrator.project_info['project_name']}'")
            self.orchestrator.creds, self.orchestrator.downloaded_videos, self.orchestrator.project_paths = self._setup_project_with_progress(
                self.orchestrator.card_data, self.orchestrator.project_info, progress_callback  # Uses updated project_info
            )
            
            # CRITICAL: Store the generated folder name for sheets column 1
            self.orchestrator.generated_folder_name = os.path.basename(self.orchestrator.project_paths['project_root'])
            print(f"📁 GENERATED FOLDER NAME: '{self.orchestrator.generated_folder_name}'")
            
            # Step 3: Processing Videos 
            progress_callback(60, "🎬 Processing videos...")
            
            # CRITICAL: Pass the UPDATED project_info (with new name) to process_videos  
            print(f"🔍 PASSING PROJECT_INFO TO PROCESSING: '{self.orchestrator.project_info['project_name']}'")
            self.orchestrator.processed_files = self._process_videos_with_progress(
                self.orchestrator.downloaded_videos, self.orchestrator.project_paths, self.orchestrator.project_info,  # Uses updated project_info
                self.orchestrator.processing_mode, self.orchestrator.creds, progress_callback
            )
            
            # Step 4: FIXED - Use folder name for column 1, original card title for routing
            progress_callback(90, "📊 Updating Google Sheets...")
            
            # Use original card title for ROUTING to correct worksheet
            sheets_routing_name = self.orchestrator.original_card_title
            # Use generated folder name for COLUMN 1 content
            sheets_column1_name = self.orchestrator.generated_folder_name
            
            print(f"📊 Sheets routing (find worksheet): '{sheets_routing_name}'")
            print(f"📊 Sheets column 1 (display name): '{sheets_column1_name}'")
            
            # Call finalize with both names
            self._finalize_with_correct_names(
                self.orchestrator.processed_files, self.orchestrator.project_info, 
                self.orchestrator.creds, self.orchestrator.project_paths, 
                sheets_routing_name, sheets_column1_name
            )
            
            # Step 5: Finalizing
            progress_callback(100, "🎉 Processing complete!")
            
            return create_processing_result_from_orchestrator(
                processed_files=self.orchestrator.processed_files,
                start_time=self.orchestrator.start_time,
                output_folder=self.orchestrator.project_paths['project_root'],
                success=True
            )
            
        except Exception as e:
            from ..workflow_data_models import ProcessingResult
            return ProcessingResult(
                success=False,
                duration="",
                processed_files=[],
                output_folder="",
                error_message=str(e),
                error_solution=self.orchestrator.error_handler.generate_error_solution(str(e))
            )
    
    def _setup_project_with_progress(self, card_data, project_info, progress_callback):
        """Setup project with progress updates"""
        progress_callback(30, "🔑 Setting up credentials...")
        print(f"🔍 SETUP_PROJECT RECEIVED PROJECT_INFO: '{project_info['project_name']}'")
        creds, downloaded_videos, project_paths = self.orchestrator.processing_steps.setup_project(
            card_data, project_info
        )
        progress_callback(50, "📁 Project structure created...")
        return creds, downloaded_videos, project_paths
    
    def _process_videos_with_progress(self, downloaded_videos, project_paths, project_info, processing_mode, creds, progress_callback):
        """Process videos with progress updates"""
        progress_callback(70, "🎬 Starting video processing...")
        print(f"🔍 PROCESS_VIDEOS RECEIVED PROJECT_INFO: '{project_info['project_name']}'")
        processed_files = self.orchestrator.processing_steps.process_videos(
            downloaded_videos, project_paths, project_info, processing_mode, creds
        )
        progress_callback(85, "✅ Video processing complete...")
        return processed_files
    
    def _finalize_with_correct_names(self, processed_files, project_info, creds, project_paths, 
                                   routing_name, column1_name):
        """FIXED: Use routing name for worksheet selection, folder name for column 1"""
        
        print(f"\n--- Step 5: Logging to Google Sheets ---")
        print(f"🔍 Routing name (worksheet): '{routing_name}'")
        print(f"📁 Column 1 name (folder): '{column1_name}'")
        
        if processed_files:
            data_to_write = [
                [pf['version'], pf['description'], pf['output_name']]
                for pf in processed_files
            ]
            
            def write_results():
                from ..api_clients import write_to_google_sheets_with_custom_name
                # Use routing name to find worksheet, column1 name for actual content
                error, _ = write_to_google_sheets_with_custom_name(
                    routing_name, column1_name, data_to_write, creds
                )
                if error:
                    raise Exception(f"Failed to write to Google Sheets: {error}")
                return "Results logged successfully"
            
            result = self.orchestrator.monitor.execute_with_activity_monitoring(
                write_results,
                "Google Sheets Logging",
                no_activity_timeout=120
            )
            print(result)
        else:
            print("No files were processed, skipping log.")