# app/src/automation/instruction_parser.py
# ENHANCED - Add multi-mode detection while keeping existing single-mode logic

import re

class InstructionParser:
    """Parser for detecting processing modes from Trello card descriptions"""
    
    def __init__(self):
        # Keep all existing pattern definitions unchanged
        self.critical_vsl_patterns = [
            r"connect\s+to\s+an?\s+vsl",              # "connect to an VSL" or "connect to a VSL"
            r"please\s+connect\s+to\s+an?\s+vsl",     # "please connect to an VSL"
            r"attach\s+to\s+an?\s+vsl",               # "attach to a VSL"
        ]
        
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
            r"just\s+quiz",
            r"quiz\s+funnel",           # NEW: Added for your card
            r"quiz\s+male\s+outro"      # NEW: Added for your card
        ]
        
        self.connector_quiz_patterns = [
            r"connect\s+to\s+connector\s+and\s+quiz",
            r"connector\s+\+\s+quiz",
            r"add\s+connector\s+and\s+quiz",
            r"connector\s+plus\s+quiz",
            r"blake\s+connector.*quiz"
        ]
        
        self.svsl_patterns = [
            r"attach\s+to\s+svsl",
            r"connect\s+to\s+svsl(?!\s+and)",
            r"add\s+svsl",
            r"svsl\s+only",
            r"only\s+svsl",
            r"just\s+svsl",
            r"combine\s+.*with\s+.*svsl",
            r"combine\s+.*svsl"
        ]
        
        self.connector_svsl_patterns = [
            r"connect\s+to\s+connector\s+and\s+svsl",
            r"connector\s+\+\s+svsl",
            r"add\s+connector\s+and\s+svsl",
            r"connector\s+plus\s+svsl",
            r"blake\s+connector.*svsl"
        ]
        
        self.vsl_patterns = [
            r"attach\s+to\s+vsl",
            r"connect\s+to\s+vsl(?!\s+and)",
            r"add\s+vsl",
            r"vsl\s+only",
            r"only\s+vsl",
            r"just\s+vsl",
            # CRITICAL: These patterns match your cards
            r"combine\s+.*with\s+.*vsl",           # "combine the three standalone versions with our VSL"
            r"combine\s+.*vsl",                    # "combine with VSL" 
            r"combine\s+.*with\s+our\s+vsl",       # "combine with our VSL"
            r"combine\s+.*versions\s+with\s+.*vsl", # "combine versions with VSL"
            r"combine\s+the\s+.*with\s+.*vsl",     # "combine the ... with VSL"
            r"standalone\s+versions\s+with\s+.*vsl" # "standalone versions with our VSL"
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
        EXISTING METHOD - Keep unchanged for backward compatibility
        Parse Trello card description to determine processing mode
        """
        description_lower = description.lower()
        
        print(f"🔍 PARSING INSTRUCTIONS: '{description[:100]}...'")
        
        # CRITICAL: Check for high-priority VSL patterns FIRST
        if self._check_patterns(description_lower, self.critical_vsl_patterns):
            print("📋 Detected: VSL ONLY mode (Critical Pattern Match)")
            return "vsl_only"
        
        # Priority 1: Check for connector + endpoint patterns
        if self._check_patterns(description_lower, self.connector_quiz_patterns):
            print("📋 Detected: CONNECTOR + QUIZ mode")
            return "connector_quiz"
        
        if self._check_patterns(description_lower, self.connector_svsl_patterns):
            print("📋 Detected: CONNECTOR + SVSL mode")
            return "connector_svsl"
        
        if self._check_patterns(description_lower, self.connector_vsl_patterns):
            print("📋 Detected: CONNECTOR + VSL mode")
            return "connector_vsl"
        
        # Priority 2: Check for endpoint-only patterns
        # IMPORTANT: Check VSL FIRST (before quiz) since VSL is more specific
        if self._check_patterns(description_lower, self.vsl_patterns):
            print("📋 Detected: VSL ONLY mode")
            return "vsl_only"
        
        if self._check_patterns(description_lower, self.svsl_patterns):
            print("📋 Detected: SVSL ONLY mode")
            return "svsl_only"
        
        if self._check_patterns(description_lower, self.quiz_patterns):
            print("📋 Detected: QUIZ ONLY mode")
            return "quiz_only"
        
        # Priority 3: Check for save-only patterns (MOVED LATER)
        if self._check_patterns(description_lower, self.save_patterns):
            print("📋 Detected: SAVE ONLY mode")
            return "save_only"
        
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
    
    def parse_card_instructions_multi(self, description: str) -> list:
        """
        NEW METHOD - Multi-mode detection
        Returns list of detected processing modes
        """
        description_lower = description.lower()
        detected_modes = []
        
        print(f"🔍 MULTI-MODE PARSING: '{description[:100]}...'")
        
        # Check for connector combinations first (these are mutually exclusive)
        if self._check_patterns(description_lower, self.connector_quiz_patterns):
            detected_modes.append("connector_quiz")
            print("📋 Detected: CONNECTOR + QUIZ mode")
        
        if self._check_patterns(description_lower, self.connector_svsl_patterns):
            detected_modes.append("connector_svsl")
            print("📋 Detected: CONNECTOR + SVSL mode")
        
        if self._check_patterns(description_lower, self.connector_vsl_patterns):
            detected_modes.append("connector_vsl")
            print("📋 Detected: CONNECTOR + VSL mode")
        
        # If no connector combinations found, check for individual modes
        if not detected_modes:
            # Check for critical VSL patterns first
            if self._check_patterns(description_lower, self.critical_vsl_patterns):
                detected_modes.append("vsl_only")
                print("📋 Detected: VSL ONLY mode (Critical Pattern)")
            
            # Check for regular patterns - CAN DETECT MULTIPLE
            if self._check_patterns(description_lower, self.vsl_patterns):
                if "vsl_only" not in detected_modes:
                    detected_modes.append("vsl_only")
                    print("📋 Detected: VSL ONLY mode")
            
            if self._check_patterns(description_lower, self.quiz_patterns):
                detected_modes.append("quiz_only")
                print("📋 Detected: QUIZ ONLY mode")
            
            if self._check_patterns(description_lower, self.svsl_patterns):
                detected_modes.append("svsl_only")
                print("📋 Detected: SVSL ONLY mode")
            
            # Check for save patterns only if no processing modes found
            if not detected_modes and self._check_patterns(description_lower, self.save_patterns):
                detected_modes.append("save_only")
                print("📋 Detected: SAVE ONLY mode")
        
        # Default fallback
        if not detected_modes:
            detected_modes.append("save_only")
            print("📋 No clear instructions found, defaulting to: SAVE ONLY mode")
        
        print(f"✅ FINAL MODES DETECTED: {detected_modes}")
        return detected_modes
    
    def _check_patterns(self, text: str, patterns: list) -> bool:
        """Check if any pattern matches in the text - UNCHANGED"""
        for pattern in patterns:
            if re.search(pattern, text):
                print(f"✅ MATCHED PATTERN: '{pattern}' in text")
                return True
        return False
    
    def get_processing_mode_display(self, mode: str) -> str:
        """Get a human-readable display name for the processing mode - UNCHANGED"""
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
    
    def get_processing_modes_display(self, modes: list) -> list:
        """NEW METHOD - Get display names for multiple modes"""
        return [self.get_processing_mode_display(mode) for mode in modes]
    
    def debug_pattern_matching(self, description: str) -> dict:
        """Debug function to test all patterns against description - UNCHANGED"""
        description_lower = description.lower()
        results = {}
        
        pattern_groups = {
            'critical_vsl': self.critical_vsl_patterns,
            'save': self.save_patterns,
            'quiz': self.quiz_patterns,
            'connector_quiz': self.connector_quiz_patterns,
            'svsl': self.svsl_patterns,
            'connector_svsl': self.connector_svsl_patterns,
            'vsl': self.vsl_patterns,
            'connector_vsl': self.connector_vsl_patterns
        }
        
        for group_name, patterns in pattern_groups.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    matches.append(pattern)
            results[group_name] = matches
        
        return results