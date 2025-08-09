# app/src/automation/instruction_parser.py
# Updated to detect SVSL and VSL processing modes

import re

class InstructionParser:
    """Parser for detecting processing modes from Trello card descriptions"""
    
    def __init__(self):
        # Define priority patterns for different processing modes
        self.save_patterns = [
            r"save\s+as\s+is",
            r"save\s+them\s+as\s+is",
            r"just\s+save",
            r"save\s+and\s+rename",
            r"rename\s+only",
            r"no\s+processing"
        ]
        
        self.quiz_patterns = [
            r"attach\s+to\s+quiz",
            r"connect\s+to\s+quiz(?!\s+and)",
            r"add\s+quiz\s+outro",
            r"quiz\s+outro\s+only",
            r"only\s+quiz",
            r"just\s+quiz"
        ]
        
        self.connector_quiz_patterns = [
            r"connect\s+to\s+connector\s+and\s+quiz",
            r"connector\s+\+\s+quiz",
            r"add\s+connector\s+and\s+quiz",
            r"connector\s+plus\s+quiz",
            r"blake\s+connector.*quiz"
        ]
        
        # New SVSL patterns
        self.svsl_patterns = [
            r"attach\s+to\s+svsl",
            r"connect\s+to\s+svsl(?!\s+and)",
            r"add\s+svsl",
            r"svsl\s+only",
            r"only\s+svsl",
            r"just\s+svsl"
        ]
        
        self.connector_svsl_patterns = [
            r"connect\s+to\s+connector\s+and\s+svsl",
            r"connector\s+\+\s+svsl",
            r"add\s+connector\s+and\s+svsl",
            r"connector\s+plus\s+svsl",
            r"blake\s+connector.*svsl"
        ]
        
        # New VSL patterns
        self.vsl_patterns = [
            r"attach\s+to\s+vsl",
            r"connect\s+to\s+vsl(?!\s+and)",
            r"add\s+vsl",
            r"vsl\s+only",
            r"only\s+vsl",
            r"just\s+vsl"
        ]
        
        self.connector_vsl_patterns = [
            r"connect\s+to\s+connector\s+and\s+vsl",
            r"connector\s+\+\s+vsl",
            r"add\s+connector\s+and\s+vsl",
            r"connector\s+plus\s+vsl",
            r"blake\s+connector.*vsl"
        ]
    
    def parse_card_instructions(self, description: str) -> str:
        """
        Parse Trello card description to determine processing mode
        
        Priority order:
        1. Save as is (highest priority)
        2. Connector + Quiz/SVSL/VSL
        3. Quiz/SVSL/VSL only
        4. Default to quiz_only if processing keywords found
        5. Default to save_only if no clear instruction
        
        Returns:
            One of: "save_only", "quiz_only", "connector_quiz",
                   "svsl_only", "connector_svsl", "vsl_only", "connector_vsl"
        """
        description_lower = description.lower()
        
        # Priority 1: Check for save-only patterns
        if self._check_patterns(description_lower, self.save_patterns):
            print("📋 Detected: SAVE ONLY mode")
            return "save_only"
        
        # Priority 2: Check for connector + endpoint patterns
        if self._check_patterns(description_lower, self.connector_quiz_patterns):
            print("📋 Detected: CONNECTOR + QUIZ mode")
            return "connector_quiz"
        
        if self._check_patterns(description_lower, self.connector_svsl_patterns):
            print("📋 Detected: CONNECTOR + SVSL mode")
            return "connector_svsl"
        
        if self._check_patterns(description_lower, self.connector_vsl_patterns):
            print("📋 Detected: CONNECTOR + VSL mode")
            return "connector_vsl"
        
        # Priority 3: Check for endpoint-only patterns
        if self._check_patterns(description_lower, self.quiz_patterns):
            print("📋 Detected: QUIZ ONLY mode")
            return "quiz_only"
        
        if self._check_patterns(description_lower, self.svsl_patterns):
            print("📋 Detected: SVSL ONLY mode")
            return "svsl_only"
        
        if self._check_patterns(description_lower, self.vsl_patterns):
            print("📋 Detected: VSL ONLY mode")
            return "vsl_only"
        
        # Check for general processing keywords
        processing_keywords = ["process", "edit", "render", "export", "quiz", "connector", "svsl", "vsl"]
        has_processing_keyword = any(keyword in description_lower for keyword in processing_keywords)
        
        if has_processing_keyword:
            # Default to quiz_only if processing is mentioned but no specific mode detected
            print("📋 Processing keywords found, defaulting to: QUIZ ONLY mode")
            return "quiz_only"
        
        # Default fallback
        print("📋 No clear instructions found, defaulting to: SAVE ONLY mode")
        return "save_only"
    
    def _check_patterns(self, text: str, patterns: list) -> bool:
        """Check if any pattern matches in the text"""
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def get_processing_mode_display(self, mode: str) -> str:
        """Get a human-readable display name for the processing mode"""
        mode_displays = {
            "save_only": "Save As Is",
            "quiz_only": "Add Quiz Outro",
            "connector_quiz": "Add Connector + Quiz",
            "svsl_only": "Add SVSL",
            "connector_svsl": "Add Connector + SVSL",
            "vsl_only": "Add VSL",
            "connector_vsl": "Add Connector + VSL"
        }
        return mode_displays.get(mode, mode.replace('_', ' ').title())