# app/src/automation/workflow_utils_modules/validation.py
"""
Validation and cleaning utilities for project info
Separated from the original workflow_utils.py
"""

import re
from typing import Dict, Optional

def validate_project_info(info: Dict[str, str], original_folder_name: str) -> Dict[str, str]:
    """
    Validate and clean project info, ensuring all required fields exist.
    
    Args:
        info: Project info dictionary to validate
        original_folder_name: Original folder name for fallback
        
    Returns:
        Validated and cleaned project info
    """
    if not info:
        return None
    
    # Ensure all required fields exist
    validated = {
        'project_name': info.get('project_name', original_folder_name),
        'ad_type': info.get('ad_type', 'Unknown'),
        'test_name': info.get('test_name', '0000'),
        'version_letter': info.get('version_letter', '')
    }
    
    # Clean project name
    validated['project_name'] = clean_project_name(validated['project_name'])
    
    # Validate ad_type
    if validated['ad_type'] not in ['VTD', 'STOR', 'ACT']:
        validated['ad_type'] = 'VTD'  # Default to VTD
    
    # Ensure test_name is numeric
    if not validated['test_name'].isdigit():
        # Try to extract numbers
        numbers = re.findall(r'\d+', validated['test_name'])
        validated['test_name'] = numbers[0] if numbers else '0000'
    
    # Ensure test_name is 4-5 digits
    validated['test_name'] = validated['test_name'].zfill(4)[:5]
    
    # Clean version letter (single uppercase letter)
    if validated['version_letter']:
        validated['version_letter'] = validated['version_letter'].upper()[:1]
        if not validated['version_letter'].isalpha():
            validated['version_letter'] = ''
    
    # Add account code if present
    if 'account_code' in info:
        validated['account_code'] = info['account_code']
    
    print(f"✅ Validated project info: {validated['project_name']} ({validated['ad_type']}-{validated['test_name']})")
    
    return validated

def clean_project_name(project_name: str) -> str:
    """
    Clean project name by removing prefixes, suffixes, and normalizing.
    FIXED: Don't destroy the structure with aggressive title case
    
    Args:
        project_name: Raw project name
        
    Returns:
        Cleaned project name
    """
    if not project_name:
        return "Unknown Project"
    
    cleaned = project_name
    
    # CRITICAL FIX: Handle the broken title case format first
    # If it looks like "Fb - New Ads From Gh..." it's already broken
    if re.match(r'^[A-Z][a-z]+\s*-\s*New Ads From', cleaned):
        # Try to extract just the meaningful part
        parts = cleaned.split("From Gh", 1)
        if len(parts) > 1:
            cleaned = parts[1].strip()
    
    # Remove common prefixes
    prefixes_to_remove = [
        'Copy of ', 'GH ', 'AGMD ', 'BC3 ', 'OO ', 'TR ', 'MCT ',
        'DS ', 'NB ', 'MK ', 'DRC ', 'PC ', 'GD ', 'MC ', 'PP ',
        'SPC ', 'MA ', 'KA ', 'BLR ', 'OO_', 'Copy of OO_'
    ]
    
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    
    # Remove "Ad" suffix if present
    if cleaned.endswith(' Ad'):
        cleaned = cleaned[:-3]
    
    # Remove common suffixes
    suffixes_to_remove = [' Quiz', ' Test', ' Final', ' Draft']
    for suffix in suffixes_to_remove:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)]
    
    # Replace underscores with spaces
    cleaned = cleaned.replace('_', ' ')
    
    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remove leading/trailing underscores and spaces
    cleaned = cleaned.strip('_ ')
    
    # CRITICAL: DON'T apply aggressive title case!
    # Just ensure proper spacing and preserve important acronyms
    if cleaned:
        words = cleaned.split()
        result_words = []
        
        # List of words that should stay uppercase
        preserve_upper = {'VTD', 'STOR', 'ACT', 'AD', 'GH', 'FB', 'YT', 'IG', 'TT'}
        
        for word in words:
            if word.upper() in preserve_upper:
                result_words.append(word.upper())
            elif word[0].islower():
                # Capitalize first letter only
                result_words.append(word[0].upper() + word[1:])
            else:
                result_words.append(word)
        
        cleaned = ' '.join(result_words)
    
    return cleaned if cleaned else "Unknown Project"

def extract_version_letter(folder_name: str) -> str:
    """
    Extract version letter from folder name.
    Looks for patterns like 250721A, 250721B, etc.
    
    Args:
        folder_name: Folder name to extract from
        
    Returns:
        Version letter (A, B, C, etc.) or empty string
    """
    # Pattern 1: Date followed by letter (250721A)
    pattern1 = r'(\d{6})([A-Z])(?:\.|_|$|\s)'
    match = re.search(pattern1, folder_name)
    if match:
        return match.group(2)
    
    # Pattern 2: Underscore or space followed by single letter at end
    pattern2 = r'[_\s]([A-Z])(?:\.|$)'
    match = re.search(pattern2, folder_name)
    if match:
        # Make sure it's not part of a word
        letter = match.group(1)
        # Check if it's preceded by numbers (like 12036_A)
        context = folder_name[:match.start()]
        if re.search(r'\d{4,5}$', context):
            return letter
    
    # Pattern 3: Version indicator (v1A, v2B, etc.)
    pattern3 = r'[vV]\d([A-Z])'
    match = re.search(pattern3, folder_name)
    if match:
        return match.group(1)
    
    return ''