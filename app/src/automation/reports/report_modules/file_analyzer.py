# app/src/automation/reports/report_modules/file_analyzer.py
"""
File Analyzer Module
Analyzes video files and extracts information
"""

import os

class FileAnalyzer:
    """Analyzes video files for report generation"""
    
    def __init__(self, duration_calculator):
        self.duration_calc = duration_calculator
    
    def analyze_file(self, file_info, output_folder):
        """
        Analyze a single processed file
        
        Args:
            file_info: Dictionary with file information
            output_folder: Output folder path
            
        Returns:
            Dictionary with analyzed data
        """
        analysis = {
            'output_name': file_info.get('output_name', 'processed'),
            'source_file': file_info.get('source_file', 'Unknown'),
            'description': file_info.get('description', ''),
            'client_video_path': file_info.get('client_video_path', ''),
            'connector_path': file_info.get('connector_path', ''),
            'quiz_path': file_info.get('quiz_path', ''),
            'svsl_path': file_info.get('svsl_path', ''),
            'vsl_path': file_info.get('vsl_path', ''),
            'durations': {}
        }
        
        # Determine composition type
        analysis['composition'] = self._determine_composition(analysis['description'])
        
        # Find output file
        analysis['output_path'] = self._find_output_file(
            analysis['output_name'], output_folder
        )
        
        # Get all durations
        analysis['durations'] = self._get_all_durations(analysis)
        
        # Get file size
        analysis['size_mb'] = self._get_file_size(analysis['output_path'])
        
        return analysis
    
    def _determine_composition(self, description):
        """Determine composition type from description"""
        desc_lower = description.lower()
        
        if 'connector' in desc_lower and 'quiz' in desc_lower:
            return "Client Video → Connector → Quiz"
        elif 'connector' in desc_lower and 'svsl' in desc_lower:
            return "Client Video → Connector → SVSL"
        elif 'connector' in desc_lower and 'vsl' in desc_lower:
            return "Client Video → Connector → VSL"
        elif 'quiz' in desc_lower:
            return "Client Video → Quiz"
        elif 'svsl' in desc_lower:
            return "Client Video → SVSL"
        elif 'vsl' in desc_lower:
            return "Client Video → VSL"
        else:
            return "Direct copy (no processing)"
    
    def _find_output_file(self, output_name, output_folder):
        """Find the output file path"""
        # Check in _AME subfolder first
        output_path = os.path.join(output_folder, "_AME", f"{output_name}.mp4")
        if not os.path.exists(output_path):
            # Try without _AME folder
            output_path = os.path.join(output_folder, f"{output_name}.mp4")
        
        return output_path if os.path.exists(output_path) else None
    
    def _get_all_durations(self, analysis):
        """Get durations for all video components"""
        durations = {}
        
        # DEBUG
        print(f"📊 DEBUG FileAnalyzer._get_all_durations:")
        print(f"   - client_video_path: {analysis.get('client_video_path', 'NOT SET')}")
        print(f"   - quiz_path: {analysis.get('quiz_path', 'NOT SET')}")
        
        # Get client video duration
        if analysis['client_video_path'] and os.path.exists(analysis['client_video_path']):
            print(f"   ✅ Client video found: {analysis['client_video_path']}")
            durations['client'] = self.duration_calc.get_video_duration(
                analysis['client_video_path']
            )
            print(f"   - Client duration: {durations['client']}s")
        else:
            print(f"   ❌ Client video NOT found or path empty")
            durations['client'] = 0
        
        # Get connector duration if present
        if analysis['connector_path'] and os.path.exists(analysis['connector_path']):
            durations['connector'] = self.duration_calc.get_video_duration(
                analysis['connector_path']
            )
        else:
            durations['connector'] = 0
        
        # Get endpoint duration (quiz/svsl/vsl)
        for endpoint_type in ['quiz', 'svsl', 'vsl']:
            path_key = f'{endpoint_type}_path'
            if analysis.get(path_key) and os.path.exists(analysis[path_key]):
                print(f"   ✅ {endpoint_type} found: {analysis[path_key]}")
                durations[endpoint_type] = self.duration_calc.get_video_duration(
                    analysis[path_key]
                )
                print(f"   - {endpoint_type} duration: {durations[endpoint_type]}s")
            else:
                durations[endpoint_type] = 0
        
        # Get total output duration if available
        if analysis['output_path']:
            durations['total'] = self.duration_calc.get_video_duration(
                analysis['output_path']
            )
        else:
            # Calculate total
            durations['total'] = (durations['client'] + 
                                durations['connector'] + 
                                durations.get('quiz', 0) +
                                durations.get('svsl', 0) +
                                durations.get('vsl', 0))
        
        return durations

    def _get_file_size(self, file_path):
        """Get file size in MB"""
        if file_path and os.path.exists(file_path):
            try:
                return os.path.getsize(file_path) / (1024 * 1024)
            except:
                pass
        return 0