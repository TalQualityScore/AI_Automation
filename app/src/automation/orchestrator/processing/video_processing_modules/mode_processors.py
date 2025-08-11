# app/src/automation/orchestrator/processing/video_processing_modules/mode_processor.py
"""
Mode Processors Module - FIXED
Handles different processing modes and returns actual video paths used
"""

import shutil
import os

class ModeProcessor:
    """Processes videos based on different modes"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def process_save_only(self, client_video, output_path, version_num):
        """
        Process save_only mode - just copy the file
        
        Returns:
            Tuple of (result, description, endpoint_type, video_paths)
        """
        def save_video():
            shutil.copy(client_video, output_path)
            return f"Saved: {os.path.basename(output_path)}"
        
        result = self.orchestrator.monitor.execute_with_activity_monitoring(
            save_video,
            f"Save Video v{version_num:02d}",
            no_activity_timeout=120
        )
        
        # Return empty video_paths for save_only
        return result, "", "", {}
    
    def process_with_transitions(self, client_video, output_path, target_width, 
                                target_height, processing_mode, timeout_seconds,
                                version_num):
        """
        Process video with transitions and endpoints - FIXED to return video paths
        
        Returns:
            Tuple of (result, description, endpoint_type, video_paths)
        """
        from ....video_processor import process_video_sequence
        
        # Build description
        original_filename = os.path.basename(client_video)
        description = f"Copy of OO_{original_filename}"
        
        # Determine endpoint type and get actual video paths
        video_paths = {}
        
        if "quiz" in processing_mode:
            endpoint_type = "quiz"
            # Get the actual quiz video path
            from ....video_processor import _get_quiz_video
            quiz_video = _get_quiz_video()
            if quiz_video:
                video_paths['quiz_path'] = quiz_video
                
        elif "svsl" in processing_mode:
            endpoint_type = "svsl"
            from ....video_processor import _get_svsl_video
            svsl_video = _get_svsl_video()
            if svsl_video:
                video_paths['svsl_path'] = svsl_video
                
        elif "vsl" in processing_mode:
            endpoint_type = "vsl"
            from ....video_processor import _get_vsl_video
            vsl_video = _get_vsl_video()
            if vsl_video:
                video_paths['vsl_path'] = vsl_video
        else:
            endpoint_type = ""
        
        # Check for connector in any mode
        if "connector" in processing_mode:
            from ....video_processor import _get_connector_video
            connector_video = _get_connector_video()
            if connector_video:
                video_paths['connector_path'] = connector_video
        
        # Process with FFmpeg
        def process_with_ffmpeg():
            error = process_video_sequence(
                client_video, output_path, target_width, 
                target_height, processing_mode
            )
            if error:
                raise Exception(error)
            return f"Processed: {os.path.basename(output_path)}"
        
        result = self.orchestrator.monitor.execute_with_activity_monitoring(
            process_with_ffmpeg,
            f"Process Video v{version_num:02d}",
            no_activity_timeout=timeout_seconds
        )
        
        # Return with video_paths
        return result, description, endpoint_type, video_paths