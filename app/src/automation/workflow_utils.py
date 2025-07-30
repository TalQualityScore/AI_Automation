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
        # Keep UGC as-is (don't separate it and keep it in caps)
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
    
    # FIXED: Better patterns with priority order - focusing on extracting full project names
    patterns = [
        # Pattern 1: Standard OO format - OO_[FULL_PROJECT]_AD_[TYPE]-[NUMBER]
        r'OO_(.*?)_AD_([A-Z]+)-(\d+).*?([A-Z])_\d+\.mp4',
        
        # Pattern 2: Standard OO format without file extension  
        r'OO_(.*?)_AD_([A-Z]+)-(\d+).*?([A-Z])_\d+',
        
        # Pattern 3: AD-It format - OO_[FULL_PROJECT]_AD-It_[TYPE]-[NUMBER]
        r'OO_(.*?)_AD-It_([A-Z]+)-(\d+).*?([A-Z])_?\d*',
        
        # Pattern 4: AD-It format without letter
        r'OO_(.*?)_AD-It_([A-Z]+)-(\d+)',
        
        # Pattern 5: Modern format with OPT - [COMPANY]_[PREFIX]_[PROJECT]_OPT_[ADTYPE]-[NUMBER]
        r'([A-Z0-9_]+)_([A-Z0-9]+)_(.*?)_OPT_([A-Z]+)-(\d+).*?([A-Z])',
        
        # Pattern 6: GH prefix format - should extract the FULL project part, not just prefix
        r'GH\s+OO_(.*?)_AD[_-](?:It_)?([A-Z]+)-(\d+)',
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
                
            elif i in [2, 3]:  # AD-It patterns
                raw_project_name = groups[0]
                ad_type = groups[1]
                test_name = groups[2]
                version_letter = groups[3] if len(groups) > 3 else ""
                project_name = clean_project_name(raw_project_name)
                
            elif i == 4:  # Modern format with OPT
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
                    
            elif i == 5:  # GH format - FIXED to extract full project name
                raw_project_name = groups[0]  # This should be the full project name after OO_
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
    
    # Manual fallback extraction - ENHANCED for ANY account prefix
    ad_type_match = re.search(r'(VTD|STOR|ACT)', folder_name)
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', folder_name)
    version_letter_match = re.search(r'_(\d+)([A-Z])_?\d*', folder_name)
    
    if ad_type_match and test_name_match:
        # Try different account prefix patterns
        project_patterns = [
            r'([A-Z]+W?)_(.*?)_AD_(?:VTD|STOR|ACT)',
            r'([A-Z]+)_(.*?)_AD-It_(?:VTD|STOR|ACT)',
            r'([A-Z]+)_(.*?)_AD_(?:VTD|STOR|ACT)',
            r'([A-Z]+)_(.*?)_(?:VTD|STOR|ACT)',
        ]
        
        for pattern in project_patterns:
            project_match = re.search(pattern, folder_name)
            if project_match:
                groups = project_match.groups()
                if len(groups) >= 2:
                    raw_project_name = groups[1]
                    if len(raw_project_name) > 3 or not raw_project_name.isupper():
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