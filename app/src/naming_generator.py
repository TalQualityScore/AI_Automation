# app/src/naming_generator.py - COMPLETE VERSION WITH ALL REQUIRED FUNCTIONS

import os
import re
from unidecode import unidecode

def generate_project_folder_name(project_name, first_client_video, ad_type_selection):
    """Generate standardized project folder name"""
    
    # Clean the project name
    clean_project = unidecode(project_name).replace(" ", "")
    
    # Extract base info from first video
    base_name = os.path.splitext(os.path.basename(first_client_video))[0].replace("Copy of OO_", "")
    
    # Extract ad type and test number
    ad_type_match = re.search(r'(VTD|STOR|ACT)', base_name)
    ad_type = ad_type_match.group(1) if ad_type_match else ""
    
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', base_name)
    test_name = test_name_match.group(1) if test_name_match else ""
    
    # Build folder name: "GH ProjectName AdType TestNumber AdTypeSelection"
    folder_name = f"GH {project_name} {ad_type} {test_name} {ad_type_selection}"
    
    print(f"📁 Generated folder name: {folder_name}")
    return folder_name

def generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter=""):
    """FIXED: Extract version letters B/C from client filenames properly"""
    
    base_name = os.path.splitext(os.path.basename(first_client_video))[0].replace("Copy of OO_", "")
    
    print(f"🔍 NAMING DEBUG - Input filename: '{base_name}'")
    print(f"🔍 NAMING DEBUG - Full path: '{first_client_video}'")
    
    ad_type_match = re.search(r'(VTD|STOR|ACT)', base_name)
    ad_type = ad_type_match.group(1) if ad_type_match else ""
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', base_name)
    test_name = test_name_match.group(1) if test_name_match else ""
    
    # FIXED: Multiple patterns for version letter extraction
    if not version_letter:
        print(f"🔍 EXTRACTING VERSION LETTER from: '{base_name}'")
        
        # Pattern 1: _250416C (most common)
        pattern1 = re.search(r'_\d{6}([A-Z])(?:_\d+)?$', base_name)
        if pattern1:
            version_letter = pattern1.group(1)
            print(f"✅ PATTERN 1 MATCH: Found '{version_letter}' in '{base_name}'")
        else:
            # Pattern 2: _250416B_001 (with suffix)
            pattern2 = re.search(r'_\d{6}([A-Z])_', base_name)
            if pattern2:
                version_letter = pattern2.group(1)
                print(f"✅ PATTERN 2 MATCH: Found '{version_letter}' in '{base_name}'")
            else:
                # Pattern 3: STOR-3133B (directly after test number)
                pattern3 = re.search(r'(?:VTD|STOR|ACT)-\d+([A-Z])', base_name)
                if pattern3:
                    version_letter = pattern3.group(1)
                    print(f"✅ PATTERN 3 MATCH: Found '{version_letter}' in '{base_name}'")
                else:
                    # Pattern 4: Any single letter at end of filename
                    pattern4 = re.search(r'([A-Z])(?:_\d+)?$', base_name)
                    if pattern4:
                        version_letter = pattern4.group(1)
                        print(f"✅ PATTERN 4 MATCH: Found '{version_letter}' in '{base_name}'")
                    else:
                        print(f"⚠️ NO VERSION LETTER FOUND in '{base_name}' - using default")
                        version_letter = ""

    part1 = "GH"
    part2 = unidecode(project_name).lower().replace(" ", "")
    part3 = ad_type
    part4 = f"{test_name}{version_letter}"  # Include version letter here
    part5 = ad_type_selection
    part6 = image_desc.lower().replace(" ", "").replace("_", "")
    part7 = f"v{version_num:02d}"
    part8, part9, part10 = "m01", "f00", "c00"
    
    name_part = f"{part1}-{part2}{part3}{part4}ZZ{part5}"
    version_part = f"{part7}-{part8}-{part9}-{part10}"
    
    final_name = f"{name_part}_{part6}-{version_part}"
    
    print(f"🎯 FINAL OUTPUT NAME: '{final_name}'")
    print(f"   📋 Breakdown:")
    print(f"   - Project: {part2}")
    print(f"   - Ad Type: {part3}")
    print(f"   - Test + Letter: {part4}")
    print(f"   - Version Letter: '{version_letter}'")
    
    return final_name

def get_image_description(video_path):
    """Generate a simple image description from video filename"""
    
    # Extract base filename without extension
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # Remove common prefixes
    base_name = base_name.replace("Copy of OO_", "").replace("OO_", "")
    
    # Extract meaningful parts and create description
    # Look for recognizable keywords
    keywords = []
    
    # Common product/topic keywords
    product_patterns = [
        (r'grocery', 'grocery'),
        (r'cooking', 'cooking'),
        (r'oil', 'oil'),
        (r'health', 'health'),
        (r'dinner', 'dinner'),
        (r'mashup', 'mashup'),
        (r'recipe', 'recipe'),
        (r'kitchen', 'kitchen')
    ]
    
    base_lower = base_name.lower()
    for pattern, keyword in product_patterns:
        if re.search(pattern, base_lower):
            keywords.append(keyword)
    
    # If we found keywords, use them
    if keywords:
        description = "_".join(keywords[:2])  # Max 2 keywords
    else:
        # Fallback: use first part of filename
        parts = re.split(r'[_\-]', base_name)
        if len(parts) > 0 and len(parts[0]) > 2:
            description = parts[0][:10].lower()  # First 10 chars
        else:
            description = "video"
    
    # Clean up the description
    description = re.sub(r'[^a-zA-Z0-9]', '', description)
    
    print(f"🖼️ Generated image description: '{description}' from '{base_name}'")
    return description

def parse_project_info(folder_name):
    """Parse project information from folder name (from workflow_utils)"""
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

# Test function to debug version letter extraction
def test_version_letter_extraction():
    """Test version letter extraction with various filename patterns"""
    
    test_files = [
        "AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416C.mp4",
        "AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416B.mp4", 
        "Copy of OO_GroceryOils_AD_STOR-5421B_002.mp4",
        "MCT_CookingOil_AD_VTD-1234C_220315.mp4",
        "PP_HealthOils_STOR-9999A_001.mp4"
    ]
    
    print("🧪 TESTING VERSION LETTER EXTRACTION:")
    print("-" * 50)
    
    for filename in test_files:
        base_name = os.path.splitext(os.path.basename(filename))[0].replace("Copy of OO_", "")
        print(f"\n📁 File: {filename}")
        print(f"📄 Base: {base_name}")
        
        # Test each pattern
        pattern1 = re.search(r'_\d{6}([A-Z])(?:_\d+)?$', base_name)
        pattern2 = re.search(r'_\d{6}([A-Z])_', base_name)
        pattern3 = re.search(r'(?:VTD|STOR|ACT)-\d+([A-Z])', base_name)
        pattern4 = re.search(r'([A-Z])(?:_\d+)?$', base_name)
        
        if pattern1:
            print(f"✅ Pattern 1: {pattern1.group(1)}")
        elif pattern2:
            print(f"✅ Pattern 2: {pattern2.group(1)}")
        elif pattern3:
            print(f"✅ Pattern 3: {pattern3.group(1)}")
        elif pattern4:
            print(f"✅ Pattern 4: {pattern4.group(1)}")
        else:
            print(f"❌ No letter found")

if __name__ == "__main__":
    test_version_letter_extraction()