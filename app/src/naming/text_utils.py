# app/src/naming/text_utils.py
"""
Text Processing Utilities Module

Handles text cleaning, formatting, and standardization operations
for project names and other text content.
"""

import re

class TextUtils:
    """Utility class for text processing and cleaning operations"""
    
    def __init__(self):
        # Define common word separators and patterns
        self.separators = ['_', '-', '+', ' ']
        self.camel_case_pattern = r'([a-z])([A-Z])'
        
        # Words that should remain capitalized
        self.preserve_caps = {
            'UGC', 'API', 'UI', 'URL', 'CEO', 'CTO', 'AI', 'ML', 'SEO',
            'ROI', 'KPI', 'FAQ', 'PDF', 'CSV', 'JSON', 'XML', 'HTML',
            'CSS', 'JS', 'SQL', 'DB', 'ID', 'USA', 'UK', 'EU'
        }
        
        # Common suffixes to remove
        self.remove_suffixes = [
            r'\s+Ad$',
            r'\s+Advertisement$',
            r'\s+Video$',
            r'\s+Content$',
            r'\s+Campaign$'
        ]
        
        # Common prefixes to clean
        self.clean_prefixes = [
            'Copy of ',
            'OO_',
            'Copy of OO_',
            'Draft_',
            'Final_',
            'Test_'
        ]
    
    def clean_project_name(self, raw_name):
        """
        Clean and format project name properly
        
        Args:
            raw_name (str): Raw project name to clean
            
        Returns:
            str: Cleaned and formatted project name
        """
        if not raw_name:
            return ""
        
        print(f"🧹 CLEANING PROJECT NAME: '{raw_name}'")
        
        # Step 1: Remove common prefixes
        name = self._remove_prefixes(raw_name)
        print(f"   After prefix removal: '{name}'")
        
        # Step 2: Replace separators with spaces
        name = self._normalize_separators(name)
        print(f"   After separator normalization: '{name}'")
        
        # Step 3: Handle camelCase
        name = self._separate_camel_case(name)
        print(f"   After camelCase separation: '{name}'")
        
        # Step 4: Clean up spacing
        name = self._normalize_spacing(name)
        print(f"   After spacing normalization: '{name}'")
        
        # Step 5: Apply proper capitalization
        name = self._apply_capitalization(name)
        print(f"   After capitalization: '{name}'")
        
        # Step 6: Remove unwanted suffixes
        name = self._remove_suffixes(name)
        print(f"   After suffix removal: '{name}'")
        
        # Step 7: Final cleanup
        name = self._final_cleanup(name)
        
        print(f"🎯 FINAL CLEANED NAME: '{name}'")
        return name
    
    def _remove_prefixes(self, text):
        """Remove common prefixes from text"""
        for prefix in self.clean_prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        return text
    
    def _normalize_separators(self, text):
        """Replace various separators with spaces"""
        # Replace + with spaces first (special case)
        text = text.replace('+', ' ')
        
        # Replace other separators
        for sep in ['_', '-']:
            text = text.replace(sep, ' ')
        
        return text
    
    def _separate_camel_case(self, text):
        """Separate camelCase words"""
        words = text.split()
        separated_words = []
        
        for word in words:
            # Keep preserved words as-is
            if word.upper() in self.preserve_caps:
                separated_words.append(word.upper())
            else:
                # Separate camelCase: lowercase followed by uppercase
                separated = re.sub(self.camel_case_pattern, r'\1 \2', word)
                separated_words.append(separated)
        
        return ' '.join(separated_words)
    
    def _normalize_spacing(self, text):
        """Clean up spacing issues"""
        # Remove multiple spaces and strip
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _apply_capitalization(self, text):
        """Apply proper capitalization rules"""
        words = text.split()
        capitalized_words = []
        
        for word in words:
            # Check if it's a word to preserve in caps
            if word.upper() in self.preserve_caps:
                capitalized_words.append(word.upper())
            # Check if it's a small connector word (and not the first word)
            elif len(capitalized_words) > 0 and word.lower() in ['and', 'or', 'of', 'the', 'in', 'on', 'at', 'to', 'for']:
                capitalized_words.append(word.lower())
            else:
                # Standard title case
                capitalized_words.append(word.capitalize())
        
        return ' '.join(capitalized_words)
    
    def _remove_suffixes(self, text):
        """Remove common unwanted suffixes"""
        for suffix_pattern in self.remove_suffixes:
            text = re.sub(suffix_pattern, '', text, flags=re.IGNORECASE)
        return text
    
    def _final_cleanup(self, text):
        """Final cleanup and validation"""
        # Remove any remaining multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Ensure it's not empty
        if not text:
            text = "Untitled Project"
        
        return text
    
    def standardize_filename(self, filename):
        """
        Standardize a filename for consistent processing
        
        Args:
            filename (str): Raw filename
            
        Returns:
            str: Standardized filename
        """
        # Remove file extension for processing
        name_without_ext = filename
        extension = ""
        
        if '.' in filename:
            name_without_ext, extension = filename.rsplit('.', 1)
            extension = '.' + extension
        
        # Clean the name part
        cleaned_name = self.clean_project_name(name_without_ext)
        
        # Replace spaces with underscores for filename compatibility
        filename_safe = cleaned_name.replace(' ', '_')
        
        # Remove any characters that might cause issues in filenames
        filename_safe = re.sub(r'[<>:"/\\|?*]', '', filename_safe)
        
        return filename_safe + extension
    
    def extract_meaningful_words(self, text, min_length=3, max_words=5):
        """
        Extract meaningful words from text for keyword generation
        
        Args:
            text (str): Input text
            min_length (int): Minimum word length to consider
            max_words (int): Maximum number of words to return
            
        Returns:
            list: List of meaningful words
        """
        # Clean the text first
        cleaned = self.clean_project_name(text)
        
        # Split into words
        words = cleaned.split()
        
        # Filter out short words and common stop words
        stop_words = {'and', 'or', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by'}
        meaningful_words = []
        
        for word in words:
            if (len(word) >= min_length and 
                word.lower() not in stop_words and
                not word.isdigit()):  # Skip pure numbers
                meaningful_words.append(word.lower())
        
        return meaningful_words[:max_words]
    
    def validate_project_name(self, name):
        """
        Validate a project name for compliance with naming standards
        
        Args:
            name (str): Project name to validate
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        if not name or not name.strip():
            errors.append("Project name cannot be empty")
            return False, errors
        
        cleaned_name = name.strip()
        
        # Check length
        if len(cleaned_name) < 2:
            errors.append("Project name must be at least 2 characters long")
        elif len(cleaned_name) > 100:
            errors.append("Project name must be less than 100 characters")
        
        # Check for invalid characters in project names
        invalid_chars = '<>:"/\\|?*'
        if any(char in cleaned_name for char in invalid_chars):
            errors.append(f"Project name contains invalid characters: {invalid_chars}")
        
        # Check that it's not just numbers or special characters
        if re.match(r'^[\d\s\-_]+$', cleaned_name):
            errors.append("Project name must contain at least some letters")
        
        return len(errors) == 0, errors
    
    def test_text_cleaning(self, test_cases):
        """
        Test text cleaning on multiple cases
        
        Args:
            test_cases (list): List of (input, expected_output) tuples
            
        Returns:
            dict: Test results
        """
        results = {
            'total': len(test_cases),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        print("🧪 TESTING TEXT CLEANING:")
        print("=" * 60)
        
        for input_text, expected in test_cases:
            print(f"\n📝 Testing: '{input_text}'")
            if expected:
                print(f"📄 Expected: '{expected}'")
            
            result = self.clean_project_name(input_text)
            
            if expected:
                # Check if result matches expected (allowing for minor variations)
                matches = result.lower() == expected.lower()
                status = "✅ PASS" if matches else "❌ FAIL"
                if matches:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
            else:
                # If no expected result, just check that we got something reasonable
                is_reasonable = result and len(result) > 0 and result != input_text
                status = "✅ PASS" if is_reasonable else "❌ FAIL"
                if is_reasonable:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
            
            results['details'].append({
                'input': input_text,
                'expected': expected,
                'result': result,
                'status': status
            })
            
            print(f"🎯 Status: {status}")
        
        print(f"\n📊 SUMMARY: {results['passed']}/{results['total']} passed")
        return results

# Test function for standalone usage
def test_text_utils():
    """Test the text utilities with common formatting scenarios"""
    
    utils = TextUtils()
    
    test_cases = [
        ("CookingOil+Recipe_Test", "Cooking Oil Recipe Test"),
        ("AGMD_BC3_Dinner_Mashup", "AGMD BC3 Dinner Mashup"),
        ("grocery_store_oils_ad", "Grocery Store Oils"),
        ("UGC_Content_Kitchen", "UGC Content Kitchen"),
        ("Copy of OO_Test_Project", "Test Project"),
        ("simple_test", "Simple Test"),
        ("", "Untitled Project")
    ]
    
    results = utils.test_text_cleaning(test_cases)
    
    # Test validation
    print("\n🔍 TESTING PROJECT NAME VALIDATION:")
    validation_tests = [
        ("Valid Project Name", True),
        ("", False),
        ("A", False),
        ("x" * 101, False),
        ("Test<>Name", False),
        ("123456", False)
    ]
    
    for name, should_be_valid in validation_tests:
        is_valid, errors = utils.validate_project_name(name)
        status = "✅" if (is_valid == should_be_valid) else "❌"
        print(f"   {status} '{name}': Valid={is_valid}, Errors={errors}")
    
    return results

if __name__ == "__main__":
    test_text_utils()