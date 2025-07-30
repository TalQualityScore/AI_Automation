import os
import re

# --- CONFIGURATION ---
BASE_OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'Desktop')

# --- FUNCTIONS ---

def parse_project_info(folder_name):
    """Parses the project information from a folder name."""
    print(f"Parsing folder name: {folder_name}")
    pattern = re.compile(r'OO_(.*?)_AD_([A-Z]+)-(\d+)')
    match = pattern.search(folder_name)
    if not match:
        pattern_fb = re.compile(r'GH OO_(.*?)_AD_([A-Z]+)-(\d+)')
        match = pattern_fb.search(folder_name)
    if not match:
        return None
    
    project_name = match.group(1).replace("_", " ").strip()
    project_name = re.sub(r'\s+Ad$', '', project_name, flags=re.IGNORECASE)

    return {
        "project_name": project_name,
        "ad_type": match.group(2), "test_name": match.group(3)
    }

def create_project_structure(project_folder_name):
    """Creates the standard project folder structure."""
    project_folder = os.path.join(BASE_OUTPUT_DIR, project_folder_name)
    
    subfolders = {
        "project_root": project_folder, "ame": os.path.join(project_folder, "_AME"),
        "audio": os.path.join(project_folder, "_Audio"), "copy": os.path.join(project_folder, "_Copy"),
        "footage": os.path.join(project_folder, "_Footage"), "thumbnails": os.path.join(project_folder, "_Thumbnails"),
        "footage_images": os.path.join(project_folder, "_Footage", "Images"),
        "footage_psd": os.path.join(project_folder, "_Footage", "PSD"),
        "footage_vector": os.path.join(project_folder, "_Footage", "Vector"),
        "footage_video": os.path.join(project_folder, "_Footage", "Video"),
        "client_footage": os.path.join(project_folder, "_Footage", "Video", "Client"),
    }
    
    for path in subfolders.values():
        os.makedirs(path, exist_ok=True)
    
    print(f"Project folder created at: {project_folder}")
    return subfolders