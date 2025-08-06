# app/src/naming/content_analyzer.py
"""
Content Analysis Module

Handles analysis of video filenames to generate meaningful descriptions
and extract content-related information.
"""

import os
import re

class ContentAnalyzer:
    """Analyzes video content and filenames to generate descriptions"""
    
    def __init__(self):
        # Define keyword patterns for content recognition
        self.content_keywords = {
            'food': {
                'patterns': [
                    (r'grocery', 'grocery'),
                    (r'cooking', 'cooking'),
                    (r'dinner', 'dinner'),
                    (r'mashup', 'mashup'),
                    (r'recipe', 'recipe'),
                    (r'kitchen', 'kitchen'),
                    (r'food', 'food'),
                    (r'meal', 'meal'),
                    (r'breakfast', 'breakfast'),
                    (r'lunch', 'lunch')
                ],
                'priority': 1
            },
            'health': {
                'patterns': [
                    (r'health', 'health'),
                    (r'supplement', 'supplement'),
                    (r'vitamin', 'vitamin'),
                    (r'nutrition', 'nutrition'),
                    (r'wellness', 'wellness'),
                    (r'fitness', 'fitness'),
                    (r'diet', 'diet')
                ],
                'priority': 2
            },
            'oil': {
                'patterns': [
                    (r'oil', 'oil'),
                    (r'olive', 'olive'),
                    (r'coconut', 'coconut'),
                    (r'mct', 'mct'),
                    (r'cooking', 'cooking')
                ],
                'priority': 3
            },
            'lifestyle': {
                'patterns': [
                    (r'daily', 'daily'),
                    (r'routine', 'routine'),
                    (r'morning', 'morning'),
                    (r'evening', 'evening'),
                    (r'lifestyle', 'lifestyle'),
                    (r'habit', 'habit')
                ],
                'priority': 4
            },
            'generic': {
                'patterns': [
                    (r'test', 'test'),
                    (r'demo', 'demo'),
                    (r'sample', 'sample'),
                    (r'example', 'example'),
                    (r'trial', 'trial')
                ],
                'priority': 5
            }
        }
    
    def get_image_description(self, video_path):
        """
        Generate image description from video filename
        
        Args:
            video_path (str): Path to video file
            
        Returns:
            str: Generated description for image/video content
        """
        # Extract base filename without extension
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        
        # Remove common prefixes that don't add content value
        base_name = self._clean_filename(base_name)
        
        print(f"🖼️ GENERATING IMAGE DESCRIPTION:")
        print(f"   Input: '{video_path}'")
        print(f"   Cleaned name: '{base_name}'")
        
        # Extract keywords based on content patterns
        keywords = self._extract_keywords(base_name)
        
        # Generate description from keywords
        description = self._build_description(keywords, base_name)
        
        print(f"🎯 Generated description: '{description}'")
        return description
    
    def _clean_filename(self, filename):
        """Remove common prefixes and clean filename for analysis"""
        
        # Remove common prefixes
        cleaned = filename.replace("Copy of OO_", "")
        cleaned = cleaned.replace("OO_", "")
        cleaned = cleaned.replace("Copy of ", "")
        
        # Remove file numbering patterns
        cleaned = re.sub(r'_\d{3,}$', '', cleaned)  # Remove trailing numbers like _001
        cleaned = re.sub(r'_v\d+$', '', cleaned, flags=re.IGNORECASE)  # Remove version indicators
        
        return cleaned
    
    def _extract_keywords(self, text):
        """Extract content keywords from text"""
        
        text_lower = text.lower()
        found_keywords = []
        
        # Search through all keyword categories
        for category, info in self.content_keywords.items():
            category_keywords = []
            
            for pattern, keyword in info['patterns']:
                if re.search(pattern, text_lower):
                    category_keywords.append({
                        'keyword': keyword,
                        'category': category,
                        'priority': info['priority']
                    })
            
            found_keywords.extend(category_keywords)
        
        # Sort by priority and remove duplicates
        found_keywords = sorted(found_keywords, key=lambda x: x['priority'])
        unique_keywords = []
        seen = set()
        
        for kw in found_keywords:
            if kw['keyword'] not in seen:
                unique_keywords.append(kw)
                seen.add(kw['keyword'])
        
        print(f"🔍 Found keywords: {[kw['keyword'] for kw in unique_keywords]}")
        return unique_keywords
    
    def _build_description(self, keywords, original_name):
        """Build final description from extracted keywords"""
        
        if keywords:
            # Use top 2 keywords for description
            top_keywords = [kw['keyword'] for kw in keywords[:2]]
            description = "_".join(top_keywords)
        else:
            # Fallback: use first meaningful part of filename
            description = self._fallback_description(original_name)
        
        # Clean up the description
        description = self._clean_description(description)
        
        return description
    
    def _fallback_description(self, original_name):
        """Generate fallback description when no keywords found"""
        
        # Split by common separators and take first meaningful part
        parts = re.split(r'[_\-\s]+', original_name)
        
        for part in parts:
            # Skip common prefixes and technical parts
            if (len(part) > 2 and 
                not part.upper() in ['AD', 'OPT', 'VTD', 'STOR', 'ACT'] and
                not re.match(r'\d+', part) and  # Skip pure numbers
                not re.match(r'[A-Z]{2,}$', part)):  # Skip all-caps codes
                return part[:10].lower()  # First 10 chars, lowercase
        
        # Ultimate fallback
        return "video"
    
    def _clean_description(self, description):
        """Clean and validate the final description"""
        
        # Remove any non-alphanumeric characters except underscores
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '', description)
        
        # Ensure it's not empty and not too long
        if not cleaned or len(cleaned) < 2:
            cleaned = "video"
        elif len(cleaned) > 20:
            cleaned = cleaned[:20]
        
        return cleaned.lower()
    
    def analyze_content_type(self, video_path):
        """
        Analyze and categorize the content type of a video
        
        Args:
            video_path (str): Path to video file
            
        Returns:
            dict: Content analysis results
        """
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        cleaned_name = self._clean_filename(base_name)
        keywords = self._extract_keywords(cleaned_name)
        
        # Determine primary content category
        primary_category = 'general'
        if keywords:
            primary_category = keywords[0]['category']
        
        # Generate confidence score based on number of matching keywords
        confidence = min(len(keywords) * 0.3, 1.0)  # Max confidence of 1.0
        
        return {
            'primary_category': primary_category,
            'keywords': [kw['keyword'] for kw in keywords],
            'confidence': confidence,
            'description': self.get_image_description(video_path),
            'cleaned_filename': cleaned_name
        }
    
    def get_content_categories(self):
        """Get available content categories and their patterns"""
        return {
            category: {
                'patterns': [pattern for pattern, _ in info['patterns']],
                'priority': info['priority']
            }
            for category, info in self.content_keywords.items()
        }
    
    def test_content_analysis(self, test_files):
        """
        Test content analysis on multiple files
        
        Args:
            test_files (list): List of (filename, expected_description) tuples
            
        Returns:
            dict: Test results
        """
        results = {
            'total': len(test_files),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        print("🧪 TESTING CONTENT ANALYSIS:")
        print("=" * 60)
        
        for filename, expected in test_files:
            print(f"\n📁 Testing: {filename}")
            if expected:
                print(f"📄 Expected: '{expected}'")
            
            result = self.get_image_description(filename)
            analysis = self.analyze_content_type(filename)
            
            # Simple pass/fail based on whether expected keywords are present
            if expected:
                contains_expected = any(exp_word in result.lower() for exp_word in expected.lower().split('_'))
                status = "✅ PASS" if contains_expected else "❌ FAIL"
                if contains_expected:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
            else:
                # If no expected result, just check that we got something reasonable
                status = "✅ PASS" if result and len(result) > 0 else "❌ FAIL"
                results['passed'] += 1
            
            results['details'].append({
                'filename': filename,
                'expected': expected,
                'result': result,
                'analysis': analysis,
                'status': status
            })
            
            print(f"🎯 Status: {status}")
            print(f"📊 Analysis: Category={analysis['primary_category']}, Keywords={analysis['keywords']}")
        
        print(f"\n📊 SUMMARY: {results['passed']}/{results['total']} passed")
        return results

# Test function for standalone usage
def test_content_analyzer():
    """Test the content analyzer with common video files"""
    
    analyzer = ContentAnalyzer()
    
    test_files = [
        ("GMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4", "dinner"),
        ("OO_GroceryOils_AD_VTD-1234A_001.mp4", "grocery"),
        ("MCT_CookingOil_AD_STOR-5678B.mp4", "cooking"),
        ("PP_HealthyRecipes_Kitchen_Test.mp4", "kitchen"),
        ("Unknown_Video_File.mp4", None)
    ]
    
    results = analyzer.test_content_analysis(test_files)
    
    # Also show available categories
    print("\n📋 AVAILABLE CONTENT CATEGORIES:")
    categories = analyzer.get_content_categories()
    for category, info in categories.items():
        print(f"   {category.title()}: {info['patterns'][:3]}...")  # Show first 3 patterns
    
    return results

if __name__ == "__main__":
    test_content_analyzer()