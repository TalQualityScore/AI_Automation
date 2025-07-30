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
    
    # Updated patterns to handle your actual format
    patterns = [
        # Original patterns (keep for backwards compatibility)
        r'OO_(.*?)_AD_([A-Z]+)-(\d+)',
        r'GH OO_(.*?)_AD_([A-Z]+)-(\d+)',
        
        # New patterns for your format with AD-It
        r'OO.*?GH\s+OO_(.*?)_.*?AD-It.*?([A-Z]+)-(\d+)',  # Most flexible for your format
        r'GH OO_(.*?)_.*?AD-It.*?([A-Z]+)-(\d+)',         # Direct GH format with AD-It
        r'OO_(.*?)_.*?AD-It.*?([A-Z]+)-(\d+)',            # Simple OO format with AD-It
        
        # Even more flexible pattern as fallback
        r'OO.*?_(.*?)_.*?AD[_-](?:It.*?)?([A-Z]+)-(\d+)'  # Handles various AD separators
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, folder_name)
        if match:
            raw_project_name = match.group(1)
            project_name = clean_project_name(raw_project_name)
            
            print(f"Pattern {i+1} matched: '{raw_project_name}' -> '{project_name}'")
            
            return {
                "project_name": project_name,
                "ad_type": match.group(2), 
                "test_name": match.group(3)
            }
    
    # If no pattern matches, try to extract what we can
    print(f"No pattern matched. Attempting fallback parsing...")
    
    # Fallback: try to extract VTD/STOR/ACT and numbers manually
    ad_type_match = re.search(r'(VTD|STOR|ACT)', folder_name)
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', folder_name)
    
    if ad_type_match and test_name_match:
        # Try to extract project name from the middle section
        project_matches = [
            re.search(r'OO_(.*?)_.*?AD', folder_name),
            re.search(r'OO_(.*?)_', folder_name)  # Even more basic fallback
        ]
        
        for project_match in project_matches:
            if project_match:
                raw_project_name = project_match.group(1)
                project_name = clean_project_name(raw_project_name)
                
                print(f"Fallback extraction: '{raw_project_name}' -> '{project_name}'")
                
                return {
                    "project_name": project_name,
                    "ad_type": ad_type_match.group(1),
                    "test_name": test_name_match.group(1)
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