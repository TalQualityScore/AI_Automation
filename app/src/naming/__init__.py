# app/src/naming/__init__.py - FIXED VERSION
"""
Modular Naming System for AI Automation Suite

This module provides intelligent naming and parsing capabilities with clear separation of concerns:
- Version extraction from filenames
- Project information parsing
- Standard name generation
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
        """Generate output filename - main interface function"""
        name_gen = NameGenerator()
        return name_gen.generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter)

    def generate_project_folder_name(project_name, first_client_video, ad_type_selection):
        """Generate project folder name - main interface function"""
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
        'clean_project_name'
    ]
    
except ImportError as e:
    print(f"⚠️  Warning: Could not import naming modules: {e}")
    print("📁 Make sure all naming module files are in place:")
    print("   - version_extractor.py")
    print("   - project_parser.py") 
    print("   - name_generator.py")
    print("   - content_analyzer.py")
    print("   - text_utils.py")
    
    # Fallback functions to prevent crashes
    def generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num, version_letter=""):
        return f"fallback_output_{version_num}"
    
    def generate_project_folder_name(project_name, first_client_video, ad_type_selection):
        return f"fallback_folder_{project_name}"
    
    def get_image_description(video_path):
        return "fallback_description"
    
    def parse_project_info(folder_name):
        return {"project_name": "Fallback Project", "ad_type": "STOR", "test_name": "0000", "version_letter": "A"}
    
    def clean_project_name(raw_name):
        return raw_name or "Fallback Project"
    
    __all__ = [
        'generate_output_name',
        'generate_project_folder_name', 
        'get_image_description',
        'parse_project_info',
        'clean_project_name'
    ]