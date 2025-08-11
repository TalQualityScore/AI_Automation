# app/src/automation/orchestrator/processing/video_processing_modules/path_handler.py
"""
Path Handler Module - FIXED
Manages video paths and output directory setup
"""

import os

class PathHandler:
    """Handles path validation and output directory setup"""
    
    def __init__(self, orchestrator):
        # Store orchestrator reference, not project_paths directly
        self.orchestrator = orchestrator
    
    def validate_and_convert_path(self, video_path):
        """
        Validate and convert video path to absolute
        
        Args:
            video_path: Path to video file
            
        Returns:
            Absolute path to video
        """
        if not os.path.isabs(video_path):
            video_path = os.path.abspath(video_path)
            print(f"📁 Converted to absolute path: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        return video_path
    
    def prepare_output_path(self, project_info, output_name, version_num):
        """
        Prepare the output path for processed video
        
        Args:
            project_info: Project information dictionary
            output_name: Generated output name
            version_num: Version number
            
        Returns:
            Full output path
        """
        # Get project_paths from orchestrator at runtime, not init time
        project_paths = getattr(self.orchestrator, 'project_paths', {})
        
        # Always use _AME folder for output
        ame_folder = project_paths.get('_AME')
        
        # If not in project_paths, try to construct it
        if not ame_folder:
            project_root = project_paths.get('project_root', '.')
            ame_folder = os.path.join(project_root, '_AME')
        
        # Ensure _AME folder exists
        if not os.path.exists(ame_folder):
            os.makedirs(ame_folder)
            print(f"📁 Created _AME folder: {ame_folder}")
        
        output_path = os.path.join(ame_folder, f"{output_name}.mp4")
        print(f"📁 Output path: {output_path}")
        
        return output_path
    
    def get_original_filename(self, video_path):
        """Get the original filename from path"""
        return os.path.basename(video_path)