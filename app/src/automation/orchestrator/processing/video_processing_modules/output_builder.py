# app/src/automation/orchestrator/processing/video_processing_modules/output_builder.py
"""
Output Builder Module - WITH DEBUG
Builds output information for processed videos
"""

import os

class OutputBuilder:
    """Builds output information dictionaries"""
    
    def build_processed_file_info(self, client_video, output_path, output_name,
                                 version_num, version_letter, video_paths,
                                 description, endpoint_type):
        """
        Build the processed file information dictionary
        """
        original_filename = os.path.basename(client_video)
        
        # DEBUG: Print what we're receiving
        print(f"📝 DEBUG OutputBuilder:")
        print(f"   - client_video: {client_video}")
        print(f"   - client exists: {os.path.exists(client_video)}")
        print(f"   - video_paths: {video_paths}")
        
        # Get file size if output exists
        size_mb = 0
        if output_path and os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
        
        # Build complete info with all paths for breakdown report
        processed_file_info = {
            "version": version_num,
            "version_letter": version_letter if version_letter else '',
            "source_file": original_filename,
            "output_name": output_name,
            "client_video_path": client_video,  # Full path to client video
            "output_path": output_path,
            "original_filename": original_filename,
            "description": description,
            "endpoint_type": endpoint_type,
            "size_mb": size_mb,
            
            # ADD ALL VIDEO PATHS FOR BREAKDOWN REPORT
            "connector_path": video_paths.get('connector_path', ''),
            "quiz_path": video_paths.get('quiz_path', ''),
            "svsl_path": video_paths.get('svsl_path', ''),
            "vsl_path": video_paths.get('vsl_path', ''),
            
            # Duration placeholders (will be calculated by report)
            "duration": "0:00",
            "connector_start": "",
            "endpoint_start": "",
            "total_duration": "0:00"
        }
        
        # DEBUG: Print what we're sending
        print(f"   - client_video_path in output: {processed_file_info['client_video_path']}")
        print(f"   - quiz_path in output: {processed_file_info['quiz_path']}")
        
        return processed_file_info