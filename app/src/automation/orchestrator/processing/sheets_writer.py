# app/src/automation/orchestrator/processing/sheets_writer.py
"""
Sheets Writer Module - Handles Google Sheets updates
"""

from ...api_clients import write_to_google_sheets

class SheetsWriter:
    """Handles writing results to Google Sheets"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def write_to_sheets(self, project_info, processed_files, creds):
        """Write results to Google Sheets with proper formatting
        
        Expected Google Sheets format (multiple rows):
        Column A: Project/Folder name (handled by sheets client)
        Column B: Version (v01, v02, v03)
        Column C: Description ("New Ad from Copy of OO_...")
        Column D: Output filename
        
        Args:
            project_info: Project information dictionary
            processed_files: List of processed file dictionaries
            creds: Google credentials
        """
        print("\n--- Step 5: Writing to Google Sheets ---")
        
        # Determine the type suffix based on what was processed
        type_suffix = "Quiz"  # Default
        if processed_files and len(processed_files) > 0:
            first_file = processed_files[0]
            if 'svsl_path' in first_file or first_file.get('endpoint_type') == 'svsl':
                type_suffix = "SVSL"
            elif 'vsl_path' in first_file or first_file.get('endpoint_type') == 'vsl':
                type_suffix = "VSL"
        
        # Build concept name for display in column A
        concept_name = f"GH {project_info['project_name']} {project_info['ad_type']} {project_info['test_name']} {type_suffix}"
        
        # For worksheet routing, use original card title if available
        routing_name = None
        if hasattr(self.orchestrator, 'original_card_title'):
            routing_name = self.orchestrator.original_card_title
            print(f"📋 Using original card title for routing: '{routing_name}'")
        else:
            routing_name = concept_name
            print(f"⚠️ Original card title not found, using concept name for routing")
        
        # Prepare data with MULTIPLE ROWS (one per version)
        # Each row: [version, description, filename]
        # Column A (folder name) is handled by the sheets client
        
        if processed_files:
            # Sort files by version number to ensure correct order
            sorted_files = sorted(processed_files, key=lambda x: x['version'])
            
            # Create multiple rows, one for each version
            data_rows = []
            
            print(f"📝 Preparing data for Google Sheets:")
            print(f"   Project: {concept_name}")
            print(f"   Files to write:")
            
            for pf in sorted_files:
                version_num = pf['version']
                
                # Column B: Version
                version_text = f"v{version_num:02d}"
                
                # Column C: Description
                description = pf.get('description', '')
                endpoint_type = pf.get('endpoint_type', type_suffix.lower())
                
                # Format the description properly
                if description:
                    # Ensure proper formatting
                    if not description.startswith("Copy of OO_"):
                        if description.startswith("OO_"):
                            description = f"Copy of {description}"
                        else:
                            description = f"Copy of OO_{description}"
                    
                    # Add the "New Ad from" prefix and endpoint suffix
                    if endpoint_type:
                        description_text = f"New Ad from {description} + {endpoint_type}"
                    else:
                        description_text = f"New Ad from {description}"
                else:
                    # Fallback if no description
                    source_file = pf.get('source_file', pf.get('original_filename', ''))
                    description_text = f"New Ad from Copy of OO_{source_file} + {endpoint_type}"
                
                # Column D: Output filename (with .mp4 extension)
                output_filename = f"{pf.get('output_name', '')}.mp4"
                
                # Create row with 3 columns (B, C, D)
                # Column A will be added by the sheets client
                row = [version_text, description_text, output_filename]
                data_rows.append(row)
                
                # Print what we're writing
                print(f"   Row {len(data_rows)}:")
                print(f"      Version: {version_text}")
                print(f"      Description: {description_text[:60]}..." if len(description_text) > 60 else f"      Description: {description_text}")
                print(f"      Filename: {output_filename}")
            
            print(f"\n📊 Summary: {len(data_rows)} rows × 3 columns")
            print(f"   Column A: {concept_name} (will be added by sheets client)")
            print(f"   Column B: Version numbers (v01, v02, v03...)")
            print(f"   Column C: Descriptions")
            print(f"   Column D: Output filenames")
            
        else:
            data_rows = []
            print("⚠️ No files to write to sheets")
        
        def write_sheets():
            # Try to use custom name function if available
            try:
                from ...api_clients import write_to_google_sheets_with_custom_name
                error, _ = write_to_google_sheets_with_custom_name(
                    routing_name,  # For finding worksheet (has account/platform)
                    concept_name,  # For column A display
                    data_rows,     # Multiple rows with [version, description, filename]
                    creds
                )
            except ImportError:
                # Fallback to regular write function
                error, _ = write_to_google_sheets(concept_name, data_rows, creds)
            
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