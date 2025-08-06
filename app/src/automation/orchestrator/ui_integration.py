# app/src/automation/orchestrator/ui_integration.py - FIXED PROJECT NAME FLOW

def prepare_confirmation_data(self):
    """Prepare data for the confirmation dialog - FIXED to preserve card title"""
    # Fetch basic card data for validation
    self.orchestrator.card_data = self.orchestrator.processing_steps.fetch_and_validate_card(self.orchestrator.trello_card_id)
    
    # IMPORTANT: Store the original card title for Google Sheets
    self.orchestrator.original_card_title = self.orchestrator.card_data['name']
    print(f"🔍 UI INTEGRATION - Stored original card title: '{self.orchestrator.original_card_title}'")
    
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

def ui_processing_callback(self, progress_callback):
    """Processing callback that provides UI updates - FIXED TO USE UPDATED PROJECT NAME"""
    try:
        # Step 1: Already done in preparation
        progress_callback(15, "🔍 Fetching Data from Trello...")
        time.sleep(0.5)
        
        # FIXED: Get the updated project name from confirmation data
        if hasattr(self.orchestrator, 'updated_project_name') and self.orchestrator.updated_project_name:
            # User edited the project name in confirmation tab
            final_project_name = self.orchestrator.updated_project_name
            print(f"🔄 Using UPDATED project name: '{final_project_name}'")
            
            # Update project_info with new name
            self.orchestrator.project_info['project_name'] = final_project_name
        else:
            # Use original parsed project name
            final_project_name = self.orchestrator.project_info['project_name']
            print(f"📝 Using ORIGINAL project name: '{final_project_name}'")
        
        # Step 2: Downloading Assets from Google Drive
        progress_callback(25, "📥 Downloading Assets from Google Drive...")
        self.orchestrator.creds, self.orchestrator.downloaded_videos, self.orchestrator.project_paths = self._setup_project_with_progress(
            self.orchestrator.card_data, self.orchestrator.project_info, progress_callback
        )
        
        # Step 3: Processing Videos 
        progress_callback(60, "🎬 Processing videos...")
        self.orchestrator.processed_files = self._process_videos_with_progress(
            self.orchestrator.downloaded_videos, self.orchestrator.project_paths, self.orchestrator.project_info,
            self.orchestrator.processing_mode, self.orchestrator.creds, progress_callback
        )
        
        # Step 4: FIXED - Use ORIGINAL card title for Google Sheets, not generated folder name
        progress_callback(90, "📊 Updating Google Sheets...")
        
        # CRITICAL FIX: Use original card title for sheets routing, not generated concept name
        sheets_concept_name = self.orchestrator.original_card_title
        print(f"📊 FIXED - Using ORIGINAL card title for sheets: '{sheets_concept_name}'")
        
        # Call finalize with corrected concept name
        self._finalize_with_original_card_title(
            self.orchestrator.processed_files, self.orchestrator.project_info, 
            self.orchestrator.creds, self.orchestrator.project_paths, sheets_concept_name
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

def _finalize_with_original_card_title(self, processed_files, project_info, creds, project_paths, original_card_title):
    """Finalize using original card title for proper Google Sheets routing"""
    
    print(f"\n--- Step 5: Logging to Google Sheets with ORIGINAL title ---")
    print(f"🔍 Original Card Title: '{original_card_title}'")
    
    if processed_files:
        # Use ORIGINAL card title for sheets routing - this fixes the BC3 FB issue
        concept_name = original_card_title  # NOT the generated folder name
        
        data_to_write = [
            [pf['version'], pf['description'], pf['output_name']]
            for pf in processed_files
        ]
        
        def write_results():
            from ..api_clients import write_to_google_sheets
            error, _ = write_to_google_sheets(concept_name, data_to_write, creds)
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