# app/src/automation/orchestrator/processing/sheets_writer.py - COMPLETE FIXED VERSION
"""
Sheets Writer Module - FIXED to properly use original card title for routing
All issues with UNKNOWN worksheet resolved
"""

from ...api_clients import write_to_google_sheets

class SheetsWriter:
    """Handles writing results to Google Sheets"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def write_to_sheets(self, project_info, processed_files, creds, current_mode=None):
        """Write results to Google Sheets with proper routing"""
        
        print("\n--- Step 5: Writing to Google Sheets ---")
        
        # Determine endpoint type from current processing mode (for multi-mode support)
        type_suffix = "Quiz"  # Default
        
        if current_mode:
            # Use current mode to determine type suffix (for multi-mode processing)
            print(f"🔧 Using current_mode to determine type: {current_mode}")
            if current_mode == 'quiz_only' or current_mode == 'connector_quiz':
                type_suffix = "Quiz"
            elif current_mode == 'vsl_only' or current_mode == 'connector_vsl':
                type_suffix = "VSL"
            elif current_mode == 'svsl_only' or current_mode == 'connector_svsl':
                type_suffix = "SVSL"
            elif current_mode == 'save_only':
                type_suffix = ""  # No suffix for save_only
        else:
            # Fallback to old logic if no current mode provided
            if processed_files and len(processed_files) > 0:
                first_file = processed_files[0]
                if 'svsl_path' in first_file or first_file.get('endpoint_type') == 'svsl':
                    type_suffix = "SVSL"
                elif 'vsl_path' in first_file or first_file.get('endpoint_type') == 'vsl':
                    type_suffix = "VSL"
        
        print(f"📊 Using type suffix for Google Sheets: {type_suffix}")
        
        # Build display name for column A
        base_name = f"GH {project_info['project_name']} {project_info.get('ad_type', '')} {project_info.get('test_name', '')}"
        # Only add type_suffix if it's not empty (save_only has empty suffix)
        if type_suffix.strip():
            display_name = f"{base_name} {type_suffix}"
        else:
            display_name = base_name.strip()  # Remove extra spaces
        
        # ========== FIX #1: PROPERLY GET ORIGINAL CARD TITLE ==========
        # Try multiple attributes to find the original card title
        routing_name = None
        
        # First try original_card_title (set in ui_preparation.py)
        if hasattr(self.orchestrator, 'original_card_title'):
            routing_name = self.orchestrator.original_card_title
            print(f"📋 Using original_card_title for routing: '{routing_name}'")
        # Then try card_name
        elif hasattr(self.orchestrator, 'card_name'):
            routing_name = self.orchestrator.card_name
            print(f"📋 Using card_name for routing: '{routing_name}'")
        # Try card_data directly
        elif hasattr(self.orchestrator, 'card_data') and self.orchestrator.card_data:
            routing_name = self.orchestrator.card_data.get('name')
            if routing_name:
                print(f"📋 Using card_data['name'] for routing: '{routing_name}'")
        
        # Final fallback
        if not routing_name:
            print(f"⚠️ WARNING: Could not find original card title, using display name for routing")
            print(f"   Available orchestrator attributes: {[attr for attr in dir(self.orchestrator) if not attr.startswith('_')]}")
            routing_name = display_name
        
        # ========== END FIX #1 ==========
        
        # Prepare data rows
        data_rows = self._prepare_data_rows(processed_files, type_suffix)
        
        # Write to sheets with proper routing
        def write_sheets():
            try:
                # Try to use the custom name function that allows separate routing/display names
                from ...api_clients import write_to_google_sheets_with_custom_name
                error, _ = write_to_google_sheets_with_custom_name(
                    routing_name,  # Original card title (has OO FB - prefix)
                    display_name,  # Generated name for column A
                    data_rows,
                    creds
                )
            except ImportError:
                # Fallback to regular function
                error, _ = write_to_google_sheets(display_name, data_rows, creds)
            
            if error:
                raise Exception(f"Failed to write to Google Sheets: {error}")
            return "Success"
        
        result = self.orchestrator.monitor.execute_with_activity_monitoring(
            write_sheets,
            "Google Sheets Update",
            no_activity_timeout=120
        )
        
        print(f"✅ Successfully wrote {len(data_rows)} rows to Google Sheets")
        return result
    
    def _prepare_data_rows(self, processed_files, type_suffix):
        """Prepare data rows for Google Sheets"""
        data_rows = []
        
        if not processed_files:
            return data_rows
        
        # Sort by version number
        sorted_files = sorted(processed_files, key=lambda x: x.get('version', 0))
        
        print(f"📝 Preparing {len(sorted_files)} rows for Google Sheets")
        
        for pf in sorted_files:
            version_num = pf.get('version', 0)
            version_text = f"v{version_num:02d}"
            
            # Format description
            description = pf.get('description', '')
            endpoint_type = pf.get('endpoint_type', type_suffix.lower())
            
            if description:
                if not description.startswith("Copy of OO_"):
                    if description.startswith("OO_"):
                        description = f"Copy of {description}"
                    else:
                        description = f"Copy of OO_{description}"
                description_text = f"New Ad from {description} + {endpoint_type}"
            else:
                source_file = pf.get('source_file', '')
                description_text = f"New Ad from Copy of OO_{source_file} + {endpoint_type}"
            
            # Output filename
            output_filename = f"{pf.get('output_name', '')}.mp4"
            
            # Create row
            row = [version_text, description_text, output_filename]
            data_rows.append(row)
        
        return data_rows