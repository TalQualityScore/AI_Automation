# app/src/naming/tests/test_project_parsing.py
"""
Unit tests for project information parsing functionality

Tests the ProjectParser class with various folder name patterns
to ensure correct extraction of project names, ad types, and test numbers.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_parser import ProjectParser

class TestProjectParsing(unittest.TestCase):
    """Test cases for project information parsing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = ProjectParser()
    
    def test_standard_oo_format_parsing(self):
        """Test parsing of standard OO_[PROJECT]_AD_[TYPE]-[NUMBER] format"""
        test_cases = [
            {
                'input': 'OO_GroceryOils_AD_VTD-1234A_001.mp4',
                'expected': {
                    'project_name': 'Grocery Oils',
                    'ad_type': 'VTD',
                    'test_name': '1234',
                    'version_letter': 'A'
                }
            },
            {
                'input': 'OO_CookingRecipes_AD_STOR-5678B.mp4',
                'expected': {
                    'project_name': 'Cooking Recipes',
                    'ad_type': 'STOR',
                    'test_name': '5678',
                    'version_letter': 'B'
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                result = self.parser.parse_project_info(case['input'])
                self.assertIsNotNone(result, f"Should parse {case['input']}")
                
                expected = case['expected']
                self.assertEqual(result['project_name'], expected['project_name'])
                self.assertEqual(result['ad_type'], expected['ad_type'])
                self.assertEqual(result['test_name'], expected['test_name'])
    
    def test_ad_it_format_parsing(self):
        """Test parsing of OO_[PROJECT]_AD-It_[TYPE]-[NUMBER] format"""
        test_cases = [
            {
                'input': 'OO_HealthyMeals_AD-It_ACT-9999C_final.mp4',
                'expected': {
                    'project_name': 'Healthy Meals',
                    'ad_type': 'ACT',
                    'test_name': '9999'
                }
            },
            {
                'input': 'OO_KitchenTips_AD-It_VTD-1111D',
                'expected': {
                    'project_name': 'Kitchen Tips',
                    'ad_type': 'VTD',
                    'test_name': '1111'
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                result = self.parser.parse_project_info(case['input'])
                self.assertIsNotNone(result, f"Should parse {case['input']}")
                
                expected = case['expected']
                self.assertEqual(result['project_name'], expected['project_name'])
                self.assertEqual(result['ad_type'], expected['ad_type'])
                self.assertEqual(result['test_name'], expected['test_name'])
    
    def test_modern_opt_format_parsing(self):
        """Test parsing of [COMPANY]_[PREFIX]_[PROJECT]_OPT_[TYPE]-[NUMBER] format"""
        test_cases = [
            {
                'input': 'AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4',
                'expected': {
                    'project_name': 'AGMD Dinner Mashup',
                    'ad_type': 'STOR',
                    'test_name': '3133',
                    'version_letter': 'D'
                }
            },
            {
                'input': 'GMD_PP_Healthy_Living_OPT_VTD-2222_250416A.mp4',
                'expected': {
                    'project_name': 'GMD Healthy Living',
                    'ad_type': 'VTD',
                    'test_name': '2222',
                    'version_letter': 'A'
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                result = self.parser.parse_project_info(case['input'])
                self.assertIsNotNone(result, f"Should parse {case['input']}")
                
                expected = case['expected']
                self.assertEqual(result['project_name'], expected['project_name'])
                self.assertEqual(result['ad_type'], expected['ad_type'])
                self.assertEqual(result['test_name'], expected['test_name'])
    
    def test_gh_prefix_format_parsing(self):
        """Test parsing of GH OO_[PROJECT]_AD_[TYPE]-[NUMBER] format"""
        test_cases = [
            {
                'input': 'GH OO_FitnessRoutine_AD_ACT-8888',
                'expected': {
                    'project_name': 'Fitness Routine',
                    'ad_type': 'ACT',
                    'test_name': '8888'
                }
            },
            {
                'input': 'GH OO_WellnessTips_AD-It_STOR-7777',
                'expected': {
                    'project_name': 'Wellness Tips',
                    'ad_type': 'STOR',
                    'test_name': '7777'
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                result = self.parser.parse_project_info(case['input'])
                self.assertIsNotNone(result, f"Should parse {case['input']}")
                
                expected = case['expected']
                self.assertEqual(result['project_name'], expected['project_name'])
                self.assertEqual(result['ad_type'], expected['ad_type'])
                self.assertEqual(result['test_name'], expected['test_name'])
    
    def test_manual_extraction_fallback(self):
        """Test manual extraction for non-standard formats"""
        test_cases = [
            {
                'input': 'MCT_CookingOil_AD_STOR-5678B.mp4',
                'expected': {
                    'project_name': 'Cooking Oil',
                    'ad_type': 'STOR',
                    'test_name': '5678'
                }
            },
            {
                'input': 'TR_HealthSupplements_VTD-1234A',
                'expected': {
                    'project_name': 'Health Supplements',
                    'ad_type': 'VTD',
                    'test_name': '1234'
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                result = self.parser.parse_project_info(case['input'])
                self.assertIsNotNone(result, f"Should parse {case['input']} with manual extraction")
                
                expected = case['expected']
                self.assertEqual(result['ad_type'], expected['ad_type'])
                self.assertEqual(result['test_name'], expected['test_name'])
    
    def test_parsing_failures(self):
        """Test cases that should fail to parse"""
        invalid_cases = [
            "Invalid_Folder_Name",
            "No_Ad_Type_Here",
            "Missing-Test-Number",
            "",
            "Just_Text_No_Patterns"
        ]
        
        for case in invalid_cases:
            with self.subTest(input=case):
                result = self.parser.parse_project_info(case)
                self.assertIsNone(result, f"Should not parse invalid case: {case}")
    
    def test_project_name_cleaning(self):
        """Test that project names are properly cleaned"""
        test_cases = [
            {
                'input': 'OO_CookingOil+Recipe_AD_VTD-1234A.mp4',
                'expected_project_contains': 'Cooking Oil Recipe'
            },
            {
                'input': 'OO_UGC_Content_AD_STOR-5678B.mp4',
                'expected_project_contains': 'UGC Content'
            },
            {
                'input': 'OO_grocery_store_oils_AD_ACT-9999C.mp4',
                'expected_project_contains': 'Grocery Store Oils'
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                result = self.parser.parse_project_info(case['input'])
                self.assertIsNotNone(result, f"Should parse {case['input']}")
                
                project_name = result['project_name']
                expected_text = case['expected_project_contains']
                self.assertIn(expected_text, project_name,
                    f"Project name '{project_name}' should contain '{expected_text}'")
    
    def test_version_letter_extraction(self):
        """Test version letter extraction in project parsing"""
        test_cases = [
            {
                'input': 'OO_TestProject_AD_VTD-1234A_001.mp4',
                'expected_letter': 'A'
            },
            {
                'input': 'AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4',
                'expected_letter': 'D'
            },
            {
                'input': 'OO_NoLetter_AD_STOR-5678.mp4',
                'expected_letter': ''
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                result = self.parser.parse_project_info(case['input'])
                self.assertIsNotNone(result, f"Should parse {case['input']}")
                
                version_letter = result.get('version_letter', '')
                expected_letter = case['expected_letter']
                self.assertEqual(version_letter, expected_letter,
                    f"Expected version letter '{expected_letter}', got '{version_letter}'")
    
    def test_get_pattern_info(self):
        """Test that pattern information is available"""
        patterns = self.parser.get_pattern_info()
        
        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 0, "Should have at least one pattern")
        
        for pattern in patterns:
            self.assertIn('name', pattern, "Each pattern should have a name")
            self.assertIn('regex', pattern, "Each pattern should have a regex")
            self.assertIn('groups', pattern, "Each pattern should have groups")

class TestProjectParsingIntegration(unittest.TestCase):
    """Integration tests for project parsing with real-world scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = ProjectParser()
    
    def test_trello_card_examples(self):
        """Test parsing of examples from actual Trello card names"""
        # These are based on the patterns mentioned in your conversation
        trello_examples = [
            {
                'input': 'TR FB - New Ads from GH AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416',
                'expected': {
                    'project_name': 'AGMD Dinner Mashup',
                    'ad_type': 'STOR',
                    'test_name': '3133'
                }
            },
            {
                'input': 'BC3 YT - New project from OO_GroceryOils_AD_VTD-1234A_001',
                'expected': {
                    'project_name': 'Grocery Oils',
                    'ad_type': 'VTD',
                    'test_name': '1234'
                }
            }
        ]
        
        for case in trello_examples:
            with self.subTest(input=case['input']):
                result = self.parser.parse_project_info(case['input'])
                self.assertIsNotNone(result, f"Should parse Trello example: {case['input']}")
                
                expected = case['expected']
                self.assertEqual(result['ad_type'], expected['ad_type'])
                self.assertEqual(result['test_name'], expected['test_name'])
    
    def test_bulk_parsing_performance(self):
        """Test parsing performance on a large batch"""
        test_files = [
            "AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4",
            "OO_GroceryOils_AD_VTD-1234A_001.mp4",
            "MCT_CookingOil_AD_STOR-5678B.mp4",
            "OO_HealthyRecipes_AD-It_ACT-9999C.mp4",
            "GH OO_FitnessRoutine_AD_VTD-8888.mp4",
            "TR_Supplements_STOR-7777A.mp4",
            "Invalid_File_Name.mp4",
            "Another_Invalid_Name.mp4"
        ]
        
        results = {
            'parsed': 0,
            'failed': 0,
            'total': len(test_files)
        }
        
        for filename in test_files:
            result = self.parser.parse_project_info(filename)
            if result:
                results['parsed'] += 1
            else:
                results['failed'] += 1
        
        # Should parse most valid files
        parse_rate = results['parsed'] / results['total']
        self.assertGreaterEqual(parse_rate, 0.6,
            f"Parse rate should be at least 60%, got {parse_rate:.1%}")
    
    def test_edge_case_handling(self):
        """Test edge cases and unusual inputs"""
        edge_cases = [
            "",  # Empty string
            "A",  # Single character
            "Normal_File.mp4",  # Normal filename with no patterns
            "VTD-1234",  # Just test pattern, no project
            "STOR-5678_NoProject.mp4",  # Test pattern but no clear project
            "Project_With_No_Numbers.mp4",  # No test numbers
        ]
        
        for case in edge_cases:
            with self.subTest(input=case):
                # Should not crash, even on edge cases
                try:
                    result = self.parser.parse_project_info(case)
                    # Result can be None, that's fine for edge cases
                except Exception as e:
                    self.fail(f"Should not raise exception for edge case '{case}': {e}")

def run_project_parsing_tests():
    """Run all project parsing tests"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestProjectParsing))
    suite.addTest(unittest.makeSuite(TestProjectParsingIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == '__main__':
    print("🧪 RUNNING PROJECT PARSING TESTS")
    print("=" * 60)
    
    result = run_project_parsing_tests()
    
    if result.wasSuccessful():
        print("\n✅ ALL PROJECT PARSING TESTS PASSED!")
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