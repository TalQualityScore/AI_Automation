# app/src/naming_generator.py - QUICK FIX FOR VERSION LETTER ISSUE

import os
import re
from unidecode import unidecode

def generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter=""):
    """FIXED: Extract version letters correctly from client filenames"""
    
    base_name = os.path.splitext(os.path.basename(first_client_video))[0].replace("Copy of OO_", "")
    
    print(f"\n🔍 VERSION LETTER EXTRACTION DEBUG:")
    print(f"   Input filename: '{first_client_video}'")
    print(f"   Base name: '{base_name}'")
    print(f"   Passed version_letter: '{version_letter}'")
    
    # Parse ad type and test number
    ad_type_match = re.search(r'(VTD|STOR|ACT)', base_name)
    ad_type = ad_type_match.group(1) if ad_type_match else ""
    
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', base_name)
    test_name = test_name_match.group(1) if test_name_match else ""
    
    # CRITICAL FIX: Enhanced version letter extraction with priority for your format
    extracted_letter = ""
    if not version_letter:
        print(f"🔍 No version letter provided, extracting from filename...")
        
        # PRIORITY PATTERN 1: _250416D format (your specific case)
        pattern1 = re.search(r'_(\d{6})([A-D])(?:\.mp4|\.mov|_|$)', base_name)
        if pattern1:
            date_part = pattern1.group(1)
            letter_part = pattern1.group(2)
            extracted_letter = letter_part
            print(f"✅ PATTERN 1 MATCH (_250416D): Found '{extracted_letter}' after date '{date_part}'")
        else:
            print(f"❌ PATTERN 1 FAILED: No match for _250416D pattern")
            
            # PATTERN 2: _20240408A format (longer date)
            pattern2 = re.search(r'_(\d{8})([A-D])(?:\.mp4|\.mov|_|$)', base_name)
            if pattern2:
                date_part = pattern2.group(1)
                letter_part = pattern2.group(2)
                extracted_letter = letter_part
                print(f"✅ PATTERN 2 MATCH (_20240408A): Found '{extracted_letter}' after date '{date_part}'")
            else:
                print(f"❌ PATTERN 2 FAILED: No match for _20240408A pattern")
                
                # PATTERN 3: STOR-3133D format (test number + letter)
                pattern3 = re.search(r'(?:VTD|STOR|ACT)-(\d+)([A-D])(?:\.mp4|\.mov|_|$)', base_name)
                if pattern3:
                    test_num = pattern3.group(1)
                    letter_part = pattern3.group(2)
                    extracted_letter = letter_part
                    print(f"✅ PATTERN 3 MATCH (STOR-3133D): Found '{extracted_letter}' after test '{test_num}'")
                else:
                    print(f"❌ PATTERN 3 FAILED: No match for STOR-3133D pattern")
                    
                    # PATTERN 4: Any number followed by letter
                    pattern4 = re.search(r'(\d+)([A-D])(?:\.mp4|\.mov|_|$)', base_name)
                    if pattern4:
                        num_part = pattern4.group(1)
                        letter_part = pattern4.group(2)
                        extracted_letter = letter_part
                        print(f"✅ PATTERN 4 MATCH (NumberLetter): Found '{extracted_letter}' after '{num_part}'")
                    else:
                        print(f"❌ ALL PATTERNS FAILED: No version letter found")
        
        # Final validation and assignment
        if extracted_letter and extracted_letter in ['A', 'B', 'C', 'D']:
            version_letter = extracted_letter
            print(f"🎯 FINAL VERSION LETTER: '{version_letter}' (extracted)")
        else:
            version_letter = "ZZ"  # Keep original fallback behavior
            print(f"🎯 DEFAULTING to 'ZZ' (no valid letter found)")
    else:
        print(f"🎯 USING PROVIDED VERSION LETTER: '{version_letter}'")

    print(f"🎯 FINAL RESULT:")
    print(f"   - Project: {project_name}")
    print(f"   - Ad Type: {ad_type}")
    print(f"   - Test Number: {test_name}")
    print(f"   - Version Letter: '{version_letter}'")
    print(f"   - Version Num: {version_num:02d}")

    # Build the output name using the CORRECT version letter
    part1 = "GH"
    part2 = unidecode(project_name).lower().replace(" ", "")
    part3 = ad_type
    part4 = f"{test_name}{version_letter}"  # This should now be correct (e.g., "3133D")
    part5 = ad_type_selection
    part6 = image_desc.lower().replace(" ", "").replace("_", "")
    part7 = f"v{version_num:02d}"
    part8, part9, part10 = "m01", "f00", "c00"
    
    name_part = f"{part1}-{part2}{part3}{part4}ZZ{part5}"
    version_part = f"{part7}-{part8}-{part9}-{part10}"
    final_name = f"{name_part}_{part6}-{version_part}"
    
    print(f"🎯 FINAL OUTPUT NAME: '{final_name}'")
    print(f"   📋 Components:")
    print(f"   - Name part: {name_part}")
    print(f"   - Test + Letter: {part4} (should show {test_name}{version_letter})")
    print(f"   - Version part: {version_part}")
    
    return final_name

# Keep all the other existing functions unchanged for now
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

# Keep other functions as they were...
def parse_project_info(folder_name):
    """Parse project information from folder name (simplified version for now)"""
    print(f"Parsing folder name: {folder_name}")
    
    # Simple pattern matching - can be enhanced later
    ad_type_match = re.search(r'(VTD|STOR|ACT)', folder_name)
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', folder_name)
    
    if ad_type_match and test_name_match:
        return {
            "project_name": "Parsed Project",  # Simplified for now
            "ad_type": ad_type_match.group(1),
            "test_name": test_name_match.group(1),
            "version_letter": ""
        }
    
    return None

def clean_project_name(raw_name):
    """Clean and format the project name properly."""
    if not raw_name:
        return ""
    
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