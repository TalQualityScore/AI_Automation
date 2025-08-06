# --- File: app/src/naming_generator.py - CORRECTED VERSION ---
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

def generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter=""):
    """CORRECTED: Generates the final stitched video filename with proper version letter extraction."""
    base_name = os.path.splitext(os.path.basename(first_client_video))[0].replace("Copy of OO_", "")
    
    print(f"🔍 NAMING DEBUG - Input filename: '{base_name}'")
    
    ad_type_match = re.search(r'(VTD|STOR|ACT)', base_name)
    ad_type = ad_type_match.group(1) if ad_type_match else ""
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', base_name)
    test_name = test_name_match.group(1) if test_name_match else ""
    
    # CORRECTED: Extract version letter from the original filename
    if not version_letter:
        # Look for pattern like "STOR-3133_250416C" or "STOR-3133_250416B"
        # Pattern: numbers followed by letter at the end (before any file extension)
        version_letter_match = re.search(r'_\d+([A-Z])(?:_\d+)?$', base_name)
        if version_letter_match:
            version_letter = version_letter_match.group(1)
            print(f"✅ VERSION LETTER EXTRACTED: '{version_letter}' from '{base_name}'")
        else:
            print(f"⚠️ NO VERSION LETTER FOUND in '{base_name}'")
            version_letter = ""

    part1 = "GH"
    part2 = unidecode(project_name).lower().replace(" ", "")
    part3 = ad_type
    part4 = f"{test_name}{version_letter}"  # Include version letter here
    part5 = ad_type_selection
    part6 = image_desc.lower().replace(" ", "").replace("_", "")
    part7 = f"v{version_num:02d}"
    part8, part9, part10 = "m01", "f00", "c00"
    
    name_part = f"{part1}-{part2}{part3}{part4}ZZ{part5}"
    version_part = f"{part7}-{part8}-{part9}-{part10}"
    
    final_name = f"{name_part}_{part6}-{version_part}"
    
    print(f"🎯 FINAL OUTPUT NAME: '{final_name}'")
    print(f"   📋 Breakdown:")
    print(f"   - Project: {part2}")
    print(f"   - Ad Type: {part3}")
    print(f"   - Test + Letter: {part4}")
    print(f"   - Version Letter: '{version_letter}'")
    
    return final_name

def get_image_description(video_path, temp_dir=None):
    """
    Returns a simple placeholder 'X' instead of calling any API.
    This eliminates API quota issues and dependency on external services.
    """
    print("Using placeholder 'x' for image description.")
    return "x"

# Deprecated function - keeping for compatibility but it does nothing
def load_api_key():
    """Returns None - API key no longer needed."""
    return None