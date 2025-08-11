# app/src/automation/reports/report_modules/timeline_builder.py
"""
Timeline Builder Module
Builds video timeline information
"""

import os

class TimelineBuilder:
    """Builds timeline information for video compositions"""
    
    def __init__(self, duration_calculator):
        self.duration_calc = duration_calculator
    
    def build_timeline(self, analysis, use_transitions):
        """
        Build timeline showing when each component appears
        
        Args:
            analysis: File analysis dictionary
            use_transitions: Whether transitions are enabled
            
        Returns:
            List of timeline entries
        """
        timeline = []
        current_time = 0
        durations = analysis['durations']
        composition = analysis['composition']
        
        # Client video timeline
        if durations['client'] > 0:
            client_end = current_time + durations['client']
            timeline.append({
                'component': 'Client',
                'start': current_time,
                'end': client_end,
                'formatted': self.duration_calc.format_timecode(current_time, client_end)
            })
            current_time = client_end
        
        # Connector timeline (if present)
        if 'connector' in composition.lower() and durations['connector'] > 0:
            if use_transitions:
                current_time += 0.25  # Add transition time
            
            connector_end = current_time + durations['connector']
            timeline.append({
                'component': 'Connector',
                'start': current_time,
                'end': connector_end,
                'formatted': self.duration_calc.format_timecode(current_time, connector_end)
            })
            current_time = connector_end
        
        # Endpoint timeline (quiz/svsl/vsl)
        endpoint_types = {
            'quiz': 'Quiz Outro',
            'svsl': 'SVSL',
            'vsl': 'VSL'
        }
        
        for endpoint_key, endpoint_name in endpoint_types.items():
            if endpoint_key in composition.lower() and durations.get(endpoint_key, 0) > 0:
                if use_transitions:
                    current_time += 0.25  # Add transition time
                
                endpoint_end = current_time + durations[endpoint_key]
                timeline.append({
                    'component': endpoint_name,
                    'start': current_time,
                    'end': endpoint_end,
                    'formatted': self.duration_calc.format_timecode(current_time, endpoint_end)
                })
                current_time = endpoint_end
                break  # Only one endpoint type per video
        
        return timeline
    
    def get_component_files(self, analysis):
        """Get component file names for display"""
        files = {}
        
        if analysis['connector_path']:
            files['connector'] = os.path.basename(analysis['connector_path'])
        
        for endpoint in ['quiz', 'svsl', 'vsl']:
            path_key = f'{endpoint}_path'
            if analysis.get(path_key):
                files[endpoint] = os.path.basename(analysis[path_key])
        
        return files