# app/src/automation/orchestrator/processing/video_processing_modules/video_validator.py
"""
Video Validator Module
Validates required videos exist for processing modes
"""

import os

class VideoValidator:
    """Validates required videos for different processing modes"""
    
    def __init__(self, project_info, project_paths):
        self.project_info = project_info
        self.project_paths = project_paths
    
    def validate_required_videos(self, processing_mode):
        """
        Validate that required videos exist for the processing mode
        
        Args:
            processing_mode: Processing mode string
            
        Returns:
            Tuple of (video_paths_dict, missing_videos_list)
        """
        from ....video_processor import (_get_connector_video, _get_quiz_video, 
                                         _get_svsl_video, _get_vsl_video)
        
        video_paths = {}
        missing_videos = []
        
        # Check based on processing mode
        if processing_mode == "connector_quiz":
            connector = _get_connector_video()
            quiz = _get_quiz_video()
            
            if not connector:
                missing_videos.append("connector")
            else:
                video_paths['connector_path'] = connector
            
            if not quiz:
                missing_videos.append("quiz")
            else:
                video_paths['quiz_path'] = quiz
                video_paths['endpoint_type'] = "quiz"
        
        elif processing_mode == "quiz_only":
            quiz = _get_quiz_video()
            if not quiz:
                missing_videos.append("quiz")
            else:
                video_paths['quiz_path'] = quiz
                video_paths['endpoint_type'] = "quiz"
        
        elif processing_mode == "connector_svsl":
            connector = _get_connector_video()
            svsl = _get_svsl_video()
            
            if not connector:
                missing_videos.append("connector")
            else:
                video_paths['connector_path'] = connector
            
            if not svsl:
                missing_videos.append("SVSL")
            else:
                video_paths['svsl_path'] = svsl
                video_paths['endpoint_type'] = "svsl"
        
        elif processing_mode == "svsl_only":
            svsl = _get_svsl_video()
            if not svsl:
                missing_videos.append("SVSL")
            else:
                video_paths['svsl_path'] = svsl
                video_paths['endpoint_type'] = "svsl"
        
        elif processing_mode == "connector_vsl":
            connector = _get_connector_video()
            vsl = _get_vsl_video()
            
            if not connector:
                missing_videos.append("connector")
            else:
                video_paths['connector_path'] = connector
            
            if not vsl:
                missing_videos.append("VSL")
            else:
                video_paths['vsl_path'] = vsl
                video_paths['endpoint_type'] = "vsl"
        
        elif processing_mode == "vsl_only":
            vsl = _get_vsl_video()
            if not vsl:
                missing_videos.append("VSL")
            else:
                video_paths['vsl_path'] = vsl
                video_paths['endpoint_type'] = "vsl"
        
        return video_paths, missing_videos
    
    def generate_missing_video_error(self, missing_videos, processing_mode):
        """
        Generate detailed error message for missing videos
        
        Args:
            missing_videos: List of missing video types
            processing_mode: Processing mode that failed
            
        Returns:
            Detailed error message string
        """
        account_code = self.project_info.get('account_code', 'OO')
        platform_code = self.project_info.get('platform_code', 'FB')
        
        error_message = f"❌ MISSING REQUIRED VIDEO FILES\n\n"
        error_message += f"Cannot process in '{processing_mode}' mode.\n"
        error_message += f"Missing: {', '.join(missing_videos)} video(s)\n\n"
        error_message += "Please add the missing video(s) to:\n"
        
        # Add specific paths for each missing video type
        for video_type in missing_videos:
            if video_type.lower() == "connector":
                path = f"Assets/Videos/{account_code}/{platform_code}/Connector/"
            elif video_type.lower() == "quiz":
                path = f"Assets/Videos/{account_code}/{platform_code}/Quiz/"
            elif video_type.upper() == "VSL":
                path = f"Assets/Videos/{account_code}/{platform_code}/VSL/"
            elif video_type.upper() == "SVSL":
                path = f"Assets/Videos/{account_code}/{platform_code}/SVSL/"
            else:
                path = f"Assets/Videos/{account_code}/{platform_code}/{video_type}/"
            
            full_path = os.path.join(
                os.path.dirname(self.project_paths.get('project_root', '.')), 
                path
            )
            error_message += f"\n{video_type.upper()}:\n  {full_path}"
            
            # Check if folder exists and is empty
            if not os.path.exists(full_path):
                error_message += f"\n  ⚠️ Folder doesn't exist - create it first!"
            else:
                files = [f for f in os.listdir(full_path) 
                        if f.endswith(('.mp4', '.mov', '.avi'))]
                if not files:
                    error_message += f"\n  ⚠️ Folder is empty - add {video_type.upper()} videos!"
            error_message += "\n"
        
        error_message += "\n📌 Action Required:\n"
        error_message += "1. Add the missing video files to the folders above\n"
        error_message += "2. Run the automation again\n"
        
        return error_message