# app/src/naming/name_generator.py - FIXED: Correct output format with ZZ

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
        Generate standardized output filename with correct format:
        GH-projectnameVTD12036AZZquiz_X-v01-m01-f00-c00.mp4
        
        Args:
            project_name (str): Project name (will be cleaned to remove account prefixes)
            first_client_video (str): Path to first client video file
            ad_type_selection (str): Ad type selection (Quiz, Connector, etc.)
            image_desc (str): Image description (IGNORED - will use X placeholder)
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
        
        # Clean project name to remove account prefixes
        cleaned_project_name = self._remove_account_prefix(project_name)
        print(f"   Cleaned project: '{cleaned_project_name}' (removed account prefix)")
        
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
        
        # Build the output name components - CORRECT FORMAT
        part1 = "GH"
        # Remove spaces and lowercase the project name
        part2 = unidecode(cleaned_project_name).lower().replace(" ", "")
        part3 = ad_type
        part4 = f"{test_name}{version_letter}"
        part5 = "ZZ"  # ALWAYS add ZZ
        part6 = ad_type_selection.lower()  # quiz, connector, etc.
        part7 = "X"  # ALWAYS use X as placeholder
        part8 = f"v{version_num:02d}"
        part9, part10, part11 = "m01", "f00", "c00"
        
        # Combine components with correct format
        # GH-projectnameVTD12036AZZquiz_X-v01-m01-f00-c00
        name_part = f"{part1}-{part2}{part3}{part4}{part5}{part6}"
        version_part = f"{part8}-{part9}-{part10}-{part11}"
        final_name = f"{name_part}_{part7}-{version_part}"
        
        print(f"🎯 FINAL OUTPUT NAME: '{final_name}'")
        print(f"   📋 Components:")
        print(f"   - GH prefix: {part1}")
        print(f"   - Project: {part2}")
        print(f"   - Ad type: {part3}")
        print(f"   - Test + Letter: {part4}")
        print(f"   - ZZ constant: {part5}")
        print(f"   - Ad selection: {part6}")
        print(f"   - Placeholder: {part7} (X for future API)")
        print(f"   - Version part: {version_part}")
        
        return final_name
    
    def generate_project_folder_name(self, project_name, first_client_video, ad_type_selection):
        """
        Generate standardized project folder name WITHOUT account prefixes
        
        Args:
            project_name (str): Project name (will be cleaned to remove account prefixes)
            first_client_video (str): Path to first client video
            ad_type_selection (str): Ad type selection
            
        Returns:
            str: Generated folder name
        """
        base_name = os.path.splitext(os.path.basename(first_client_video))[0]
        base_name = base_name.replace("Copy of OO_", "")
        
        # Clean project name to remove account prefixes
        cleaned_project_name = self._remove_account_prefix(project_name)
        
        # Extract components
        ad_type = self._extract_ad_type(base_name)
        test_name = self._extract_test_number(base_name)
        
        # Build folder name: "GH ProjectName AdType TestNumber AdTypeSelection" (no account prefix)
        folder_name = f"GH {cleaned_project_name} {ad_type} {test_name} {ad_type_selection}"
        
        print(f"📁 Generated folder name: '{folder_name}' (account prefix removed)")
        return folder_name
    
    def _remove_account_prefix(self, project_name):
        """Remove account prefixes like 'AGMD', 'BC3', etc. from project name"""
        
        # Common account prefixes to remove (more comprehensive list)
        account_prefixes = [
            'AGMD', 'BC3', 'TR', 'OO', 'MCT', 'DS', 'NB', 'MK', 
            'DRC', 'PC', 'GD', 'MC', 'PP', 'SPC', 'MA', 'KA', 'BLR',
            'GMD', 'TOTAL', 'RESTORE', 'BIO', 'COMPLETE', 'OLIVE', 'OIL',
            'FB', 'YT', 'IG', 'TT', 'SNAP'  # Also remove platform codes if at start
        ]
        
        # Split project name into words
        words = project_name.split()
        
        # Remove account prefixes from the beginning
        while words:
            first_word = words[0].upper()
            
            # Check if first word is an account prefix
            if first_word in account_prefixes:
                print(f"🧹 REMOVING ACCOUNT PREFIX: '{words[0]}'")
                words = words[1:]  # Remove first word
            else:
                # Check for patterns like "Fb -" which are broken formats
                if len(words[0]) <= 3 and len(words) > 1 and words[1] == '-':
                    print(f"🧹 REMOVING BROKEN PREFIX: '{words[0]} {words[1]}'")
                    words = words[2:]  # Remove first two elements
                else:
                    break  # No more prefixes to remove
        
        # Also check for combined prefixes like "AGMD BC3"
        if len(words) >= 2:
            combined = f"{words[0]} {words[1]}".upper()
            if any(prefix in combined for prefix in account_prefixes):
                # If the combined first two words contain account codes, be more aggressive
                while words and len(words[0]) <= 4 and words[0].upper() in account_prefixes:
                    print(f"🧹 REMOVING ADDITIONAL PREFIX: '{words[0]}'")
                    words = words[1:]
        
        # Reconstruct the cleaned name
        cleaned_name = ' '.join(words) if words else project_name
        
        if cleaned_name != project_name:
            print(f"🧹 ACCOUNT PREFIX REMOVAL: '{project_name}' → '{cleaned_name}'")
        
        return cleaned_name if cleaned_name.strip() else project_name
    
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