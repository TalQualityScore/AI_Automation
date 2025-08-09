# app/src/automation/workflow_utils_modules/project_parser.py
"""
Main project info parser - orchestrates different parsing strategies
This is the main entry point that was the 205-line monster function
"""

import re
from typing import Optional, Dict
from .folder_parser import (
    extract_folder_name_from_drive_link,
    parse_standard_format,
    parse_alternative_format,
    parse_legacy_format
)
from .validation import validate_project_info

def parse_project_info(gdrive_folder_link: str) -> Optional[Dict[str, str]]:
    """
    Parse project information from Google Drive folder link or name.
    Main orchestrator function that tries different parsing strategies.
    
    Args:
        gdrive_folder_link: Google Drive folder URL or folder name
        
    Returns:
        Dictionary with project_name, ad_type, test_name, version_letter
        or None if parsing fails
    """
    print(f"🔍 PARSING PROJECT INFO from: {gdrive_folder_link}")
    
    # Step 1: Extract folder name from link
    folder_name = extract_folder_name_from_drive_link(gdrive_folder_link)
    if not folder_name:
        print("❌ Could not extract folder name")
        return None
    
    print(f"📁 Extracted folder name: '{folder_name}'")
    
    # Step 2: Try standard format first (most common)
    result = parse_standard_format(folder_name)
    if result:
        print(f"✅ Parsed using STANDARD format")
        return validate_project_info(result, folder_name)
    
    # Step 3: Try alternative formats
    result = parse_alternative_format(folder_name)
    if result:
        print(f"✅ Parsed using ALTERNATIVE format")
        return validate_project_info(result, folder_name)
    
    # Step 4: Try legacy format
    result = parse_legacy_format(folder_name)
    if result:
        print(f"✅ Parsed using LEGACY format")
        return validate_project_info(result, folder_name)
    
    # Step 5: Create fallback if all parsing fails
    print(f"⚠️ All parsing strategies failed, creating fallback")
    fallback = create_fallback_info(folder_name)
    return validate_project_info(fallback, folder_name)

def create_fallback_info(folder_name: str) -> Dict[str, str]:
    """
    Create fallback project info when all parsing strategies fail.
    
    Args:
        folder_name: The folder name that couldn't be parsed
        
    Returns:
        Dictionary with default/extracted values
    """
    # Try to extract any useful information
    project_name = folder_name
    
    # Remove common prefixes
    for prefix in ['Copy of ', 'GH ', 'AGMD ', 'BC3 ', 'OO ', 'TR ']:
        if project_name.startswith(prefix):
            project_name = project_name[len(prefix):]
    
    # Try to find ad type
    ad_type = 'Unknown'
    if 'VTD' in folder_name:
        ad_type = 'VTD'
    elif 'STOR' in folder_name:
        ad_type = 'STOR'
    elif 'ACT' in folder_name:
        ad_type = 'ACT'
    
    # Try to find test number
    test_match = re.search(r'(\d{4,5})', folder_name)
    test_name = test_match.group(1) if test_match else '0000'
    
    # Try to find version letter
    version_match = re.search(r'_([A-Z])(?:\.|_|$)', folder_name)
    version_letter = version_match.group(1) if version_match else ''
    
    return {
        'project_name': project_name.strip(),
        'ad_type': ad_type,
        'test_name': test_name,
        'version_letter': version_letter
    }