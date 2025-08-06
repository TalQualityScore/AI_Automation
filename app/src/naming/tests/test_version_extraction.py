# app/src/naming/tests/test_version_extraction.py
"""
Unit tests for version letter extraction functionality

Tests the VersionExtractor class with various filename patterns
to ensure correct extraction of A, B, C, D version letters.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from version_extractor import VersionExtractor

class TestVersionExtraction(unittest.TestCase):
    """Test cases for version letter extraction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = VersionExtractor()
    
    def test_250416_format_extraction(self):
        """Test extraction from _250416D format (your specific case)"""
        test_cases = [
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4", "D"),
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416C.mp4", "C"),
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416B.mp4", "B"),
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416A.mp4", "A"),
            ("GMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4", "D"),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.extractor.extract_version_letter(filename, debug=False)
                self.assertEqual(result, expected, 
                    f"Expected '{expected}' for {filename}, got '{result}'")
    
    def test_long_date_format_extraction(self):
        """Test extraction from _20240408A format"""
        test_cases = [
            ("TestFile_20240408A.mp4", "A"),
            ("TestFile_20240408B.mov", "B"),
            ("TestFile_20240408C", "C"),
            ("TestFile_20240408D_001.mp4", "D"),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.extractor.extract_version_letter(filename, debug=False)
                self.assertEqual(result, expected,
                    f"Expected '{expected}' for {filename}, got '{result}'")
    
    def test_test_number_format_extraction(self):
        """Test extraction from STOR-3133D format"""
        test_cases = [
            ("OO_GroceryOils_AD_VTD-1234A_001.mp4", "A"),
            ("MCT_CookingOil_AD_STOR-5678B.mp4", "B"),
            ("TestProject_ACT-9999C.mov", "C"),
            ("Sample_VTD-1111D", "D"),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.extractor.extract_version_letter(filename, debug=False)
                self.assertEqual(result, expected,
                    f"Expected '{expected}' for {filename}, got '{result}'")
    
    def test_number_letter_format_extraction(self):
        """Test extraction from general NumberLetter format"""
        test_cases = [
            ("TestFile_1234A.mp4", "A"),
            ("Project_999B.mov", "B"),
            ("Sample_456C", "C"),
            ("Demo_789D_final.mp4", "D"),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.extractor.extract_version_letter(filename, debug=False)
                self.assertEqual(result, expected,
                    f"Expected '{expected}' for {filename}, got '{result}'")
    
    def test_no_version_letter_found(self):
        """Test files with no version letters"""
        test_cases = [
            "TestFile_NoLetter.mp4",
            "Project_Without_Version.mov",
            "Sample_123.mp4",  # Number but no letter
            "Demo_File.mov",
            "STOR-1234.mp4",  # Test number but no letter
        ]
        
        for filename in test_cases:
            with self.subTest(filename=filename):
                result = self.extractor.extract_version_letter(filename, debug=False)
                self.assertEqual(result, "",
                    f"Expected empty string for {filename}, got '{result}'")
    
    def test_invalid_version_letters(self):
        """Test files with invalid version letters (not A, B, C, D)"""
        test_cases = [
            "TestFile_250416E.mp4",  # E is not valid
            "Project_250416Z.mov",   # Z is not valid
            "Sample_250416X.mp4",    # X is not valid
        ]
        
        for filename in test_cases:
            with self.subTest(filename=filename):
                result = self.extractor.extract_version_letter(filename, debug=False)
                self.assertEqual(result, "",
                    f"Expected empty string for invalid letter in {filename}, got '{result}'")
    
    def test_pattern_priority_order(self):
        """Test that patterns are matched in correct priority order"""
        # This file has multiple potential matches - should use the first one
        filename = "Test_250416D_VTD-1234A.mp4"
        result = self.extractor.extract_version_letter(filename, debug=False)
        self.assertEqual(result, "D",
            "Should extract 'D' from _250416D pattern (higher priority) not 'A' from VTD-1234A")
    
    def test_copy_prefix_removal(self):
        """Test that 'Copy of OO_' prefix is properly removed"""
        test_cases = [
            ("Copy of OO_TestFile_250416A.mp4", "A"),
            ("Copy of OO_Project_VTD-1234B.mov", "B"),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.extractor.extract_version_letter(filename, debug=False)
                self.assertEqual(result, expected,
                    f"Expected '{expected}' for {filename}, got '{result}'")
    
    def test_validation_function(self):
        """Test the version letter validation function"""
        valid_letters = ['A', 'B', 'C', 'D']
        invalid_letters = ['E', 'Z', 'X', '1', '', None]
        
        for letter in valid_letters:
            with self.subTest(letter=letter):
                self.assertTrue(self.extractor.validate_version_letter(letter),
                    f"Letter '{letter}' should be valid")
        
        for letter in invalid_letters:
            with self.subTest(letter=letter):
                self.assertFalse(self.extractor.validate_version_letter(letter),
                    f"Letter '{letter}' should be invalid")
    
    def test_get_pattern_info(self):
        """Test that pattern information is available"""
        patterns = self.extractor.get_extraction_info()
        
        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 0, "Should have at least one pattern")
        
        for pattern in patterns:
            self.assertIn('name', pattern, "Each pattern should have a name")
            self.assertIn('regex', pattern, "Each pattern should have a regex")
            self.assertIn('description', pattern, "Each pattern should have a description")
    
    def test_edge_cases(self):
        """Test edge cases and unusual inputs"""
        edge_cases = [
            ("", ""),  # Empty string
            ("A", ""),  # Single character
            ("TestFile.mp4", ""),  # No pattern match
            ("250416D", "D"),  # No underscore prefix
            ("_250416D_", "D"),  # Extra underscore suffix
            ("multiple_250416A_and_VTD-1234B.mp4", "A"),  # Multiple patterns, should get first
        ]
        
        for filename, expected in edge_cases:
            with self.subTest(filename=filename):
                result = self.extractor.extract_version_letter(filename, debug=False)
                self.assertEqual(result, expected,
                    f"Expected '{expected}' for edge case {filename}, got '{result}'")

class TestVersionExtractionIntegration(unittest.TestCase):
    """Integration tests for version extraction with real-world scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = VersionExtractor()
    
    def test_your_specific_problem_files(self):
        """Test the specific files mentioned in your problem report"""
        # These are the exact files you mentioned having issues with
        problem_files = [
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4", "D"),
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416C.mp4", "C"),
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416B.mp4", "B"),
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416A.mp4", "A"),
        ]
        
        for filename, expected in problem_files:
            with self.subTest(filename=filename):
                result = self.extractor.extract_version_letter(filename, debug=True)
                self.assertEqual(result, expected,
                    f"CRITICAL: Expected '{expected}' for {filename}, got '{result}' - this was the original problem!")
    
    def test_bulk_extraction(self):
        """Test extraction on a large batch of files"""
        test_files = [
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4", "D"),
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416C.mp4", "C"),
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416B.mp4", "B"),
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416A.mp4", "A"),
            ("GMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4", "D"),
            ("OO_GroceryOils_AD_VTD-1234A_001.mp4", "A"),
            ("MCT_CookingOil_AD_STOR-5678B.mp4", "B"),
            ("TestFile_NoLetter.mp4", "")
        ]
        
        results = self.extractor.test_extraction(test_files)
        
        # Should have high success rate
        success_rate = results['passed'] / results['total']
        self.assertGreaterEqual(success_rate, 0.8,
            f"Success rate should be at least 80%, got {success_rate:.1%}")

def run_version_extraction_tests():
    """Run all version extraction tests"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestVersionExtraction))
    suite.addTest(unittest.makeSuite(TestVersionExtractionIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == '__main__':
    print("🧪 RUNNING VERSION EXTRACTION TESTS")
    print("=" * 60)
    
    result = run_version_extraction_tests()
    
    if result.wasSuccessful():
        print("\n✅ ALL VERSION EXTRACTION TESTS PASSED!")
    else:
        print(f"\n❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")