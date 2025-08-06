# app/src/naming/project_parser.py
"""
Project Information Parsing Module

Handles parsing of project information from folder names and filenames
using multiple pattern matching strategies.
"""

import re
from .text_utils import TextUtils

class ProjectParser:
    """Parses project information from various folder name and filename formats"""
    
    def __init__(self):
        self.text_utils = TextUtils()
        
        # Define parsing patterns in priority order
        self.patterns = [
            {
                'name': 'Standard OO with letter',
                'regex': r'OO_(.*?)_AD_([A-Z]+)-(\d+).*?([A-Z])_\d+\.mp4',
                'description': 'OO_[PROJECT]_AD_[TYPE]-[NUMBER]_[LETTER]_XXX.mp4',
                'groups': ['project', 'ad_type', 'test_name', 'version_letter']
            },
            {
                'name': 'Standard OO without extension',
                'regex': r'OO_(.*?)_AD_([A-Z]+)-(\d+).*?([A-Z])_\d+',
                'description': 'OO_[PROJECT]_AD_[TYPE]-[NUMBER]_[LETTER]_XXX',
                'groups': ['project', 'ad_type', 'test_name', 'version_letter']
            },
            {
                'name': 'AD-It format with letter',
                'regex': r'OO_(.*?)_AD-It_([A-Z]+)-(\d+).*?([A-Z])_?\d*',
                'description': 'OO_[PROJECT]_AD-It_[TYPE]-[NUMBER]_[LETTER]',
                'groups': ['project', 'ad_type', 'test_name', 'version_letter']
            },
            {
                'name': 'AD-It format without letter',
                'regex': r'OO_(.*?)_AD-It_([A-Z]+)-(\d+)',
                'description': 'OO_[PROJECT]_AD-It_[TYPE]-[NUMBER]',
                'groups': ['project', 'ad_type', 'test_name']
            },
            {
                'name': 'Modern OPT format',
                'regex': r'([A-Z0-9_]+)_([A-Z0-9]+)_(.*?)_OPT_([A-Z]+)-(\d+).*?([A-Z])',
                'description': '[COMPANY]_[PREFIX]_[PROJECT]_OPT_[TYPE]-[NUMBER]_[LETTER]',
                'groups': ['company', 'prefix', 'project', 'ad_type', 'test_name', 'version_letter']
            },
            {
                'name': 'GH prefix format',
                'regex': r'GH\s+OO_(.*?)_AD[_-](?:It_)?([A-Z]+)-(\d+)',
                'description': 'GH OO_[PROJECT]_AD_[TYPE]-[NUMBER]',
                'groups': ['project', 'ad_type', 'test_name']
            }
        ]
    
    def parse_project_info(self, folder_name):
        """
        Parse project information from folder name
        
        Args:
            folder_name (str): Folder name to parse
            
        Returns:
            dict: Parsed project information or None if parsing fails
        """
        print(f"🔍 PARSING PROJECT INFO FROM: '{folder_name}'")
        
        # Try each pattern in order
        for i, pattern_info in enumerate(self.patterns):
            pattern = pattern_info['regex']
            name = pattern_info['name']
            groups = pattern_info['groups']
            
            match = re.search(pattern, folder_name)
            if match:
                groups_found = match.groups()
                print(f"✅ PATTERN {i+1} MATCH ({name}): Found {len(groups_found)} groups: {groups_found}")
                
                result = self._process_pattern_match(i, groups_found, groups)
                if result:
                    print(f"🎯 EXTRACTED: '{result['project_name']}' (Type: {result['ad_type']}, Test: {result['test_name']}, Letter: {result.get('version_letter', 'N/A')})")
                    return result
                else:
                    print(f"❌ PATTERN {i+1} PROCESSING FAILED")
            else:
                print(f"❌ PATTERN {i+1} NO MATCH ({name})")
        
        # If no patterns matched, try manual extraction
        print(f"🔄 NO PATTERNS MATCHED - Attempting manual extraction...")
        manual_result = self._manual_extraction(folder_name)
        if manual_result:
            return manual_result
        
        print(f"❌ FAILED TO PARSE: '{folder_name}'")
        return None
    
    def _process_pattern_match(self, pattern_index, groups, group_names):
        """Process a successful pattern match into project info"""
        
        try:
            if pattern_index in [0, 1]:  # Standard OO patterns
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
                
                project_name = self.text_utils.clean_project_name(raw_project_name)
                
            elif pattern_index in [2, 3]:  # AD-It patterns
                raw_project_name = groups[0]
                ad_type = groups[1]
                test_name = groups[2]
                version_letter = groups[3] if len(groups) > 3 else ""
                project_name = self.text_utils.clean_project_name(raw_project_name)
                
            elif pattern_index == 4:  # Modern OPT format
                if len(groups) >= 6:
                    company = groups[0]
                    prefix = groups[1]
                    raw_project_name = groups[2]
                    ad_type = groups[3]
                    test_name = groups[4]
                    version_letter = groups[5]
                    combined_name = f"{company} {raw_project_name}".replace('_', ' ')
                    project_name = self.text_utils.clean_project_name(combined_name)
                else:
                    raw_project_name = groups[2]
                    ad_type = groups[3]
                    test_name = groups[4]
                    version_letter = ""
                    project_name = self.text_utils.clean_project_name(raw_project_name)
                    
            elif pattern_index == 5:  # GH format
                raw_project_name = groups[0]
                ad_type = groups[1]
                test_name = groups[2]
                version_letter = ""
                project_name = self.text_utils.clean_project_name(raw_project_name)
            
            # Extract version letter if not found and available in filename
            if not version_letter:
                version_letter_match = re.search(r'_(\d+)([A-Z])_?\d*', folder_name)
                version_letter = version_letter_match.group(2) if version_letter_match else ""
            
            return {
                "project_name": project_name,
                "ad_type": ad_type,
                "test_name": test_name,
                "version_letter": version_letter
            }
            
        except (IndexError, AttributeError) as e:
            print(f"❌ ERROR processing pattern {pattern_index}: {e}")
            return None
    
    def _manual_extraction(self, folder_name):
        """Manual fallback extraction for any account prefix"""
        
        # Look for ad type and test number
        ad_type_match = re.search(r'(VTD|STOR|ACT)', folder_name)
        test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', folder_name)
        version_letter_match = re.search(r'_(\d+)([A-Z])_?\d*', folder_name)
        
        if not ad_type_match or not test_name_match:
            print(f"❌ MANUAL EXTRACTION FAILED: No ad type or test number found")
            return None
        
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
                        project_name = self.text_utils.clean_project_name(raw_project_name)
                        version_letter = version_letter_match.group(2) if version_letter_match else ""
                        
                        print(f"✅ MANUAL EXTRACTION SUCCESS: '{raw_project_name}' -> '{project_name}' (Letter: {version_letter})")
                        
                        return {
                            "project_name": project_name,
                            "ad_type": ad_type_match.group(1),
                            "test_name": test_name_match.group(1),
                            "version_letter": version_letter
                        }
        
        print(f"❌ MANUAL EXTRACTION FAILED: No valid project pattern found")
        return None
    
    def get_pattern_info(self):
        """Get information about available parsing patterns"""
        return self.patterns.copy()
    
    def test_parsing(self, test_cases):
        """
        Test project parsing on multiple cases
        
        Args:
            test_cases (list): List of (folder_name, expected_result) tuples
            
        Returns:
            dict: Test results
        """
        results = {
            'total': len(test_cases),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        print("🧪 TESTING PROJECT INFO PARSING:")
        print("=" * 60)
        
        for folder_name, expected in test_cases:
            print(f"\n📁 Testing: '{folder_name}'")
            if expected:
                print(f"📄 Expected: Project='{expected.get('project_name')}', Type='{expected.get('ad_type')}', Test='{expected.get('test_name')}'")
            
            result = self.parse_project_info(folder_name)
            
            if result and expected:
                # Compare key fields
                project_match = result.get('project_name') == expected.get('project_name')
                type_match = result.get('ad_type') == expected.get('ad_type')
                test_match = result.get('test_name') == expected.get('test_name')
                
                if project_match and type_match and test_match:
                    status = "✅ PASS"
                    results['passed'] += 1
                else:
                    status = "❌ FAIL"
                    results['failed'] += 1
            elif not result and not expected:
                status = "✅ PASS (Expected failure)"
                results['passed'] += 1
            else:
                status = "❌ FAIL"
                results['failed'] += 1
            
            results['details'].append({
                'folder_name': folder_name,
                'expected': expected,
                'result': result,
                'status': status
            })
            
            print(f"🎯 Status: {status}")
        
        print(f"\n📊 SUMMARY: {results['passed']}/{results['total']} passed")
        return results

# Test function for standalone usage
def test_project_parser():
    """Test the project parser with common folder patterns"""
    
    parser = ProjectParser()
    
    test_cases = [
        (
            "TR FB - New Ads from GH AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416",
            {"project_name": "AGMD Dinner Mashup", "ad_type": "STOR", "test_name": "3133"}
        ),
        (
            "OO_GroceryOils_AD_VTD-1234A_001.mp4",
            {"project_name": "Grocery Oils", "ad_type": "VTD", "test_name": "1234"}
        ),
        (
            "MCT_CookingOil_AD_STOR-5678B.mp4",
            {"project_name": "Cooking Oil", "ad_type": "STOR", "test_name": "5678"}
        ),
        (
            "Invalid_Folder_Name",
            None  # Should fail
        )
    ]
    
    results = parser.test_parsing(test_cases)
    return results

if __name__ == "__main__":
    test_project_parser()