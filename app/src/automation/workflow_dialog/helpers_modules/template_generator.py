# app/src/automation/workflow_dialog/helpers_modules/template_generator.py
"""
Template Generator Module
Generates processing templates based on mode and platform
"""

class TemplateGenerator:
    """Generates template descriptions for different processing modes"""
    
    def generate_templates(self, processing_mode, platform):
        """
        Generate template list based on processing mode
        
        Args:
            processing_mode: The processing mode string
            platform: Platform name (e.g., "Facebook")
            
        Returns:
            List of template description strings
        """
        
        templates = []
        
        if processing_mode == "connector_quiz":
            templates = [
                f"Add Blake connector ({platform}/Connectors/) with slide transition",
                f"Add quiz outro ({platform}/Quiz/) with slide transition",
                "Apply professional slide transitions between segments"
            ]
        
        elif processing_mode == "quiz_only":
            templates = [
                f"Add quiz outro ({platform}/Quiz/) with slide transition",
                "Apply professional slide transitions"
            ]
        
        elif processing_mode == "connector_svsl":
            templates = [
                f"Add Blake connector ({platform}/Connectors/) with slide transition",
                f"Add SVSL ({platform}/SVSL/) with slide transition",
                "Apply professional slide transitions between segments"
            ]
        
        elif processing_mode == "svsl_only":
            templates = [
                f"Add SVSL ({platform}/SVSL/) with slide transition",
                "Apply professional slide transitions"
            ]
        
        elif processing_mode == "connector_vsl":
            templates = [
                f"Add Blake connector ({platform}/Connectors/) with slide transition",
                f"Add VSL ({platform}/VSL/) with slide transition",
                "Apply professional slide transitions between segments"
            ]
        
        elif processing_mode == "vsl_only":
            templates = [
                f"Add VSL ({platform}/VSL/) with slide transition",
                "Apply professional slide transitions"
            ]
        
        elif processing_mode == "save_only":
            templates = ["Save and rename videos (no processing)"]
        
        else:
            templates = ["Unknown processing mode"]
        
        return templates
    
    def get_endpoint_type(self, processing_mode):
        """Get the endpoint type from processing mode"""
        
        if "quiz" in processing_mode:
            return "quiz"
        elif "svsl" in processing_mode:
            return "svsl"
        elif "vsl" in processing_mode:
            return "vsl"
        else:
            return "quiz"  # Default