import os
import re

# --- CONFIGURATION ---
BASE_OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'Desktop')

# --- FUNCTIONS ---

def clean_project_name(raw_name):
    """Clean and format the project name properly."""
    # Replace + with spaces first
    name = raw_name.replace('+', ' ')
    
    # Split by spaces and process each word
    words = name.split()
    cleaned_words = []
    
    for word in words:
        # Keep UGC as-is (don't separate it)
        if word.upper() == 'UGC':
            cleaned_words.append('UGC')
        else:
            # Separate camelCase words (e.g., CookingOil -> Cooking Oil)
            # This regex finds lowercase followed by uppercase
            separated = re.sub(r'([a-z])([A-Z])', r'\1 \2', word)
            cleaned_words.append(separated)
    
    # Join all words with single spaces and clean up
    result = ' '.join(cleaned_words)
    
    # Remove any multiple spaces and strip
    result = re.sub(r'\s+', ' ', result).strip()
    
    # Remove common suffixes like "Ad"
    result = re.sub(r'\s+Ad$', '', result, flags=re.IGNORECASE)
    
    return result

def parse_project_info(folder_name):
    """Parses the project information from a folder name."""
    print(f"Parsing folder name: {folder_name}")
    
    # FIXED: Better patterns with priority order
    patterns = [
        # Pattern 1: Standard OO format - OO_[PROJECT]_AD_[TYPE]-[NUMBER]_[DETAILS]_[LETTER]
        r'OO_(.*?)_AD_([A-Z]+)-(\d+).*?([A-Z])_\d+\.mp4',
        
        # Pattern 2: Standard OO format without file extension
        r'OO_(.*?)_AD_([A-Z]+)-(\d+).*?([A-Z])_\d+',
        
        # Pattern 3: Standard OO format with less details
        r'OO_(.*?)_AD_([A-Z]+)-(\d+)',
        
        # Pattern 4: Modern format with OPT - [COMPANY]_[PREFIX]_[PROJECT]_OPT_[ADTYPE]-[NUMBER]
        r'([A-Z0-9_]+)_([A-Z0-9]+)_(.*?)_OPT_([A-Z]+)-(\d+).*?([A-Z])',
        
        # Pattern 5: GH prefix format
        r'GH\s+([A-Z0-9]+)_(.*?)_AD_([A-Z]+)-(\d+)',
        
        # Pattern 6: Flexible GH format
        r'GH\s+(.*?)_.*?([A-Z]+)-(\d+)',
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, folder_name)
        if match:
            groups = match.groups()
            print(f"Pattern {i+1} matched with {len(groups)} groups: {groups}")
            
            if i in [0, 1]:  # Standard OO patterns with letter
                if len(groups) >= 4:
                    raw_project_name = groups[0]
                    ad_type = groups[1]
                    test_name = groups[2]
                    version_letter = groups[3] if len(groups) > 3 else ""
                else:
                    raw_project_name = groups[0]
                    ad_type = groups[1]
                    test_name = groups[2]
                    version_letter = ""
                project_name = clean_project_name(raw_project_name)
                
            elif i == 2:  # Standard OO pattern without letter
                raw_project_name = groups[0]
                ad_type = groups[1]
                test_name = groups[2]
                version_letter = ""
                project_name = clean_project_name(raw_project_name)
                
            elif i == 3:  # Modern format with OPT
                if len(groups) >= 6:
                    company = groups[0]
                    prefix = groups[1]
                    raw_project_name = groups[2]
                    ad_type = groups[3]
                    test_name = groups[4]
                    version_letter = groups[5]
                    combined_name = f"{company} {raw_project_name}".replace('_', ' ')
                    project_name = clean_project_name(combined_name)
                else:
                    raw_project_name = groups[2]
                    ad_type = groups[3]
                    test_name = groups[4]
                    version_letter = ""
                    project_name = clean_project_name(raw_project_name)
                    
            elif i in [4, 5]:  # GH formats
                if len(groups) >= 4:
                    raw_project_name = groups[1]
                    ad_type = groups[2]
                    test_name = groups[3]
                    version_letter = ""
                else:
                    # Extract from content
                    content_parts = groups[0].split('_')
                    if len(content_parts) >= 2:
                        raw_project_name = '_'.join(content_parts[1:])  # Skip first part (likely prefix)
                    else:
                        raw_project_name = groups[0]
                    ad_type = groups[1]
                    test_name = groups[2]
                    version_letter = ""
                project_name = clean_project_name(raw_project_name)
            
            # Extract version letter if not found and available in filename
            if not version_letter:
                version_letter_match = re.search(r'_(\d+)([A-Z])_?\d*', folder_name)
                version_letter = version_letter_match.group(2) if version_letter_match else ""
            
            print(f"Extracted: '{raw_project_name}' -> '{project_name}' (Type: {ad_type}, Test: {test_name}, Letter: {version_letter})")
            
            return {
                "project_name": project_name,
                "ad_type": ad_type, 
                "test_name": test_name,
                "version_letter": version_letter
            }
    
    print(f"No pattern matched. Attempting manual extraction...")
    
    # Manual fallback extraction
    ad_type_match = re.search(r'(VTD|STOR|ACT)', folder_name)
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', folder_name)
    version_letter_match = re.search(r'_(\d+)([A-Z])_?\d*', folder_name)
    
    if ad_type_match and test_name_match:
        # Try to extract project name
        oo_match = re.search(r'OO_(.*?)_AD_', folder_name)
        if oo_match:
            raw_project_name = oo_match.group(1)
            project_name = clean_project_name(raw_project_name)
            version_letter = version_letter_match.group(2) if version_letter_match else ""
            
            print(f"Manual extraction: '{raw_project_name}' -> '{project_name}' (Letter: {version_letter})")
            
            return {
                "project_name": project_name,
                "ad_type": ad_type_match.group(1),
                "test_name": test_name_match.group(1),
                "version_letter": version_letter
            }
    
    print(f"Failed to parse folder name: {folder_name}")
    return None

def create_project_structure(project_folder_name):
    """Creates the standard project folder structure."""
    project_folder = os.path.join(BASE_OUTPUT_DIR, project_folder_name)
    
    subfolders = {
        "project_root": project_folder, 
        "ame": os.path.join(project_folder, "_AME"),
        "audio": os.path.join(project_folder, "_Audio"), 
        "copy": os.path.join(project_folder, "_Copy"),
        "footage": os.path.join(project_folder, "_Footage"), 
        "thumbnails": os.path.join(project_folder, "_Thumbnails"),
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