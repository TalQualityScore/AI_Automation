# app/src/naming/name_generator.py - Updated for SVSL/VSL support

import os
import re
from unidecode import unidecode
from .version_extractor import VersionExtractor

class NameGenerator:
    """Generates standardized names for files and folders with SVSL/VSL support"""
    
    def __init__(self):
        self.version_extractor = VersionExtractor()
    
    def generate_output_name(self, project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter=""):
        """
        Generate standardized output filename with correct format:
        GH-projectnameVTD12036AZZquiz_X-v01-m01-f00-c00.mp4
        GH-projectnameVTD12036AZZsvsl_X-v01-m01-f00-c00.mp4
        GH-projectnameVTD12036AZZvsl_X-v01-m01-f00-c00.mp4
        
        Args:
            project_name (str): Project name (will be cleaned to remove account prefixes)
            first_client_video (str): Path to first client video file
            ad_type_selection (str): Type selection - "quiz", "svsl", or "vsl"
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
        print(f"   Ad type selection: '{ad_type_selection}'")
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
                version_letter = ""  # No letter if not found
                print(f"🎯 No version letter found")
        else:
            print(f"🎯 USING PROVIDED VERSION LETTER: '{version_letter}'")
        
        print(f"🎯 EXTRACTED COMPONENTS:")
        print(f"   - Ad Type: {ad_type}")
        print(f"   - Test Number: {test_name}")
        print(f"   - Version Letter: '{version_letter}'")
        print(f"   - Version Num: {version_num:02d}")
        
        # Ensure ad_type_selection is lowercase and valid
        ad_type_selection = ad_type_selection.lower()
        if ad_type_selection not in ["quiz", "svsl", "vsl"]:
            ad_type_selection = "quiz"  # Default to quiz if invalid
            print(f"   ⚠️ Invalid ad_type_selection, defaulting to 'quiz'")
        
        # Build the output name components - CORRECT FORMAT
        part1 = "GH"
        # Remove spaces and lowercase the project name
        part2 = unidecode(cleaned_project_name).lower().replace(" ", "")
        part3 = ad_type
        part4 = f"{test_name}{version_letter}" if version_letter else test_name
        part5 = "ZZ"  # ALWAYS add ZZ
        part6 = ad_type_selection  # quiz, svsl, or vsl
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
        Now supports Quiz, SVSL, and VSL folder naming
        
        Args:
            project_name (str): Project name (will be cleaned to remove account prefixes)
            first_client_video (str): Path to first client video
            ad_type_selection (str): Ad type selection - "Quiz", "SVSL", or "VSL"
            
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
        
        # Ensure ad_type_selection has proper case for folder names
        folder_type_mapping = {
            "quiz": "Quiz",
            "svsl": "SVSL",
            "vsl": "VSL"
        }
        
        # Normalize the input
        normalized_selection = ad_type_selection.lower()
        folder_type = folder_type_mapping.get(normalized_selection, "Quiz")
        
        # Build folder name: "GH ProjectName AdType TestNumber FolderType"
        folder_name = f"GH {cleaned_project_name} {ad_type} {test_name} {folder_type}"
        
        print(f"📁 Generated folder name: '{folder_name}' (type: {folder_type})")
        return folder_name
    
    def _remove_account_prefix(self, project_name):
        """Remove account prefixes like 'AGMD', 'BC3', 'OO', 'MCT', etc."""
        # List of known account prefixes to remove
        account_prefixes = [
            'AGMD', 'BC3', 'OO', 'MCT', 'TR', 'DS', 'NB', 'MK', 
            'DRC', 'PC', 'GD', 'MC', 'PP', 'SPC', 'MA', 'KA', 'BLR'
        ]
        
        cleaned_name = project_name
        for prefix in account_prefixes:
            # Remove prefix if it appears at the start with space or underscore
            if cleaned_name.startswith(prefix + ' '):
                cleaned_name = cleaned_name[len(prefix) + 1:]
                break
            elif cleaned_name.startswith(prefix + '_'):
                cleaned_name = cleaned_name[len(prefix) + 1:]
                break
            elif cleaned_name == prefix:
                # If the entire name is just the prefix, keep it
                break
        
        return cleaned_name
    
    def _extract_ad_type(self, base_name):
        """Extract ad type (VTD, STOR, ACT, etc.) from filename - FIXED"""
        # Pattern to match ad types - look for VTD/STOR/ACT specifically
        # The file format is: ...Ad_AD_VTD-12036...
        # We want VTD, not AD
        
        ad_type_patterns = [
            r'_(VTD|STOR|ACT|CTA|UGC|OPT)[-_](\d{4,5})',  # Matches _VTD-12036
            r'(VTD|STOR|ACT|CTA|UGC|OPT)[-_](\d{4,5})',   # Matches VTD-12036
            r'_(VTD|STOR|ACT|CTA|UGC|OPT)$',              # Matches _VTD at end
        ]
        
        for pattern in ad_type_patterns:
            match = re.search(pattern, base_name, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        # If no VTD/STOR/ACT found, default to VTD
        return "VTD"

    def _extract_test_number(self, base_name):
        """Extract test number from filename - FIXED to get full 5 digits"""
        # The format is VTD-12036, we want 12036 (5 digits)
        
        # Look specifically after VTD/STOR/ACT
        test_patterns = [
            r'(?:VTD|STOR|ACT|CTA|UGC|OPT)[-_](\d{4,5})',  # After ad type
            r'[-_](\d{5})[-_]',                             # Any 5-digit number
            r'[-_](\d{5})',                                 # 5 digits anywhere
            r'[-_](\d{4})[-_]',                             # Fallback to 4 digits
            r'[-_](\d{4})',                                 # 4 digits anywhere
        ]
        
        for pattern in test_patterns:
            match = re.search(pattern, base_name, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "0000"  # Default if no test number found