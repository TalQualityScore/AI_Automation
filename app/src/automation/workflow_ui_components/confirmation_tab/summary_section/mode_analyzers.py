# app/src/automation/workflow_ui_components/confirmation_tab/summary_section/mode_analyzers.py
"""
Mode Analyzers - Processing Mode Analysis Logic
Handles analyzing selected modes and determining display information
"""

class ModeAnalyzers:
    """Handles mode analysis and display logic"""
    
    def __init__(self, summary_section):
        self.ss = summary_section  # Reference to main SummarySection
        
        # Mode display mapping
        self.mode_displays = {
            "save_only": "Save As Is",
            "quiz_only": "Add Quiz Outro",
            "connector_quiz": "Add Connector + Quiz",
            "svsl_only": "Add SVSL",
            "connector_svsl": "Add Connector + SVSL",
            "vsl_only": "Add VSL",
            "connector_vsl": "Add Connector + VSL"
        }
        
        # Endpoint mapping
        self.endpoint_mapping = {
            "save_only": "No processing (Save As Is)",
            "quiz_only": "Quiz Outro",
            "connector_quiz": "Quiz Outro",
            "svsl_only": "SVSL",
            "connector_svsl": "SVSL", 
            "vsl_only": "VSL",
            "connector_vsl": "VSL"
        }
    
    def get_video_count(self):
        """Get actual video count from data"""
        video_count = 0
        
        if hasattr(self.ss.data, 'client_videos') and self.ss.data.client_videos:
            if isinstance(self.ss.data.client_videos, list):
                # Count only non-empty entries
                actual_videos = [v for v in self.ss.data.client_videos if v]
                video_count = len(actual_videos)
            else:
                video_count = 1
        
        # If we still have 0, default to 1
        if video_count == 0:
            video_count = 1
        
        return video_count
    
    def get_selected_modes(self):
        """Get currently selected processing modes"""
        # Try to get from main tab first
        if hasattr(self.ss.main_tab, 'get_selected_processing_modes'):
            modes = self.ss.main_tab.get_selected_processing_modes()
            if modes:
                return modes
        
        # Try to get from data
        if hasattr(self.ss.data, 'selected_processing_modes'):
            modes = getattr(self.ss.data, 'selected_processing_modes', [])
            if modes:
                return modes
        
        # Fallback to single mode
        current_mode = self._get_fallback_mode()
        return [current_mode]
    
    def _get_fallback_mode(self):
        """Get fallback mode when no modes are selected"""
        # Try main tab first
        if hasattr(self.ss.main_tab, 'processing_mode_var'):
            mode_display = self.ss.main_tab.processing_mode_var.get()
            mode_code = self._convert_display_to_code(mode_display)
            if mode_code:
                return mode_code
        
        # Try data object
        if hasattr(self.ss.data, 'processing_mode'):
            return getattr(self.ss.data, 'processing_mode', 'quiz_only')
        
        # Final fallback
        return 'quiz_only'
    
    def _convert_display_to_code(self, display_name):
        """Convert display name back to mode code"""
        mode_map = {
            "Save As Is": "save_only",
            "Add Quiz Outro": "quiz_only",
            "Add Connector + Quiz": "connector_quiz",
            "Add SVSL": "svsl_only",
            "Add Connector + SVSL": "connector_svsl",
            "Add VSL": "vsl_only",
            "Add Connector + VSL": "connector_vsl"
        }
        return mode_map.get(display_name, "quiz_only")
    
    def get_mode_display_name(self, mode_code):
        """Get display name for processing mode"""
        return self.mode_displays.get(mode_code, mode_code.replace('_', ' ').title())
    
    def get_endpoint_from_mode(self, mode_code):
        """Get endpoint description from processing mode"""
        return self.endpoint_mapping.get(mode_code, "Quiz Outro")
    
    def is_single_mode(self, selected_modes):
        """Check if only one mode is selected"""
        return len(selected_modes) == 1
    
    def is_multi_mode(self, selected_modes):
        """Check if multiple modes are selected"""
        return len(selected_modes) > 1
    
    def requires_connector(self, mode_code):
        """Check if mode requires connector"""
        return mode_code.startswith('connector_')
    
    def get_endpoint_type(self, mode_code):
        """Get endpoint type from mode"""
        if 'quiz' in mode_code:
            return 'quiz'
        elif 'svsl' in mode_code:
            return 'svsl'
        elif 'vsl' in mode_code:
            return 'vsl'
        elif 'save' in mode_code:
            return 'save'
        else:
            return 'unknown'
    
    def analyze_mode_complexity(self, selected_modes):
        """Analyze complexity of selected modes"""
        analysis = {
            'total_modes': len(selected_modes),
            'has_connector': any(self.requires_connector(mode) for mode in selected_modes),
            'endpoint_types': list(set(self.get_endpoint_type(mode) for mode in selected_modes)),
            'complexity_score': self._calculate_complexity_score(selected_modes)
        }
        return analysis
    
    def _calculate_complexity_score(self, selected_modes):
        """Calculate complexity score for processing"""
        score = 0
        
        # Base score per mode
        score += len(selected_modes) * 10
        
        # Connector modes are more complex
        connector_modes = [mode for mode in selected_modes if self.requires_connector(mode)]
        score += len(connector_modes) * 5
        
        # Different endpoint types increase complexity
        unique_endpoints = set(self.get_endpoint_type(mode) for mode in selected_modes)
        score += len(unique_endpoints) * 3
        
        return score
    
    def get_mode_categories(self, selected_modes):
        """Categorize selected modes"""
        categories = {
            'save_modes': [],
            'quiz_modes': [],
            'vsl_modes': [],
            'svsl_modes': [],
            'connector_modes': []
        }
        
        for mode in selected_modes:
            if 'save' in mode:
                categories['save_modes'].append(mode)
            elif 'quiz' in mode:
                categories['quiz_modes'].append(mode)
            elif 'vsl' in mode and 'svsl' not in mode:
                categories['vsl_modes'].append(mode)
            elif 'svsl' in mode:
                categories['svsl_modes'].append(mode)
            
            if self.requires_connector(mode):
                categories['connector_modes'].append(mode)
        
        return categories
    
    def validate_mode_selection(self, selected_modes):
        """Validate mode selection"""
        if not selected_modes:
            return False, "No processing modes selected"
        
        # Check for valid mode codes
        valid_modes = list(self.mode_displays.keys())
        invalid_modes = [mode for mode in selected_modes if mode not in valid_modes]
        
        if invalid_modes:
            return False, f"Invalid modes: {', '.join(invalid_modes)}"
        
        # Check for conflicting modes (optional validation)
        # Could add logic here if certain modes shouldn't be combined
        
        return True, ""
    
    def get_mode_summary_text(self, selected_modes):
        """Get summary text for modes"""
        if not selected_modes:
            return "No modes selected"
        
        if len(selected_modes) == 1:
            return f"Single mode: {self.get_mode_display_name(selected_modes[0])}"
        else:
            return f"Multi-mode: {len(selected_modes)} modes selected"
    
    def should_show_endpoint_info(self, mode_code):
        """Check if endpoint info should be shown for mode"""
        return mode_code != 'save_only'