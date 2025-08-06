# app/src/naming/version_extractor.py
"""
Version Letter Extraction Module

Handles extraction of version letters (A, B, C, D) from client filenames
with multiple pattern matching strategies.
"""

import re
import os

class VersionExtractor:
    """Extracts version letters from video filenames using priority-based pattern matching"""
    
    def __init__(self):
        # Define extraction patterns in priority order
        self.patterns = [
            # Pattern 1: _250416D format (6-digit date + letter)
            {
                'name': '_250416D format',
                'regex': r'_(\d{6})([A-D])(?:\.mp4|\.mov|_|$)',
                'description': 'Six-digit date followed by version letter'
            },
            # Pattern 2: _20240408A format (8-digit date + letter) 
            {
                'name': '_20240408A format',
                'regex': r'_(\d{8})([A-D])(?:\.mp4|\.mov|_|$)',
                'description': 'Eight-digit date followed by version letter'
            },
            # Pattern 3: STOR-3133D format (test number + letter)
            {
                'name': 'STOR-3133D format',
                'regex': r'(?:VTD|STOR|ACT)-(\d+)([A-D])(?:\.mp4|\.mov|_|$)',
                'description': 'Test type and number followed by version letter'
            },
            # Pattern 4: Any number followed by letter
            {
                'name': 'NumberLetter format',
                'regex': r'(\d+)([A-D])(?:\.mp4|\.mov|_|$)',
                'description': 'Any number followed by version letter'
            }
        ]
    
    def extract_version_letter(self, filename, debug=True):
        """
        Extract version letter from filename using priority patterns
        
        Args:
            filename (str): Input filename or path
            debug (bool): Whether to print debug information
            
        Returns:
            str: Version letter (A, B, C, D) or empty string if not found
        """
        base_name = os.path.splitext(os.path.basename(filename))[0]
        base_name = base_name.replace("Copy of OO_", "")
        
        if debug:
            print(f"\n🔍 VERSION LETTER EXTRACTION:")
            print(f"   Input: '{filename}'")
            print(f"   Base name: '{base_name}'")
        
        # Try each pattern in priority order
        for i, pattern_info in enumerate(self.patterns, 1):
            pattern = pattern_info['regex']
            name = pattern_info['name']
            
            match = re.search(pattern, base_name)
            if match:
                if len(match.groups()) >= 2:
                    identifier = match.group(1)  # Date/number part
                    letter = match.group(2)      # Version letter
                    
                    if debug:
                        print(f"✅ PATTERN {i} MATCH ({name}): Found '{letter}' after '{identifier}'")
                    
                    return letter
                else:
                    if debug:
                        print(f"❌ PATTERN {i} PARTIAL ({name}): Match found but insufficient groups")
            else:
                if debug:
                    print(f"❌ PATTERN {i} FAILED ({name}): No match")
        
        if debug:
            print(f"❌ ALL PATTERNS FAILED: No version letter found")
        
        return ""
    
    def validate_version_letter(self, letter):
        """
        Validate that the extracted letter is valid
        
        Args:
            letter (str): Letter to validate
            
        Returns:
            bool: True if letter is valid (A, B, C, D)
        """
        return letter in ['A', 'B', 'C', 'D']
    
    def get_extraction_info(self):
        """
        Get information about available extraction patterns
        
        Returns:
            list: List of pattern information dictionaries
        """
        return self.patterns.copy()
    
    def test_extraction(self, test_files):
        """
        Test version letter extraction on multiple files
        
        Args:
            test_files (list): List of (filename, expected_letter) tuples
            
        Returns:
            dict: Test results with pass/fail status
        """
        results = {
            'total': len(test_files),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        print("🧪 TESTING VERSION LETTER EXTRACTION:")
        print("=" * 60)
        
        for filename, expected in test_files:
            print(f"\n📁 Testing: {filename}")
            print(f"📄 Expected: '{expected}'")
            
            extracted = self.extract_version_letter(filename, debug=False)
            
            if extracted == expected:
                status = "✅ PASS"
                results['passed'] += 1
            else:
                status = "❌ FAIL"
                results['failed'] += 1
            
            result_detail = {
                'filename': filename,
                'expected': expected,
                'extracted': extracted,
                'status': status
            }
            
            results['details'].append(result_detail)
            print(f"🎯 Result: {status} (Got: '{extracted}')")
        
        print(f"\n📊 SUMMARY: {results['passed']}/{results['total']} passed")
        return results

# Test function for standalone usage
def test_version_extractor():
    """Test the version extractor with common file patterns"""
    
    extractor = VersionExtractor()
    
    test_files = [
        ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4", "D"),
        ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416C.mp4", "C"), 
        ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416B.mp4", "B"),
        ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416A.mp4", "A"),
        ("GMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4", "D"),
        ("OO_GroceryOils_AD_VTD-1234A_001.mp4", "A"),
        ("MCT_CookingOil_AD_STOR-5678B.mp4", "B"),
        ("TestFile_NoLetter.mp4", "")  # Should return empty string
    ]
    
    results = extractor.test_extraction(test_files)
    return results

if __name__ == "__main__":
    test_version_extractor()