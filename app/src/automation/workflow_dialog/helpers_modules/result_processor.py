# app/src/automation/workflow_dialog/helpers_modules/result_processor.py
"""
Result Processor Module
Processes and formats processing results
"""

import os
import time
from ...workflow_data_models import ProcessingResult

class ResultProcessor:
    """Processes and formats processing results"""
    
    def create_processing_result(self, processed_files, start_time, output_folder, 
                                success=True):
        """
        Create ProcessingResult from processing data
        
        Args:
            processed_files: List of processed file information
            start_time: Processing start time
            output_folder: Output folder path
            success: Whether processing succeeded
            
        Returns:
            ProcessingResult object
        """
        
        duration_seconds = time.time() - start_time
        duration_display = self._format_duration(duration_seconds)
        
        # Convert processed files to result format
        result_files = self._format_result_files(processed_files)
        
        return ProcessingResult(
            success=success,
            duration=duration_display,
            processed_files=result_files,
            output_folder=output_folder
        )
    
    def _format_duration(self, seconds):
        """Format duration in human-readable format"""
        
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    
    def _format_result_files(self, processed_files):
        """Format processed files for result output"""
        
        result_files = []
        
        for i, file_info in enumerate(processed_files):
            if isinstance(file_info, dict):
                result_files.append(self._format_file_dict(file_info, i))
            else:
                result_files.append(self._format_file_string(file_info, i))
        
        return result_files
    
    def _format_file_dict(self, file_info, index):
        """Format a dictionary file info"""
        
        # Determine endpoint type
        endpoint_type = "quiz"
        if 'svsl_path' in file_info:
            endpoint_type = "svsl"
        elif 'vsl_path' in file_info:
            endpoint_type = "vsl"
        
        return {
            'version': file_info.get('version', f'v{index+1:02d}'),
            'source_file': file_info.get('source_file', f'unknown_{index+1}.mp4'),
            'output_name': file_info.get('output_name', f'processed_{index+1}'),
            'description': file_info.get('description', f'Processed video {index+1}'),
            'duration': file_info.get('duration', '0:00'),
            'size_mb': file_info.get('size_mb', 0),
            'connector_start': file_info.get('connector_start', ''),
            'endpoint_start': file_info.get(f'{endpoint_type}_start', ''),
            'total_duration': file_info.get('total_duration', '0:00'),
            'endpoint_type': endpoint_type
        }
    
    def _format_file_string(self, filename, index):
        """Format a simple filename string"""
        
        filename = str(filename)
        
        return {
            'version': f'v{index+1:02d}',
            'source_file': filename,
            'output_name': os.path.splitext(filename)[0],
            'description': f'Processed {filename}',
            'duration': '0:00',
            'size_mb': 0,
            'connector_start': '',
            'endpoint_start': '',
            'total_duration': '0:00',
            'endpoint_type': 'quiz'
        }