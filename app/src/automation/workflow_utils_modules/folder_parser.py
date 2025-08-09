# app/src/automation/workflow_utils_modules/folder_parser.py
"""
Folder name parsing strategies - different formats and patterns
Split from the original 205-line parse_project_info function
"""

import re
from typing import Optional, Dict
from urllib.parse import unquote

def extract_folder_name_from_drive_link(gdrive_link: str) -> Optional[str]:
    """
    Extract folder name from various Google Drive link formats.
    
    Args:
        gdrive_link: Google Drive URL or folder name
        
    Returns:
        Extracted folder name or original string if not a link
    """
    # If it's already just a folder name, return it
    if not gdrive_link.startswith('http'):
        return gdrive_link.strip()
    
    # Handle different Google Drive URL patterns
    patterns = [
        r'/folders/([^/?]+)',  # Standard folder link
        r'/file/d/([^/?]+)',   # File link (might be folder)
        r'[?&]id=([^&]+)',     # ID parameter
        r'/open\?id=([^&]+)',  # Open link format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, gdrive_link)
        if match:
            folder_id = match.group(1)
            # Try to extract folder name from URL if present
            name_match = re.search(r'/([^/]+)(?:\?|$)', gdrive_link)
            if name_match:
                folder_name = unquote(name_match.group(1))
                return folder_name.strip()
            return folder_id
    
    # If no pattern matches, return the original
    return gdrive_link.strip()

def parse_standard_format(folder_name: str) -> Optional[Dict[str, str]]:
    """
    Parse standard naming format: ACCOUNT_PROJECT_AD_TEST
    Example: OO_Grocery Store Oils Ad_AD_VTD-12036_4x5_250721A
    
    Args:
        folder_name: Folder name to parse
        
    Returns:
        Parsed info dictionary or None if doesn't match
    """
    # Remove "Copy of " prefix if present
    cleaned_name = folder_name
    if cleaned_name.startswith("Copy of "):
        cleaned_name = cleaned_name[8:]
    
    # Standard pattern: ACCOUNT_PROJECT_AD_TYPE-NUMBER_DIMENSIONS_DATE+LETTER
    pattern = r'^([A-Z]{2,4})_(.+?)_([A-Z]+)_(VTD|STOR|ACT)-(\d+)(?:_.*?_.*?([A-Z]))?'
    match = re.match(pattern, cleaned_name)
    
    if match:
        account_code = match.group(1)
        project_name = match.group(2)
        # ad_prefix = match.group(3)  # Usually "AD"
        ad_type = match.group(4)
        test_number = match.group(5)
        version_letter = match.group(6) or ''
        
        # Clean project name (remove "Ad" suffix if present)
        if project_name.endswith(' Ad'):
            project_name = project_name[:-3]
        
        return {
            'project_name': project_name.strip(),
            'ad_type': ad_type,
            'test_name': test_number,
            'version_letter': version_letter,
            'account_code': account_code
        }
    
    return None

def parse_alternative_format(folder_name: str) -> Optional[Dict[str, str]]:
    """
    Parse alternative naming formats with variations.
    Handles missing underscores, different separators, etc.
    
    Args:
        folder_name: Folder name to parse
        
    Returns:
        Parsed info dictionary or None if doesn't match
    """
    # Remove common prefixes
    cleaned_name = folder_name
    for prefix in ["Copy of ", "GH ", "AGMD "]:
        if cleaned_name.startswith(prefix):
            cleaned_name = cleaned_name[len(prefix):]
    
    # Pattern 1: PROJECT NAME TYPE NUMBER (spaces instead of underscores)
    pattern1 = r'^(.+?)\s+(VTD|STOR|ACT)[\s-](\d{4,5})(?:.*?([A-Z])(?:\.|_|$))?'
    match = re.match(pattern1, cleaned_name)
    
    if match:
        project_name = match.group(1)
        ad_type = match.group(2)
        test_number = match.group(3)
        version_letter = match.group(4) or ''
        
        # Clean project name
        project_name = re.sub(r'\s+Quiz$', '', project_name)
        project_name = re.sub(r'\s+Ad$', '', project_name)
        
        return {
            'project_name': project_name.strip(),
            'ad_type': ad_type,
            'test_name': test_number,
            'version_letter': version_letter
        }
    
    # Pattern 2: Compact format without clear separators
    pattern2 = r'(.+?)(VTD|STOR|ACT)(\d{4,5})'
    match = re.match(pattern2, cleaned_name)
    
    if match:
        project_name = match.group(1)
        ad_type = match.group(2)
        test_number = match.group(3)
        
        # Extract version letter if present
        version_match = re.search(r'(\d{6})([A-Z])', cleaned_name)
        version_letter = version_match.group(2) if version_match else ''
        
        return {
            'project_name': project_name.strip('_ '),
            'ad_type': ad_type,
            'test_name': test_number,
            'version_letter': version_letter
        }
    
    return None

def parse_legacy_format(folder_name: str) -> Optional[Dict[str, str]]:
    """
    Parse legacy/old naming formats from previous versions.
    
    Args:
        folder_name: Folder name to parse
        
    Returns:
        Parsed info dictionary or None if doesn't match
    """
    # Legacy pattern: PROJECT_TEST_TYPE or PROJECT-TEST-TYPE
    patterns = [
        # Old format with hyphens
        r'^(.+?)-(\d{4,5})-(VTD|STOR|ACT)',
        # Old format with mixed separators
        r'^(.+?)_(\d{4,5})_(VTD|STOR|ACT)',
        # Very old format
        r'^(.+?)\s+Test\s+(\d+)\s+(VTD|STOR|ACT)',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, folder_name, re.IGNORECASE)
        if match:
            project_name = match.group(1)
            test_number = match.group(2)
            ad_type = match.group(3).upper()
            
            # Try to find version letter
            version_match = re.search(r'[_\s]([A-Z])(?:\.|_|$)', folder_name)
            version_letter = version_match.group(1) if version_match else ''
            
            return {
                'project_name': project_name.strip('_ '),
                'ad_type': ad_type,
                'test_name': test_number,
                'version_letter': version_letter
            }
    
    return None