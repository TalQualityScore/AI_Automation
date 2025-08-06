# app/src/naming_generator.py - FIXED VERSION LETTER EXTRACTION

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