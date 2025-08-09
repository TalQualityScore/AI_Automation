# app/src/automation/workflow_utils_modules/project_structure.py
"""
Project folder structure creation
Separated from the original workflow_utils.py
"""

import os
from typing import Dict

def create_project_structure(project_folder_name: str) -> Dict[str, str]:
    """
    Creates the project folder structure with _AME, _Audio, _Copy, _Footage, _Thumbnails.
    
    Args:
        project_folder_name: Name for the project folder
        
    Returns:
        Dictionary with paths to all created folders
    """
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    project_path = os.path.join(desktop_path, project_folder_name)
    
    try:
        # Create main project folder
        os.makedirs(project_path, exist_ok=True)
        
        # Define folder structure
        subfolders = {
            "audio": "_Audio", 
            "copy": "_Copy", 
            "footage": "_Footage", 
            "thumbs": "_Thumbnails", 
            "ame": "_AME"
        }
        
        # Create main subfolders
        for key, folder in subfolders.items():
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        # Audio subfolders
        audio_sub = ["Music", "SFX", "Source", "VO"]
        for sub in audio_sub:
            os.makedirs(os.path.join(project_path, subfolders["audio"], sub), exist_ok=True)
        
        # Footage subfolders  
        footage_sub = ["Images", "PSD", "Vector", "Video"]
        for sub in footage_sub:
            os.makedirs(os.path.join(project_path, subfolders["footage"], sub), exist_ok=True)
        
        # Video subfolders
        video_sub = ["Client", "Quality Score", "Rendered", "Stock"]
        for sub in video_sub:
            os.makedirs(os.path.join(project_path, subfolders["footage"], "Video", sub), exist_ok=True)
        
        print(f"📁 PROJECT STRUCTURE CREATED AT: '{project_path}'")
        
        # Return paths dictionary
        return {
            "project_root": project_path,
            "audio": os.path.join(project_path, subfolders["audio"]),
            "copy": os.path.join(project_path, subfolders["copy"]),
            "footage": os.path.join(project_path, subfolders["footage"]),
            "thumbnails": os.path.join(project_path, subfolders["thumbs"]),
            "ame": os.path.join(project_path, subfolders["ame"]),
            "client_videos": os.path.join(project_path, subfolders["footage"], "Video", "Client"),
            "rendered_videos": os.path.join(project_path, subfolders["footage"], "Video", "Rendered")
        }
        
    except Exception as e:
        print(f"❌ Error creating project structure: {e}")
        raise