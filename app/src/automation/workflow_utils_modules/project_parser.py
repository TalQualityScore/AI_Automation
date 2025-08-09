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
    FIXED: Extract folder name from card title and parse properly
    
    Args:
        folder_name: The folder name that couldn't be parsed
        
    Returns:
        Dictionary with default/extracted values
    """
    # CRITICAL FIX: Check if this is a Trello card title with "from GH" pattern
    if "from GH" in folder_name:
        # Extract the actual folder name from after "from GH"
        parts = folder_name.split("from GH", 1)
        if len(parts) > 1:
            actual_folder = parts[1].strip()
            # Remove the (VTD XXXX) suffix if present
            actual_folder = re.sub(r'\s*\([^)]*\)\s*$', '', actual_folder)
            
            # Try to parse the actual folder with standard pattern
            # Pattern: OO_Grocery Store Oils Ad_AD_VTD-12036_4x5_250721
            pattern = r'^([A-Z]{2,4})_(.+?)_AD_(VTD|STOR|ACT)-(\d+)'
            match = re.match(pattern, actual_folder)
            
            if match:
                project_name = match.group(2)
                if project_name.endswith(' Ad'):
                    project_name = project_name[:-3]
                
                return {
                    'project_name': project_name.strip(),
                    'ad_type': match.group(3),
                    'test_name': match.group(4),
                    'version_letter': ''
                }
            
            # Use the extracted folder as base for parsing
            folder_name = actual_folder
    
    # Try to extract any useful information
    project_name = folder_name
    
    # Try to extract VTD/STOR/ACT and number
    ad_type_match = re.search(r'(VTD|STOR|ACT)', folder_name, re.IGNORECASE)
    test_num_match = re.search(r'(?:VTD|STOR|ACT)[\s-]*(\d{4,5})', folder_name, re.IGNORECASE)
    
    if ad_type_match and test_num_match:
        ad_type = ad_type_match.group(1).upper()
        test_name = test_num_match.group(1)
        
        # Extract project name more carefully
        # Remove card title prefix if present
        project_name = re.sub(r'^[A-Z]{2,4}\s+[A-Z]{2,4}\s*-\s*New Ads from GH\s*', '', project_name)
        # Remove parenthetical suffix
        project_name = re.sub(r'\s*\([^)]*\)\s*$', '', project_name)
        # Try to get just the project part
        project_match = re.search(r'([A-Z]{2,4}_)?(.+?)(?:_AD_|_AD-It_)', project_name)
        if project_match:
            project_name = project_match.group(2)
        
        # Clean up underscores and get proper name
        project_name = project_name.replace('_', ' ').strip()
        if project_name.endswith(' Ad'):
            project_name = project_name[:-3]
        
        # Try to find version letter
        version_match = re.search(r'_([A-Z])(?:\.|_|$)', folder_name)
        version_letter = version_match.group(1) if version_match else ''
        
        return {
            'project_name': project_name,
            'ad_type': ad_type,
            'test_name': test_name,
            'version_letter': version_letter
        }
    
    # Absolute fallback - but DON'T apply title case to everything!
    # Remove common prefixes
    for prefix in ['Copy of ', 'GH ', 'AGMD ', 'BC3 ', 'OO ', 'TR ']:
        if project_name.startswith(prefix):
            project_name = project_name[len(prefix):]
    
    # Try to find ad type even without full parsing
    ad_type = 'VTD'  # Default
    if 'VTD' in folder_name.upper():
        ad_type = 'VTD'
    elif 'STOR' in folder_name.upper():
        ad_type = 'STOR'
    elif 'ACT' in folder_name.upper():
        ad_type = 'ACT'
    
    # Try to find test number
    test_match = re.search(r'(\d{4,5})', folder_name)
    test_name = test_match.group(1) if test_match else '0000'
    
    return {
        'project_name': project_name.strip() or 'Unknown Project',
        'ad_type': ad_type,
        'test_name': test_name,
        'version_letter': ''
    }