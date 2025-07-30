# --- File: app/src/naming_generator.py ---
import re
import os
import subprocess
import sys
from unidecode import unidecode

def parse_filename_for_folder(filename):
    """Parses only the parts needed for the main project folder name."""
    base_name = os.path.splitext(filename)[0].replace("Copy of OO_", "")
    ad_type_match = re.search(r'(VTD|STOR|ACT)', base_name)
    ad_type = ad_type_match.group(1) if ad_type_match else ""
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', base_name)
    test_name = test_name_match.group(1) if test_name_match else ""
    return {"ad_type": ad_type, "test_name": test_name}

def generate_project_folder_name(project_name, first_client_video, ad_type_selection):
    """Generates the main output folder name."""
    parts = parse_filename_for_folder(os.path.basename(first_client_video))
    ad_type_cased = ad_type_selection.upper() if ad_type_selection.lower() != 'quiz' else 'Quiz'
    return f"GH {project_name} {parts['ad_type']} {parts['test_name']} {ad_type_cased}"

def generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num):
    """Generates the final stitched video filename."""
    base_name = os.path.splitext(os.path.basename(first_client_video))[0].replace("Copy of OO_", "")
    
    ad_type_match = re.search(r'(VTD|STOR|ACT)', base_name)
    ad_type = ad_type_match.group(1) if ad_type_match else ""
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', base_name)
    test_name = test_name_match.group(1) if test_name_match else ""
    version_letter_match = re.search(r'\d+([A-Z])$', base_name)
    version_letter = version_letter_match.group(1) if version_letter_match else ""

    part1 = "GH"
    part2 = unidecode(project_name).lower().replace(" ", "")
    part3 = ad_type
    part4 = f"{test_name}{version_letter}"
    part5 = ad_type_selection
    part6 = image_desc.lower().replace(" ", "").replace("_", "")
    part7 = f"v{version_num:02d}"
    part8, part9, part10 = "m00", "f00", "c00"
    
    name_part = f"{part1}-{part2}{part3}{part4}ZZ{part5}"
    version_part = f"{part7}-{part8}-{part9}-{part10}"
    
    return f"{name_part}_{part6}-{version_part}"

def get_image_description(video_path, temp_dir=None):
    """
    Returns a simple placeholder 'X' instead of calling any API.
    This eliminates API quota issues and dependency on external services.
    """
    print("Using placeholder 'X' for image description.")
    return "X"

# Deprecated function - keeping for compatibility but it does nothing
def load_api_key():
    """Returns None - API key no longer needed."""
    return None