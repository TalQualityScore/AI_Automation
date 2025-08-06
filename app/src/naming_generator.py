# app/src/naming_generator.py - SHORT IMPORT WRAPPER
"""
Naming Generator - Simple Import Wrapper

Maintains backward compatibility by importing from the modular naming system.
"""

import sys
import os

# Add current directory to Python path to help with imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # Try multiple import paths for the modular naming system
    try:
        from naming import (
            generate_output_name,
            generate_project_folder_name,
            get_image_description,
            parse_project_info,
            clean_project_name
        )
    except ImportError:
        # Fallback to relative import
        from .naming import (
            generate_output_name,
            generate_project_folder_name,
            get_image_description,
            parse_project_info,
            clean_project_name
        )
    print("✅ Using modular naming system")
    
except ImportError as e:
    print(f"❌ Modular naming system failed: {e}")
    print("🔧 Using minimal fallback functions")
    
    # Minimal fallback functions to prevent crashes
    def generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter=""):
        return f"fallback_output_{version_num}"
    
    def generate_project_folder_name(project_name, first_client_video, ad_type_selection):
        return f"fallback_folder_{project_name}"
    
    def get_image_description(video_path):
        return "fallback_description"
    
    def parse_project_info(folder_name):
        return {"project_name": "Fallback Project", "ad_type": "STOR", "test_name": "0000", "version_letter": "A"}
    
    def clean_project_name(raw_name):
        return raw_name or "Fallback Project"

# Export functions for backward compatibility
__all__ = [
    'generate_output_name',
    'generate_project_folder_name',
    'get_image_description',
    'parse_project_info',
    'clean_project_name'
]