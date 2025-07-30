import os
import shutil
import sys

# Import the modularized functions
from app.src.automation.api_clients import (get_trello_card_data, 
                                            download_files_from_gdrive, 
                                            write_to_google_sheets, 
                                            get_google_creds)
from app.src.automation.video_processor import (get_video_dimensions, 
                                                process_video_sequence)
from app.src.automation.workflow_utils import (parse_project_info, 
                                               create_project_structure)
from app.src.automation.error_handler import error_handler
from app.src.automation.timing_report import (generate_timing_report, 
                                               prepare_video_sequence_info)
from app.src import naming_generator

# --- CONFIGURATION ---
# All config is now handled by the individual modules via .env

def parse_card_instructions(card_description):
    """Parse the card description using a standardized approach."""
    desc_lower = card_description.lower()
    
    print(f"Parsing card description: {card_description[:100]}...")
    
    # PRIORITY 1: Check for "save as is" or "save as" first (most important)
    if "save as is" in desc_lower or "save as" in desc_lower:
        print("Detected 'save as is' instruction - will only rename and save files (but still add 'quiz' to name)")
        return "save_only"
    
    # PRIORITY 2: Look for EXPLICIT "no connector" or "only quiz" instructions
    no_connector_patterns = [
        "no need.*connector",
        "only.*quiz",
        "connect only to quiz",
        "quiz.*no.*connector",
        "without.*connector",
        "skip.*connector",
        "bypass.*connector"
    ]
    
    import re
    for pattern in no_connector_patterns:
        if re.search(pattern, desc_lower):
            print(f"Detected 'quiz only' pattern: '{pattern}' - will add quiz only")
            return "quiz_only"
    
    # PRIORITY 3: Look for combination patterns (connector + quiz)
    quiz_connector_patterns = [
        "quiz outro.*connector",
        "connector.*quiz outro", 
        "quiz.*blake connector",
        "blake connector.*quiz",
        "combine.*quiz.*connector",
        "combine.*connector.*quiz",
        "with.*connector.*quiz",
        "connector.*and.*quiz"
    ]
    
    for pattern in quiz_connector_patterns:
        if re.search(pattern, desc_lower):
            print(f"Detected quiz + connector pattern: '{pattern}' - will add connector + quiz")
            return "connector_quiz"
    
    # PRIORITY 4: Look for general processing instructions
    processing_verbs = ["combine", "connect", "add", "merge", "stitch", "join", "attach"]
    quiz_keywords = ["quiz", "outro"]
    
    has_processing_verb = any(verb in desc_lower for verb in processing_verbs)
    has_quiz_keyword = any(keyword in desc_lower for keyword in quiz_keywords)
    
    if has_processing_verb and has_quiz_keyword:
        # Default to quiz only unless connector is explicitly mentioned
        if "connector" in desc_lower or "blake" in desc_lower:
            print("Detected processing verb + quiz + connector - will add connector + quiz")
            return "connector_quiz"
        else:
            print("Detected processing verb + quiz (no connector mentioned) - will add quiz only")
            return "quiz_only"
    
    # PRIORITY 5: Default fallback
    print("No specific processing instructions found - defaulting to save only")
    return "save_only"

def get_processing_suffix(processing_mode):
    """Get the suffix to add to the naming based on processing mode."""
    # FIXED: Always add 'quiz' since the concept is always a quiz
    return "quiz"  # Always add quiz regardless of processing mode

