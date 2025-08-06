# app/src/naming/name_generator.py
"""
Name Generation Module

Handles generation of output filenames and project folder names
using extracted project information and version data.
"""

import os
import re
from unidecode import unidecode
from .version_extractor import VersionExtractor

class NameGenerator:
    """Generates standardized names for files and folders"""
    
    def __init__(self):
        self.version_extractor = VersionExtractor()
    
    def generate_output_name(self, project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter=""):
        """
        Generate standardized output filename
        
        Args:
            project_name (str): Project name
            first_client_video (str): Path to first client video file
            ad_type_selection (str): Ad type selection (Quiz, etc.)
            image_desc (str): Image description
            version_num (int): Version number
            version_letter (str): Version letter override (optional)
            
        Returns:
            str: Generated output filename
        """
        base_name = os.path.splitext(os.path.basename(first_client_video))[0]
        base_name = base_name.replace("Copy of OO_", "")
        
        print(f"\n🔍 OUTPUT NAME GENERATION:")
        print(f"   Project: '{project_name}'")
        print(f"   Input file: '{first_client_video}'")
        print(f"   Base name: '{base_name}'")
        
        # Extract ad type and test number
        ad_type = self._extract_ad_type(base_name)
        test_name = self._extract_test_number(base_name)
        
        # Get version letter (use provided or extract from filename)
        if not version_letter:
            version_letter = self.version_extractor.extract_version_letter(first_client_video, debug=True)
            if not version_letter:
                version_letter = "ZZ"  # Default fallback
                print(f"🎯 DEFAULTING to 'ZZ' (no valid letter found)")
        else:
            print(f"🎯 USING PROVIDED VERSION LETTER: '{version_letter}'")
        
        print(f"🎯 EXTRACTED COMPONENTS:")
        print(f"   - Ad Type: {ad_type}")
        print(f"   - Test Number: {test_name}")
        print(f"   - Version Letter: '{version_letter}'")
        print(f"   - Version Num: {version_num:02d}")
        
        # Build the output name components
        part1 = "GH"
        part2 = unidecode(project_name).lower().replace(" ", "")
        part3 = ad_type
        part4 = f"{test_name}{version_letter}"
        part5 = ad_type_selection
        part6 = image_desc.lower().replace(" ", "").replace("_", "")
        part7 = f"v{version_num:02d}"
        part8, part9, part10 = "m01", "f00", "c00"
        
        # Combine components
        name_part = f"{part1}-{part2}{part3}{part4}ZZ{part5}"
        version_part = f"{part7}-{part8}-{part9}-{part10}"
        final_name = f"{name_part}_{part6}-{version_part}"
        
        print(f"🎯 FINAL OUTPUT NAME: '{final_name}'")
        print(f"   📋 Components:")
        print(f"   - Name part: {name_part}")
        print(f"   - Test + Letter: {part4}")
        print(f"   - Version part: {version_part}")
        
        return final_name
    
    def generate_project_folder_name(self, project_name, first_client_video, ad_type_selection):
        """
        Generate standardized project folder name
        
        Args:
            project_name (str): Project name
            first_client_video (str): Path to first client video
            ad_type_selection (str): Ad type selection
            
        Returns:
            str: Generated folder name
        """
        base_name = os.path.splitext(os.path.basename(first_client_video))[0]
        base_name = base_name.replace("Copy of OO_", "")
        
        # Extract components
        ad_type = self._extract_ad_type(base_name)
        test_name = self._extract_test_number(base_name)
        
        # Build folder name: "GH ProjectName AdType TestNumber AdTypeSelection"
        folder_name = f"GH {project_name} {ad_type} {test_name} {ad_type_selection}"
        
        print(f"📁 Generated folder name: '{folder_name}'")
        return folder_name
    
    def _extract_ad_type(self, base_name):
        """Extract ad type (VTD, STOR, ACT) from filename"""
        ad_type_match = re.search(r'(VTD|STOR|ACT)', base_name)
        return ad_type_match.group(1) if ad_type_match else ""
    
    def _extract_test_number(self, base_name):
        """Extract test number from filename"""
        test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', base_name)
        return test_name_match.group(1) if test_name_match else ""
    
    def validate_name_components(self, project_name, ad_type, test_name):
        """
        Validate that all required components are present for name generation
        
        Args:
            project_name (str): Project name
            ad_type (str): Ad type
            test_name (str): Test name/number
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not project_name or not project_name.strip():
            return False, "Project name is required"
        
        if not ad_type or ad_type not in ['VTD', 'STOR', 'ACT']:
            return False, f"Invalid ad type: '{ad_type}'. Must be VTD, STOR, or ACT"
        
        if not test_name or not test_name.isdigit():
            return False, f"Invalid test name: '{test_name}'. Must be numeric"
        
        return True, ""
    
    def test_name_generation(self):
        """Test name generation with sample data"""
        
        test_cases = [
            {
                'project_name': 'AGMD Dinner Mashup',
                'video_file': 'AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4',
                'ad_type_selection': 'Quiz',
                'image_desc': 'dinner',
                'version_num': 1,
                'expected_parts': ['GH', 'agmddinnermashup', 'STOR', '3133D', 'Quiz']
            },
            {
                'project_name': 'Grocery Store Oils',
                'video_file': 'OO_GroceryOils_AD_VTD-1234A_001.mp4',
                'ad_type_selection': 'Quiz',
                'image_desc': 'grocery',
                'version_num': 1,
                'expected_parts': ['GH', 'grocerystoreoils', 'VTD', '1234A', 'Quiz']
            }
        ]
        
        print("\n🧪 TESTING NAME GENERATION:")
        print("=" * 60)
        
        results = []
        for i, case in enumerate(test_cases, 1):
            print(f"\n📁 Test Case {i}:")
            print(f"   Project: '{case['project_name']}'")
            print(f"   Video: '{case['video_file']}'")
            
            result = self.generate_output_name(
                case['project_name'],
                case['video_file'],
                case['ad_type_selection'],
                case['image_desc'],
                case['version_num']
            )
            
            # Check if expected parts are in the result
            all_parts_found = all(part.lower() in result.lower() for part in case['expected_parts'])
            status = "✅ PASS" if all_parts_found else "❌ FAIL"
            
            results.append({
                'case': i,
                'result': result,
                'status': status
            })
            
            print(f"🎯 Status: {status}")
        
        return results

if __name__ == "__main__":
    generator = NameGenerator()
    generator.test_name_generation()