# app/src/naming/tests/test_name_generation.py
"""
Unit tests for name generation functionality

Tests the NameGenerator class for generating output filenames
and project folder names with correct formatting.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from name_generator import NameGenerator

class TestNameGeneration(unittest.TestCase):
    """Test cases for name generation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = NameGenerator()
    
    def test_output_name_generation_with_version_letter(self):
        """Test output name generation when version letter is provided"""
        test_cases = [
            {
                'project_name': 'AGMD Dinner Mashup',
                'video_file': 'AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4',
                'ad_type_selection': 'Quiz',
                'image_desc': 'dinner',
                'version_num': 1,
                'version_letter': 'D',
                'expected_components': {
                    'project_part': 'agmddinnermashup',
                    'ad_type': 'STOR',
                    'test_letter': '3133D',
                    'ad_selection': 'Quiz'
                }
            },
            {
                'project_name': 'Grocery Store Oils',
                'video_file': 'OO_GroceryOils_AD_VTD-1234A_001.mp4',
                'ad_type_selection': 'Quiz',
                'image_desc': 'grocery',
                'version_num': 2,
                'version_letter': 'A',
                'expected_components': {
                    'project_part': 'grocerystoreoils',
                    'ad_type': 'VTD',
                    'test_letter': '1234A',
                    'ad_selection': 'Quiz'
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(project=case['project_name']):
                result = self.generator.generate_output_name(
                    case['project_name'],
                    case['video_file'],
                    case['ad_type_selection'],
                    case['image_desc'],
                    case['version_num'],
                    case['version_letter']
                )
                
                # Check that all expected components are in the result
                expected = case['expected_components']
                self.assertIn(expected['project_part'], result.lower())
                self.assertIn(expected['ad_type'], result)
                self.assertIn(expected['test_letter'], result)
                self.assertIn(expected['ad_selection'], result)
                
                # Check version number format
                version_part = f"v{case['version_num']:02d}"
                self.assertIn(version_part, result)
    
    def test_output_name_generation_extract_version(self):
        """Test output name generation when version letter must be extracted"""
        test_cases = [
            {
                'project_name': 'Test Project',
                'video_file': 'TestFile_250416D.mp4',
                'ad_type_selection': 'Quiz',
                'image_desc': 'test',
                'version_num': 1,
                'expected_letter': 'D'
            },
            {
                'project_name': 'Another Project',
                'video_file': 'AnotherFile_VTD-1234A.mp4',
                'ad_type_selection': 'Quiz',
                'image_desc': 'test',
                'version_num': 1,
                'expected_letter': 'A'
            }
        ]
        
        for case in test_cases:
            with self.subTest(video_file=case['video_file']):
                result = self.generator.generate_output_name(
                    case['project_name'],
                    case['video_file'],
                    case['ad_type_selection'],
                    case['image_desc'],
                    case['version_num'],
                    ""  # No version letter provided, should extract
                )
                
                # Should contain the extracted version letter
                expected_letter = case['expected_letter']
                self.assertIn(expected_letter, result,
                    f"Result should contain extracted version letter '{expected_letter}'")
    
    def test_output_name_fallback_version(self):
        """Test output name generation when no version letter can be extracted"""
        result = self.generator.generate_output_name(
            'Test Project',
            'NoVersionLetter.mp4',
            'Quiz',
            'test',
            1,
            ""  # No version letter provided
        )
        
        # Should fall back to "ZZ"
        self.assertIn('ZZ', result, "Should contain 'ZZ' fallback when no version letter found")
    
    def test_project_folder_name_generation(self):
        """Test project folder name generation"""
        test_cases = [
            {
                'project_name': 'AGMD Dinner Mashup',
                'video_file': 'AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4',
                'ad_type_selection': 'Quiz',
                'expected_components': ['GH', 'AGMD Dinner Mashup', 'STOR', '3133', 'Quiz']
            },
            {
                'project_name': 'Grocery Store Oils',
                'video_file': 'OO_GroceryOils_AD_VTD-1234A_001.mp4',
                'ad_type_selection': 'Connector',
                'expected_components': ['GH', 'Grocery Store Oils', 'VTD', '1234', 'Connector']
            }
        ]
        
        for case in test_cases:
            with self.subTest(project=case['project_name']):
                result = self.generator.generate_project_folder_name(
                    case['project_name'],
                    case['video_file'],
                    case['ad_type_selection']
                )
                
                # Check that all expected components are in the result
                for component in case['expected_components']:
                    self.assertIn(component, result,
                        f"Folder name should contain '{component}'")
    
    def test_ad_type_extraction(self):
        """Test ad type extraction from filenames"""
        test_cases = [
            ('TestFile_VTD-1234.mp4', 'VTD'),
            ('TestFile_STOR-5678.mp4', 'STOR'),
            ('TestFile_ACT-9999.mp4', 'ACT'),
            ('NoAdType.mp4', ''),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.generator._extract_ad_type(filename)
                self.assertEqual(result, expected,
                    f"Expected ad type '{expected}' for {filename}, got '{result}'")
    
    def test_test_number_extraction(self):
        """Test test number extraction from filenames"""
        test_cases = [
            ('TestFile_VTD-1234.mp4', '1234'),
            ('TestFile_STOR-5678.mp4', '5678'),
            ('TestFile_ACT-9999.mp4', '9999'),
            ('NoTestNumber.mp4', ''),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.generator._extract_test_number(filename)
                self.assertEqual(result, expected,
                    f"Expected test number '{expected}' for {filename}, got '{result}'")
    
    def test_name_component_validation(self):
        """Test validation of name components"""
        # Valid components
        valid_cases = [
            ('Valid Project', 'VTD', '1234'),
            ('Another Project', 'STOR', '5678'),
            ('Test Project', 'ACT', '9999')
        ]
        
        for project_name, ad_type, test_name in valid_cases:
            with self.subTest(project=project_name, ad_type=ad_type, test=test_name):
                is_valid, error = self.generator.validate_name_components(project_name, ad_type, test_name)
                self.assertTrue(is_valid, f"Should be valid: {error}")
        
        # Invalid components
        invalid_cases = [
            ('', 'VTD', '1234', 'Project name is required'),
            ('Valid Project', 'INVALID', '1234', 'Invalid ad type'),
            ('Valid Project', 'VTD', 'abc', 'Invalid test name'),
            ('Valid Project', 'VTD', '', 'Invalid test name'),
        ]
        
        for project_name, ad_type, test_name, expected_error in invalid_cases:
            with self.subTest(project=project_name, ad_type=ad_type, test=test_name):
                is_valid, error = self.generator.validate_name_components(project_name, ad_type, test_name)
                self.assertFalse(is_valid, f"Should be invalid")
                self.assertIn(expected_error.split()[0].lower(), error.lower(),
                    f"Error should mention '{expected_error}'")
    
    def test_output_name_format_consistency(self):
        """Test that output names follow consistent format"""
        result = self.generator.generate_output_name(
            'Test Project',
            'TestFile_STOR-1234A.mp4',
            'Quiz',
            'test',
            1,
            'A'
        )
        
        # Should follow format: GH-[project][adtype][test][letter]ZZ[selection]_[desc]-v[num]-m01-f00-c00
        self.assertTrue(result.startswith('GH-'), "Should start with 'GH-'")
        self.assertIn('STOR', result, "Should contain ad type")
        self.assertIn('1234A', result, "Should contain test number and version letter")
        self.assertIn('ZZQuiz', result, "Should contain 'ZZQuiz'")
        self.assertIn('test-v01', result, "Should contain description and version")
        self.assertIn('m01-f00-c00', result, "Should contain standard suffix")
    
    def test_special_characters_handling(self):
        """Test handling of special characters in project names"""
        test_cases = [
            ('Project With Spaces', 'projectwithspaces'),
            ('Project-With-Dashes', 'projectwithdashes'),
            ('Project_With_Underscores', 'projectwithunderscores'),
            ('Project+With+Plus', 'projectwithplus'),
            ('ProjectWithÁccénts', 'projectwithaccents'),  # Should handle unidecode
        ]
        
        for project_name, expected_part in test_cases:
            with self.subTest(project=project_name):
                result = self.generator.generate_output_name(
                    project_name,
                    'TestFile_STOR-1234A.mp4',
                    'Quiz',
                    'test',
                    1,
                    'A'
                )
                
                self.assertIn(expected_part, result.lower(),
                    f"Should contain cleaned project part '{expected_part}'")

class TestNameGenerationIntegration(unittest.TestCase):
    """Integration tests for name generation with real-world scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = NameGenerator()
    
    def test_your_specific_problem_scenario(self):
        """Test the specific scenario mentioned in your problem report"""
        # This should now correctly extract 'D' instead of showing 'S'
        result = self.generator.generate_output_name(
            'AGMD Dinner Mashup',
            'AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4',
            'Quiz',
            'dinner',
            1,
            ""  # Let it extract the version letter
        )
        
        # Critical test: should contain "3133D" not "3133S"
        self.assertIn('3133D', result,
            f"CRITICAL: Should contain '3133D' not '3133S'. Got: {result}")
        self.assertNotIn('3133S', result,
            f"CRITICAL: Should NOT contain '3133S'. Got: {result}")
    
    def test_bulk_name_generation(self):
        """Test name generation on a batch of files"""
        test_files = [
            {
                'project': 'AGMD Dinner Mashup',
                'file': 'AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4',
                'expected_test_letter': '3133D'
            },
            {
                'project': 'Grocery Store Oils',
                'file': 'OO_GroceryOils_AD_VTD-1234A_001.mp4',
                'expected_test_letter': '1234A'
            },
            {
                'project': 'Cooking Oil UGC',
                'file': 'MCT_CookingOil_AD_STOR-5678B.mp4',
                'expected_test_letter': '5678B'
            }
        ]
        
        for case in test_files:
            with self.subTest(project=case['project']):
                result = self.generator.generate_output_name(
                    case['project'],
                    case['file'],
                    'Quiz',
                    'test',
                    1,
                    ""  # Extract version letter
                )
                
                expected = case['expected_test_letter']
                self.assertIn(expected, result,
                    f"Should contain '{expected}' in result: {result}")
    
    def test_edge_cases_integration(self):
        """Test edge cases in full integration"""
        edge_cases = [
            {
                'name': 'Empty project name handling',
                'project': '',
                'file': 'TestFile_STOR-1234A.mp4',
                'should_not_crash': True
            },
            {
                'name': 'No ad type in file',
                'project': 'Test Project',
                'file': 'NoAdType.mp4',
                'should_not_crash': True
            },
            {
                'name': 'No test number in file',
                'project': 'Test Project',
                'file': 'NoTestNumber_STOR.mp4',
                'should_not_crash': True
            }
        ]
        
        for case in edge_cases:
            with self.subTest(name=case['name']):
                try:
                    result = self.generator.generate_output_name(
                        case['project'],
                        case['file'],
                        'Quiz',
                        'test',
                        1,
                        ""
                    )
                    # Should get some result, even if not perfect
                    self.assertIsInstance(result, str, "Should return a string")
                    self.assertGreater(len(result), 0, "Should not return empty string")
                except Exception as e:
                    if case['should_not_crash']:
                        self.fail(f"Should not crash on edge case '{case['name']}': {e}")

def run_name_generation_tests():
    """Run all name generation tests"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestNameGeneration))
    suite.addTest(unittest.makeSuite(TestNameGenerationIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == '__main__':
    print("🧪 RUNNING NAME GENERATION TESTS")
    print("=" * 60)
    
    result = run_name_generation_tests()
    
    if result.wasSuccessful():
        print("\n✅ ALL NAME GENERATION TESTS PASSED!")
    else:
        print(f"\n❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}")
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}")