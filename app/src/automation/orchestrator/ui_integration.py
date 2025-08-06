# app/src/automation/orchestrator/ui_integration.py - COMPLETE FIXED VERSION

import time
import os

from ..workflow_dialog.helpers import (
    create_confirmation_data_from_orchestrator,
    create_processing_result_from_orchestrator
)

class UIIntegration:
    """Handles UI-specific methods and callbacks for the orchestrator - COMPLETE VERSION"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def prepare_confirmation_data(self):
        """Prepare data for the confirmation dialog - FIXED to preserve card title"""
        # Fetch basic card data for validation
        self.orchestrator.card_data = self.orchestrator.processing_steps.fetch_and_validate_card(self.orchestrator.trello_card_id)
        
        # IMPORTANT: Store the original card title for Google Sheets ROUTING ONLY
        self.orchestrator.original_card_title = self.orchestrator.card_data['name']
        print(f"🔍 UI INTEGRATION - Stored original card title for routing: '{self.orchestrator.original_card_title}'")
        
        # CRITICAL: Use FIXED account detection with fallback dialog
        try:
            from ..api_clients import AccountMapper
            mapper = AccountMapper()
            
            # Clear any cached data first
            mapper._clear_cache()
            
            # Try to detect account/platform - this will show dialog if detection fails
            print(f"🔍 ATTEMPTING ACCOUNT/PLATFORM DETECTION from: '{self.orchestrator.original_card_title}'")
            
            account_code, platform_code = mapper.extract_account_and_platform(
                self.orchestrator.original_card_title, 
                allow_fallback=True  # Show dialog if detection fails
            )
            
            print(f"✅ Account/Platform detected: Account='{account_code}', Platform='{platform_code}'")
            
            # Store for later use in Google Sheets routing
            self.orchestrator.detected_account_code = account_code
            self.orchestrator.detected_platform_code = platform_code
            
        except Exception as detection_error:
            print(f"❌ CRITICAL: Account/Platform detection failed: {detection_error}")
            # Don't continue - this is a critical error that would cause processing to fail
            raise Exception(f"Cannot proceed without account/platform identification: {detection_error}")
        
        # Parse project info from card title
        self.orchestrator.project_info = self._parse_project_info_for_ui(self.orchestrator.card_data)
        
        # Determine processing mode from card description
        self.orchestrator.processing_mode = self.orchestrator.parser.parse_card_instructions(self.orchestrator.card_data.get('desc', ''))
        
        # Validate assets based on processing mode
        asset_issues = self.orchestrator.validator.validate_assets(self.orchestrator.processing_mode)
        
        # Mock downloaded videos for UI (we'll download them during processing)
        mock_videos = ["video1.mp4", "video2.mp4", "video3.mp4"]  # Placeholder
        
        # Create confirmation data using the helper function
        confirmation_data = create_confirmation_data_from_orchestrator(
            card_data=self.orchestrator.card_data,
            processing_mode=self.orchestrator.processing_mode,
            project_info=self.orchestrator.project_info,
            downloaded_videos=mock_videos,
            validation_issues=asset_issues
        )
        
        # Store confirmation data for later access
        self.orchestrator.confirmation_data = confirmation_data
        
        return confirmation_data
    
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
        
        print(f"🔍 PARSED PROJECT INFO: {project_info}")
        return project_info
    
    def ui_processing_callback(self, progress_callback):
        """Processing callback - COMPLETELY FIXED PROJECT NAME FLOW"""
        try:
            # Step 1: Already done in preparation
            progress_callback(15, "🔍 Fetching Data from Trello...")
            time.sleep(0.5)
            
            # COMPLETELY FIXED: Check for updated project name from confirmation tab
            print(f"\n🔍 CHECKING FOR UPDATED PROJECT NAME:")
            
            # Initialize tracking
            final_project_name = None
            sources_checked = []
            name_changed = False
            
            # Source 1: Direct orchestrator attribute (set by confirmation tab)
            if (hasattr(self.orchestrator, 'updated_project_name') and 
                self.orchestrator.updated_project_name and 
                self.orchestrator.updated_project_name.strip() != ''):
                
                final_project_name = self.orchestrator.updated_project_name.strip()
                sources_checked.append(f"✅ orchestrator.updated_project_name: '{final_project_name}'")
                name_changed = True
            else:
                sources_checked.append("❌ orchestrator.updated_project_name: Not set or empty")
            
            # Source 2: Check dialog controller if it exists
            if (not final_project_name and 
                hasattr(self.orchestrator, 'dialog_controller') and 
                self.orchestrator.dialog_controller):
                
                if (hasattr(self.orchestrator.dialog_controller, 'updated_project_name') and 
                    self.orchestrator.dialog_controller.updated_project_name and
                    self.orchestrator.dialog_controller.updated_project_name.strip() != ''):
                    
                    final_project_name = self.orchestrator.dialog_controller.updated_project_name.strip()
                    sources_checked.append(f"✅ dialog_controller.updated_project_name: '{final_project_name}'")
                    name_changed = True
                else:
                    sources_checked.append("❌ dialog_controller.updated_project_name: Not set or empty")
            else:
                sources_checked.append("❌ dialog_controller: Not available")
            
            # Source 3: Check confirmation data directly (might be updated by UI)
            if (not final_project_name and 
                hasattr(self.orchestrator, 'confirmation_data') and 
                self.orchestrator.confirmation_data):
                
                if (hasattr(self.orchestrator.confirmation_data, 'project_name') and
                    self.orchestrator.confirmation_data.project_name.strip() != ''):
                    
                    # Check if it's different from original
                    original_name = self.orchestrator.project_info.get('project_name', '')
                    ui_name = self.orchestrator.confirmation_data.project_name.strip()
                    
                    if ui_name != original_name:
                        final_project_name = ui_name
                        sources_checked.append(f"✅ confirmation_data.project_name: '{final_project_name}' (changed from '{original_name}')")
                        name_changed = True
                    else:
                        sources_checked.append(f"ℹ️ confirmation_data.project_name: '{ui_name}' (same as original)")
                else:
                    sources_checked.append("❌ confirmation_data.project_name: Not available")
            else:
                sources_checked.append("❌ confirmation_data: Not available")
            
            # Source 4: Fallback to original parsed name
            if not final_project_name:
                final_project_name = self.orchestrator.project_info['project_name']
                sources_checked.append(f"🔄 original project_info.project_name: '{final_project_name}' (fallback)")
            
            # Debug output
            print(f"🔍 PROJECT NAME SOURCES CHECKED:")
            for source in sources_checked:
                print(f"   {source}")
            
            print(f"🎯 FINAL PROJECT NAME DETERMINED: '{final_project_name}'")
            if name_changed:
                print(f"🔄 PROJECT NAME WAS CHANGED BY USER")
            else:
                print(f"ℹ️ PROJECT NAME UNCHANGED FROM ORIGINAL")
            
            # CRITICAL: Update project_info IMMEDIATELY before any processing step
            original_name = self.orchestrator.project_info['project_name']
            if final_project_name != original_name:
                print(f"\n🔄 UPDATING PROJECT_INFO:")
                print(f"   FROM: '{original_name}'")
                print(f"   TO:   '{final_project_name}'")
                
                self.orchestrator.project_info['project_name'] = final_project_name
                print(f"✅ PROJECT_INFO UPDATED SUCCESSFULLY")
                
                # Verify the update
                if self.orchestrator.project_info['project_name'] == final_project_name:
                    print(f"✅ VERIFICATION: project_info now contains '{self.orchestrator.project_info['project_name']}'")
                else:
                    print(f"❌ ERROR: project_info update failed!")
            else:
                print(f"ℹ️ NO PROJECT NAME CHANGE NEEDED")
            
            # Step 2: Downloading Assets from Google Drive
            progress_callback(25, "📥 Downloading Assets from Google Drive...")
            
            # CRITICAL: Pass the UPDATED project_info (with new name) to setup_project
            print(f"🔍 PASSING UPDATED PROJECT_INFO TO SETUP: '{self.orchestrator.project_info['project_name']}'")
            self.orchestrator.creds, self.orchestrator.downloaded_videos, self.orchestrator.project_paths = self._setup_project_with_progress(
                self.orchestrator.card_data, self.orchestrator.project_info, progress_callback  # Uses updated project_info
            )
            
            # CRITICAL: Store the generated folder name for sheets column 1
            self.orchestrator.generated_folder_name = os.path.basename(self.orchestrator.project_paths['project_root'])
            print(f"📁 GENERATED FOLDER NAME (will be used in sheets column 1): '{self.orchestrator.generated_folder_name}'")
            
            # Step 3: Processing Videos 
            progress_callback(60, "🎬 Processing videos...")
            
            # CRITICAL: Pass the UPDATED project_info (with new name) to process_videos  
            print(f"🔍 PASSING UPDATED PROJECT_INFO TO PROCESSING: '{self.orchestrator.project_info['project_name']}'")
            self.orchestrator.processed_files = self._process_videos_with_progress(
                self.orchestrator.downloaded_videos, self.orchestrator.project_paths, self.orchestrator.project_info,  # Uses updated project_info
                self.orchestrator.processing_mode, self.orchestrator.creds, progress_callback
            )
            
            # Step 4: FIXED - Use folder name for column 1, original card title for routing
            progress_callback(90, "📊 Updating Google Sheets...")
            
            # Use original card title for ROUTING to correct worksheet
            sheets_routing_name = self.orchestrator.original_card_title
            # Use generated folder name for COLUMN 1 content (reflects updated project name)
            sheets_column1_name = self.orchestrator.generated_folder_name
            
            print(f"\n📊 GOOGLE SHEETS UPDATE STRATEGY:")
            print(f"   🔍 Routing name (find worksheet): '{sheets_routing_name}'")
            print(f"   📁 Column 1 name (display in sheet): '{sheets_column1_name}'")
            print(f"   📊 Detected Account: '{self.orchestrator.detected_account_code}'")
            print(f"   📊 Detected Platform: '{self.orchestrator.detected_platform_code}'")
            
            # Call finalize with both names - this uses the FIXED account detection
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
            print(f"❌ PROCESSING ERROR: {e}")
            import traceback
            traceback.print_exc()
            
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
        
        # This will create folders using the updated project name
        creds, downloaded_videos, project_paths = self.orchestrator.processing_steps.setup_project(
            card_data, project_info
        )
        
        progress_callback(50, "📁 Project structure created...")
        print(f"📁 PROJECT STRUCTURE CREATED AT: '{project_paths['project_root']}'")
        
        return creds, downloaded_videos, project_paths
    
    def _process_videos_with_progress(self, downloaded_videos, project_paths, project_info, processing_mode, creds, progress_callback):
        """Process videos with progress updates"""
        progress_callback(70, "🎬 Starting video processing...")
        print(f"🔍 PROCESS_VIDEOS RECEIVED PROJECT_INFO: '{project_info['project_name']}'")
        
        # This will use the updated project name in output filenames
        processed_files = self.orchestrator.processing_steps.process_videos(
            downloaded_videos, project_paths, project_info, processing_mode, creds
        )
        
        progress_callback(85, "✅ Video processing complete...")
        print(f"✅ PROCESSED {len(processed_files)} FILES")
        
        return processed_files
    
    def _finalize_with_correct_names(self, processed_files, project_info, creds, project_paths, 
                                   routing_name, column1_name):
        """FIXED: Use routing name for worksheet selection, folder name for column 1"""
        
        print(f"\n--- Step 5: Logging to Google Sheets ---")
        print(f"🔍 Routing name (worksheet lookup): '{routing_name}'")
        print(f"📁 Column 1 name (folder display): '{column1_name}'")
        
        if processed_files:
            data_to_write = [
                [pf['version'], pf['description'], pf['output_name']]
                for pf in processed_files
            ]
            
            def write_results():
                # CRITICAL: Use the FIXED account detection for precise worksheet routing
                if (hasattr(self.orchestrator, 'detected_account_code') and 
                    hasattr(self.orchestrator, 'detected_platform_code') and
                    self.orchestrator.detected_account_code != 'UNKNOWN' and
                    self.orchestrator.detected_platform_code != 'UNKNOWN'):
                    
                    print(f"✅ Using DETECTED account/platform for routing:")
                    print(f"   Account: '{self.orchestrator.detected_account_code}'")
                    print(f"   Platform: '{self.orchestrator.detected_platform_code}'")
                    
                    try:
                        from ..api_clients import GoogleSheetsClient, AccountMapper
                        
                        # Use the detected account/platform for precise routing
                        sheets_client = GoogleSheetsClient(creds)
                        mapper = AccountMapper()
                        
                        # Find the exact worksheet using detected codes
                        worksheet_titles = sheets_client.get_worksheet_names()
                        print(f"📋 Available worksheets: {worksheet_titles}")
                        
                        target_worksheet = mapper.find_exact_worksheet_match(
                            worksheet_titles, 
                            self.orchestrator.detected_account_code, 
                            self.orchestrator.detected_platform_code
                        )
                        
                        if target_worksheet:
                            print(f"✅ EXACT WORKSHEET MATCH: '{target_worksheet}'")
                            # Write directly to the correct worksheet using detected routing
                            error, _ = sheets_client.write_to_sheet_with_custom_name(
                                target_worksheet,  # Use exact worksheet name
                                column1_name,     # Use folder name for column 1 display
                                data_to_write, 
                                creds
                            )
                        else:
                            print(f"❌ NO EXACT WORKSHEET FOUND - This should not happen with fixed detection!")
                            raise Exception(f"No worksheet found for {self.orchestrator.detected_account_code} - {self.orchestrator.detected_platform_code}")
                            
                    except Exception as worksheet_error:
                        print(f"❌ WORKSHEET ROUTING ERROR: {worksheet_error}")
                        raise Exception(f"Google Sheets routing failed: {worksheet_error}")
                        
                else:
                    print(f"⚠️ NO DETECTED ACCOUNT/PLATFORM CODES - This should not happen!")
                    print(f"   detected_account_code: {getattr(self.orchestrator, 'detected_account_code', 'NOT SET')}")
                    print(f"   detected_platform_code: {getattr(self.orchestrator, 'detected_platform_code', 'NOT SET')}")
                    
                    # Emergency fallback
                    print(f"🆘 USING EMERGENCY FALLBACK ROUTING")
                    from ..api_clients import write_to_google_sheets_with_custom_name
                    error, _ = write_to_google_sheets_with_custom_name(
                        routing_name, column1_name, data_to_write, creds
                    )
                
                if error:
                    print(f"❌ GOOGLE SHEETS WRITE ERROR: {error}")
                    raise Exception(f"Failed to write to Google Sheets: {error}")
                
                print(f"✅ GOOGLE SHEETS WRITE SUCCESSFUL")
                return "Results logged successfully"
            
            # Execute with monitoring
            result = self.orchestrator.monitor.execute_with_activity_monitoring(
                write_results,
                "Google Sheets Logging",
                no_activity_timeout=120
            )
            print(result)
        else:
            print("No files were processed, skipping log.")
        
        # Cleanup temporary files
        print("\n--- Step 6: Cleaning up temporary files ---")
        temp_dir = "temp_downloads"
        
        # Check if temp directory exists before trying to remove it
        if os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                print(f"✅ Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                print(f"⚠️ Warning: Could not remove temp directory {temp_dir}: {e}")
        else:
            print(f"✅ No temporary files to clean up (temp directory {temp_dir} does not exist)")
        
        print("✅ Finalization completed successfully")