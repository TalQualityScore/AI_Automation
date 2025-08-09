# app/src/naming/__init__.py - Updated for SVSL/VSL support
"""
Modular Naming System for AI Automation Suite

This module provides intelligent naming and parsing capabilities with clear separation of concerns:
- Version extraction from filenames
- Project information parsing
- Standard name generation (now with Quiz/SVSL/VSL support)
- Content analysis for descriptions
"""

# Import with error handling for missing modules
try:
    from .version_extractor import VersionExtractor
    from .project_parser import ProjectParser
    from .name_generator import NameGenerator
    from .content_analyzer import ContentAnalyzer
    from .text_utils import TextUtils
    
    # Convenience functions that maintain backward compatibility
    def generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter=""):
        """
        Generate output filename - main interface function
        Now supports ad_type_selection as "quiz", "svsl", or "vsl"
        """
        name_gen = NameGenerator()
        
        # Normalize ad_type_selection to lowercase for consistency
        if isinstance(ad_type_selection, str):
            ad_type_selection = ad_type_selection.lower()
            # Ensure it's a valid selection
            if ad_type_selection not in ["quiz", "svsl", "vsl"]:
                # Try to detect from common variations
                if "svsl" in ad_type_selection.lower():
                    ad_type_selection = "svsl"
                elif "vsl" in ad_type_selection.lower():
                    ad_type_selection = "vsl"
                else:
                    ad_type_selection = "quiz"  # Default
        
        return name_gen.generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter)

    def generate_project_folder_name(project_name, first_client_video, ad_type_selection):
        """
        Generate project folder name - main interface function
        Now supports ad_type_selection as "Quiz", "SVSL", or "VSL" for folder names
        """
        name_gen = NameGenerator()
        return name_gen.generate_project_folder_name(project_name, first_client_video, ad_type_selection)

    def get_image_description(video_path):
        """Generate image description from video filename - main interface function"""
        analyzer = ContentAnalyzer()
        return analyzer.get_image_description(video_path)

    def parse_project_info(folder_name):
        """Parse project information from folder name - main interface function"""
        parser = ProjectParser()
        return parser.parse_project_info(folder_name)

    def clean_project_name(raw_name):
        """Clean and format project name - main interface function"""
        utils = TextUtils()
        return utils.clean_project_name(raw_name)
    
    # Additional helper functions for SVSL/VSL support
    def detect_endpoint_type(description):
        """
        Detect endpoint type from card description
        Returns: "quiz", "svsl", or "vsl"
        """
        description_lower = description.lower()
        
        if "svsl" in description_lower:
            return "svsl"
        elif "vsl" in description_lower:
            return "vsl"
        else:
            return "quiz"
    
    def format_endpoint_for_folder(endpoint_type):
        """
        Format endpoint type for folder naming
        Converts lowercase to proper case
        """
        mapping = {
            "quiz": "Quiz",
            "svsl": "SVSL",
            "vsl": "VSL"
        }
        return mapping.get(endpoint_type.lower(), "Quiz")
    
    # Export all the convenience functions and classes
    __all__ = [
        'VersionExtractor',
        'ProjectParser', 
        'NameGenerator',
        'ContentAnalyzer',
        'TextUtils',
        'generate_output_name',
        'generate_project_folder_name',
        'get_image_description',
        'parse_project_info',
        'clean_project_name',
        'detect_endpoint_type',
        'format_endpoint_for_folder'
    ]
    
except ImportError as e:
    print(f"⚠️  Warning: Could not import naming modules: {e}")
    print("📁 Make sure all naming module files are in place:")
    print("   - version_extractor.py")
    print("   - project_parser.py") 
    print("   - name_generator.py")
    print("   - content_analyzer.py")
    print("   - text_utils.py")
    
    # Fallback functions to prevent crashes - Updated for SVSL/VSL
    def generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter=""):
        # Normalize ad_type_selection
        ad_type = "quiz"
        if isinstance(ad_type_selection, str):
            ad_type_lower = ad_type_selection.lower()
            if "svsl" in ad_type_lower:
                ad_type = "svsl"
            elif "vsl" in ad_type_lower:
                ad_type = "vsl"
        return f"fallback_output_{ad_type}_{version_num}"
    
    def generate_project_folder_name(project_name, first_client_video, ad_type_selection):
        # Format for folder name
        folder_type = "Quiz"
        if isinstance(ad_type_selection, str):
            ad_type_lower = ad_type_selection.lower()
            if "svsl" in ad_type_lower:
                folder_type = "SVSL"
            elif "vsl" in ad_type_lower:
                folder_type = "VSL"
        return f"fallback_folder_{project_name}_{folder_type}"
    
    def get_image_description(video_path):
        return "fallback_description"
    
    def parse_project_info(folder_name):
        return {"project_name": "Fallback Project", "ad_type": "STOR", "test_name": "0000", "version_letter": "A"}
    
    def clean_project_name(raw_name):
        return raw_name or "Fallback Project"
    
    def detect_endpoint_type(description):
        return "quiz"
    
    def format_endpoint_for_folder(endpoint_type):
        return "Quiz"
    
    __all__ = [
        'generate_output_name',
        'generate_project_folder_name', 
        'get_image_description',
        'parse_project_info',
        'clean_project_name',
        'detect_endpoint_type',
        'format_endpoint_for_folder'
    ]