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
    
    # Generic patterns that work with any prefix (OO, BC3, MCT, MK, etc.)
    patterns = [
        # Pattern 1: Classic format with _AD_ - [PREFIX]_[PROJECT]_AD_[ADTYPE]-[NUMBER]
        r'([A-Z0-9]+)_(.*?)_AD_([A-Z]+)-(\d+)',
        
        # Pattern 2: GH prefix format - GH [PREFIX]_[PROJECT]_AD_[ADTYPE]-[NUMBER]
        r'GH\s+([A-Z0-9]+)_(.*?)_AD_([A-Z]+)-(\d+)',
        
        # Pattern 3: Modern format with OPT - [COMPANY]_[PREFIX]_[PROJECT]_OPT_[ADTYPE]-[NUMBER]
        r'([A-Z0-9_]+)_([A-Z0-9]+)_(.*?)_OPT_([A-Z]+)-(\d+)',
        
        # Pattern 4: GH with modern format - GH [COMPANY]_[PREFIX]_[PROJECT]_OPT_[ADTYPE]-[NUMBER]
        r'GH\s+([A-Z0-9_]+)_([A-Z0-9]+)_(.*?)_OPT_([A-Z]+)-(\d+)',
        
        # Pattern 5: Mixed format with AD-It - [PREFIX]_(.*?)_.*?AD-It.*?[ADTYPE]-[NUMBER]
        r'([A-Z0-9]+)_(.*?)_.*?AD-It.*?([A-Z]+)-(\d+)',
        
        # Pattern 6: Very flexible - anything with GH followed by content and ending with [ADTYPE]-[NUMBER]
        r'GH\s+(.*?)_.*?([A-Z]+)-(\d+)',
        
        # Pattern 7: Ultimate fallback - find any [ADTYPE]-[NUMBER] and work backwards
        r'(.*?)(?:_.*?)?([A-Z]+)-(\d+)',
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, folder_name)
        if match:
            groups = match.groups()
            
            if i in [0, 1, 4]:  # Patterns with 4 groups: prefix, project, adtype, number
                prefix = groups[0]
                raw_project_name = groups[1]
                ad_type = groups[2]
                test_name = groups[3]
                project_name = clean_project_name(raw_project_name)
                
            elif i in [2, 3]:  # Modern patterns with 5 groups: company, prefix, project, adtype, number
                company = groups[0]
                prefix = groups[1]
                raw_project_name = groups[2]
                ad_type = groups[3]
                test_name = groups[4]
                # Combine company and project name
                combined_name = f"{company} {raw_project_name}".replace('_', ' ')
                project_name = clean_project_name(combined_name)
                
            elif i == 5:  # GH flexible pattern with 3 groups
                raw_content = groups[0]
                ad_type = groups[1]
                test_name = groups[2]
                # Try to extract meaningful project name from content
                # Remove common prefixes and clean up
                content_parts = raw_content.split('_')
                # Skip company/prefix parts, take the meaningful project parts
                if len(content_parts) >= 3:
                    raw_project_name = '_'.join(content_parts[2:])  # Skip first 2 parts (company_prefix)
                else:
                    raw_project_name = raw_content
                project_name = clean_project_name(raw_project_name)
                
            else:  # Ultimate fallback pattern
                raw_content = groups[0]
                ad_type = groups[1]
                test_name = groups[2]
                # Extract project name from the end part before ad type
                content_clean = re.sub(r'.*?GH\s+', '', raw_content)  # Remove everything up to GH
                content_parts = content_clean.split('_')
                # Take meaningful parts, skip obvious prefixes
                meaningful_parts = [part for part in content_parts if len(part) > 2 and not part.isupper()]
                if meaningful_parts:
                    raw_project_name = '_'.join(meaningful_parts)
                else:
                    raw_project_name = content_clean
                project_name = clean_project_name(raw_project_name)
            
            print(f"Pattern {i+1} matched: '{raw_project_name}' -> '{project_name}'")
            
            return {
                "project_name": project_name,
                "ad_type": ad_type, 
                "test_name": test_name
            }
    
    # If no pattern matches, try to extract what we can
    print(f"No pattern matched. Attempting fallback parsing...")
    
    # Enhanced fallback: try to extract VTD/STOR/ACT and numbers manually
    ad_type_match = re.search(r'(VTD|STOR|ACT)', folder_name)
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', folder_name)
    
    if ad_type_match and test_name_match:
        # Try to extract project name from various patterns - now generic
        project_matches = [
            # Modern format: [COMPANY]_[PREFIX]_[PROJECT]_OPT_
            re.search(r'([A-Z0-9_]+)_([A-Z0-9]+)_(.*?)_OPT_', folder_name),
            # GH format: GH [COMPANY]_[PREFIX]_[PROJECT]_
            re.search(r'GH\s+([A-Z0-9_]+)_([A-Z0-9]+)_(.*?)_', folder_name),
            # Classic format: [PREFIX]_(.*?)_.*?AD
            re.search(r'([A-Z0-9]+)_(.*?)_.*?AD', folder_name),
            # Simple format: [PREFIX]_(.*?)_
            re.search(r'([A-Z0-9]+)_(.*?)_', folder_name),
            # Generic pattern for anything between GH and the ad type
            re.search(r'GH\s+(.*?)_(?:VTD|STOR|ACT)', folder_name),
        ]
        
        for project_match in project_matches:
            if project_match:
                groups = project_match.groups()
                if len(groups) >= 3:  # Modern pattern with company_prefix_project
                    company = groups[0]
                    prefix = groups[1]
                    raw_project_name = groups[2]
                    combined_name = f"{company} {raw_project_name}".replace('_', ' ')
                    project_name = clean_project_name(combined_name)
                else:
                    raw_project_name = groups[-1]  # Take the last group (project name)
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