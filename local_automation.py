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
from app.src import naming_generator

# --- CONFIGURATION ---
# All config is now handled by the individual modules via .env

def main(trello_card_id):
    """Main function to orchestrate the entire automation workflow."""
    
    # --- Step 1: Get Data & Parse ---
    print("--- Step 1: Fetching Trello & Parsing Project Info ---")
    card_data, error = get_trello_card_data(trello_card_id)
    if error: return print(f"ERROR: {error}")
    
    project_info = parse_project_info(card_data['name'])
    if not project_info: return print("ERROR: Could not parse project info.")
    
    print(f"Successfully parsed project: {project_info['project_name']}")

    # --- Step 2: Download & Setup ---
    print("\n--- Step 2: Downloading & Setting Up Project ---")
    creds = get_google_creds()
    if not creds: return
    
    downloaded_videos, error = download_files_from_gdrive(card_data['gdrive_url'], creds)
    if error: return print(f"ERROR: {error}")
    
    project_folder_name = naming_generator.generate_project_folder_name(
        project_name=project_info['project_name'],
        first_client_video=downloaded_videos[0],
        ad_type_selection="Quiz"
    )
    project_paths = create_project_structure(project_folder_name)
    
    client_video_final_paths = []
    for video_path in downloaded_videos:
        final_path = os.path.join(project_paths['client_footage'], os.path.basename(video_path))
        shutil.move(video_path, final_path)
        client_video_final_paths.append(final_path)

    target_width, target_height, error = get_video_dimensions(client_video_final_paths[0])
    if error: return print(f"ERROR: {error}")
    print(f"Target resolution set to {target_width}x{target_height}")

    # --- Step 3: Get Starting Version from Google Sheets ---
    print("\n--- Step 3: Checking Google Sheets for Existing Project ---")
    concept_name = f"GH {project_info['project_name']} {project_info['ad_type']} {project_info['test_name']} Quiz"
    error, start_version = write_to_google_sheets(concept_name, [], creds) # Dry run
    if error: return print(f"ERROR during sheet check: {error}")

    # --- Step 4: Process Videos (Sequentially for Stability) ---
    print(f"\n--- Step 4: Processing Videos (Starting from v{start_version}) ---")
    processed_files = []

    for i, client_video in enumerate(client_video_final_paths):
        version_num = start_version + i
        print(f"\n--- Processing Version {version_num} ---")
        
        # Get placeholder image description (no API call)
        image_desc = naming_generator.get_image_description(client_video)
        
        # Generate name and process video
        output_name = naming_generator.generate_output_name(
            project_name=project_info['project_name'], first_client_video=client_video,
            ad_type_selection="Quiz", image_desc=image_desc, version_num=version_num
        )
        output_path = os.path.join(project_paths['ame'], f"{output_name}.mp4")
        
        error = process_video_sequence(client_video, output_path, target_width, target_height)
        if error:
            print(f"ERROR processing {os.path.basename(client_video)}: {error}")
        else:
            print(f"Successfully processed: {output_name}.mp4")
            processed_files.append({
                "version": f"v{version_num:02d}",
                "source_file": os.path.basename(client_video),
                "output_name": output_name
            })

    # --- Step 5: Log to Google Sheets ---
    print("\n--- Step 5: Logging to Google Sheets ---")
    if processed_files:
        data_to_write = [
            [pf['version'], f"New Ad from {pf['source_file']} + blake connector + quiz", pf['output_name']]
            for pf in processed_files
        ]
        data_to_write.append(['', '', '']) # Add empty row
        
        error, _ = write_to_google_sheets(concept_name, data_to_write, creds)
        if error: print(f"ERROR: {error}")
        else: print("Successfully logged results to Google Sheets.")
    else:
        print("No files were processed, skipping log.")

    # --- Step 6: Cleanup ---
    print("\n--- Step 6: Cleaning up temporary files ---")
    temp_dir = "temp_downloads"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    print("Cleanup complete. Automation finished successfully!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python local_automation.py <TRELLO_CARD_ID>")
    else:
        main(sys.argv[1])