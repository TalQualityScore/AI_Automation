# app/src/automation/orchestrator/integration/mode_utilities.py
"""
Mode Utilities - Helper functions for processing mode management
Extracted from ui_integration_base.py for better organization
"""

class ModeUtilities:
    """Utility functions for processing mode management"""
    
    def __init__(self):
        # Mode suffix mapping
        self.mode_suffixes = {
            'quiz_only': 'Quiz',
            'vsl_only': 'VSL',
            'svsl_only': 'SVSL',
            'connector_quiz': 'Connector Quiz',
            'connector_vsl': 'Connector VSL',
            'connector_svsl': 'Connector SVSL',
            'save_only': 'Original'
        }
        
        # Mode to folder type mapping
        self.mode_to_folder_type = {
            'quiz_only': 'Quiz',
            'vsl_only': 'VSL', 
            'svsl_only': 'SVSL',
            'connector_quiz': 'Quiz',
            'connector_vsl': 'VSL',
            'connector_svsl': 'SVSL',
            'save_only': 'Original'
        }
        
        # Processing priority order (most important first)
        self.processing_priority = [
            'quiz_only',
            'vsl_only', 
            'svsl_only',
            'connector_quiz',
            'connector_vsl',
            'connector_svsl',
            'save_only'
        ]
    
    def get_mode_suffix(self, mode):
        """Get appropriate suffix for mode"""
        return self.mode_suffixes.get(mode, mode.upper())
    
    def get_folder_type(self, mode):
        """Get folder type for mode"""
        return self.mode_to_folder_type.get(mode, 'Quiz')
    
    def sort_modes_by_priority(self, modes):
        """Sort modes by processing priority"""
        return sorted(modes, key=lambda x: self.processing_priority.index(x) 
                     if x in self.processing_priority else 999)
    
    def validate_mode(self, mode):
        """Validate if mode is supported"""
        return mode in self.mode_suffixes
    
    def get_all_supported_modes(self):
        """Get list of all supported processing modes"""
        return list(self.mode_suffixes.keys())
    
    def get_mode_display_name(self, mode):
        """Get user-friendly display name for mode"""
        display_names = {
            'quiz_only': 'Quiz Only',
            'vsl_only': 'VSL Only',
            'svsl_only': 'SVSL Only',
            'connector_quiz': 'Connector + Quiz',
            'connector_vsl': 'Connector + VSL',
            'connector_svsl': 'Connector + SVSL',
            'save_only': 'Save Original'
        }
        return display_names.get(mode, mode.replace('_', ' ').title())
    
    def requires_connector(self, mode):
        """Check if mode requires connector processing"""
        return mode.startswith('connector_')
    
    def get_endpoint_type(self, mode):
        """Extract endpoint type from mode"""
        if 'quiz' in mode:
            return 'quiz'
        elif 'vsl' in mode:
            return 'vsl'
        elif 'svsl' in mode:
            return 'svsl'
        else:
            return 'unknown'
    
    def estimate_processing_time(self, mode, video_count=1):
        """Estimate processing time for mode (in seconds)"""
        base_times = {
            'save_only': 30,        # Just copying
            'quiz_only': 120,       # Client + Quiz
            'vsl_only': 180,        # Client + VSL
            'svsl_only': 240,       # Client + SVSL
            'connector_quiz': 180,  # Client + Connector + Quiz
            'connector_vsl': 240,   # Client + Connector + VSL
            'connector_svsl': 300   # Client + Connector + SVSL
        }
        
        base_time = base_times.get(mode, 120)
        return base_time * video_count
    
    def get_required_assets(self, mode):
        """Get list of required assets for mode"""
        assets = ['client_video']  # Always need client video
        
        if self.requires_connector(mode):
            assets.append('connector_video')
        
        endpoint = self.get_endpoint_type(mode)
        if endpoint != 'unknown':
            assets.append(f'{endpoint}_template')
        
        return assets
    
    def get_processing_steps(self, mode):
        """Get list of processing steps for mode"""
        steps = ['Download Videos', 'Create Project Structure']
        
        if mode == 'save_only':
            steps.extend(['Copy Videos', 'Organize Files'])
        else:
            steps.extend(['Process Videos', 'Add Templates', 'Render Output'])
            
            if self.requires_connector(mode):
                steps.insert(-2, 'Add Connector')
        
        steps.extend(['Update Sheets', 'Generate Reports', 'Cleanup'])
        return steps