def main(trello_card_id):
    """Main function to orchestrate the entire automation workflow."""
    
    try:
        # --- Step 1: Get Data & Parse ---
        print("--- Step 1: Fetching Trello & Parsing Project Info ---")
        card_data, error = get_trello_card_data(trello_card_id)
        if error: 
            error_handler.handle_error(error, "Failed to fetch Trello card data")
            return
        
        # Parse processing instructions from card description
        processing_mode = parse_card_instructions(card_data.get('desc', ''))
        print(f"Processing mode detected: {processing_mode}")
        
        project_info = parse_project_info(card_data['name'])
        if not project_info: 
            error_handler.handle_error("Could not parse project info", "Project name parsing failed")
            return
        
        print(f"Successfully parsed project: {project_info['project_name']}")
        print(f"Version letter: {project_info.get('version_letter', 'Not found')}")

        # --- Step 2: Download & Setup ---
        print("\n--- Step 2: Downloading & Setting Up Project ---")
        creds = get_google_creds()
        if not creds: 
            error_handler.handle_error("Google credentials not available", "Credentials loading failed")
            return
        
        downloaded_videos, error = download_files_from_gdrive(card_data['gdrive_url'], creds)
        if error: 
            error_handler.handle_error(error, "Failed to download videos from Google Drive")
            return
        
        # Determine naming suffix based on processing mode
        naming_suffix = get_processing_suffix(processing_mode)
        
        project_folder_name = naming_generator.generate_project_folder_name(
            project_name=project_info['project_name'],
            first_client_video=downloaded_videos[0],
            ad_type_selection=naming_suffix.title()
        )
        project_paths = create_project_structure(project_folder_name)
        
        client_video_final_paths = []
        for video_path in downloaded_videos:
            final_path = os.path.join(project_paths['client_footage'], os.path.basename(video_path))
            shutil.move(video_path, final_path)
            client_video_final_paths.append(final_path)

        # Only get video dimensions if we're processing videos
        if processing_mode != "save_only":
            target_width, target_height, error = get_video_dimensions(client_video_final_paths[0])
            if error: 
                error_handler.handle_error(error, "Failed to get video dimensions")
                return
            print(f"Target resolution set to {target_width}x{target_height}")

        # --- Step 3: Get Starting Version from Google Sheets ---
        print("\n--- Step 3: Checking Google Sheets for Existing Project ---")
        concept_name = f"GH {project_info['project_name']} {project_info['ad_type']} {project_info['test_name']}"
        if naming_suffix:
            concept_name += f" {naming_suffix.title()}"
        
        error, start_version = write_to_google_sheets(concept_name, [], creds) # Dry run
        if error: 
            error_handler.handle_error(error, "Failed to check Google Sheets")
            return

        # --- Step 4: Process Videos Based on Mode ---
        print(f"\n--- Step 4: Processing Videos (Starting from v{start_version:02d}) ---")
        processed_files = []

        for i, client_video in enumerate(client_video_final_paths):
            version_num = start_version + i
            print(f"\n--- Processing Version {version_num:02d} ({processing_mode}) ---")
            
            image_desc = naming_generator.get_image_description(client_video)
            
            # Generate output name with version letter if available
            output_name = naming_generator.generate_output_name(
                project_name=project_info['project_name'], 
                first_client_video=client_video,
                ad_type_selection=naming_suffix, 
                image_desc=image_desc, 
                version_num=version_num,
                version_letter=project_info.get('version_letter', '')
            )
            output_path = os.path.join(project_paths['ame'], f"{output_name}.mp4")
            
            if processing_mode == "save_only":
                # Just copy with new name
                shutil.copy(client_video, output_path)
                print(f"Successfully saved: {output_name}.mp4")
                
                processed_files.append({
                    "version": f"v{version_num:02d}",
                    "source_file": os.path.basename(client_video),
                    "output_name": output_name,
                    "description": f"Saved as is from {os.path.basename(client_video)}"
                })
            else:
                # Process videos with connectors/quiz
                error = process_video_sequence(client_video, output_path, target_width, target_height, processing_mode)
                if error:
                    error_handler.handle_error(error, f"Failed to process video {os.path.basename(client_video)}")
                    return
                
                print(f"Successfully processed: {output_name}.mp4")
                
                # Create description based on processing mode
                if processing_mode == "connector_quiz":
                    description = f"New Ad from {os.path.basename(client_video)} + connector + quiz"
                elif processing_mode == "quiz_only":
                    description = f"New Ad from {os.path.basename(client_video)} + quiz"
                else:
                    description = f"New Ad from {os.path.basename(client_video)}"
                
                processed_files.append({
                    "version": f"v{version_num:02d}",
                    "source_file": os.path.basename(client_video),
                    "output_name": output_name,
                    "description": description
                })
                
                # Generate timing report for processed videos
                video_sequence_info = prepare_video_sequence_info(client_video, processing_mode)
                timing_report_path = generate_timing_report(video_sequence_info, project_paths['project_root'], processing_mode)
                if timing_report_path:
                    print(f"Generated timing report: {timing_report_path}")

        # Add empty row for organization in sheets
        if processed_files:
            processed_files.append({
                "version": "",
                "description": "",
                "output_name": ""
            })

        # --- Step 5: Log to Google Sheets ---
        print("\n--- Step 5: Logging to Google Sheets ---")
        if processed_files:
            data_to_write = [
                [pf['version'], pf['description'], pf['output_name']]
                for pf in processed_files
            ]
            
            error, _ = write_to_google_sheets(concept_name, data_to_write, creds)
            if error: 
                error_handler.handle_error(error, "Failed to write to Google Sheets")
                return
            print("Successfully logged results to Google Sheets.")
        else:
            print("No files were processed, skipping log.")

        # --- Step 6: Cleanup ---
        print("\n--- Step 6: Cleaning up temporary files ---")
        temp_dir = "temp_downloads"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print("Automation finished successfully!")

    except Exception as e:
        error_handler.handle_error(e, "Unexpected error in main automation")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python local_automation.py <TRELLO_CARD_ID>")
    else:
        main(sys.argv[1])