# app/src/automation/instruction_parser.py
# MINIMAL FIX - Just add critical VSL patterns and reorder priority

import re

class InstructionParser:
    """Parser for detecting processing modes from Trello card descriptions"""
    
    def __init__(self):
        # Define priority patterns for different processing modes
        
        # NEW: Critical VSL patterns that should be checked FIRST
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
            r"just\s+quiz"
        ]
        
        self.connector_quiz_patterns = [
            r"connect\s+to\s+connector\s+and\s+quiz",
            r"connector\s+\+\s+quiz",
            r"add\s+connector\s+and\s+quiz",
            r"connector\s+plus\s+quiz",
            r"blake\s+connector.*quiz"
        ]
        
        # Enhanced SVSL patterns
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
        
        # COMPREHENSIVE VSL patterns - covers all variations
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
        Parse Trello card description to determine processing mode
        
        FIXED Priority order:
        1. Critical VSL patterns (NEW - checked FIRST)
        2. Connector + Quiz/SVSL/VSL
        3. Quiz/SVSL/VSL only
        4. Save as is (moved later)
        5. Default to quiz_only if processing keywords found
        6. Default to save_only if no clear instruction
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
    
    def _check_patterns(self, text: str, patterns: list) -> bool:
        """Check if any pattern matches in the text"""
        for pattern in patterns:
            if re.search(pattern, text):
                print(f"✅ MATCHED PATTERN: '{pattern}' in text")
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
    
    def debug_pattern_matching(self, description: str) -> dict:
        """Debug function to test all patterns against description"""
        description_lower = description.lower()
        results = {}
        
        pattern_groups = {
            'critical_vsl': self.critical_vsl_patterns,  # NEW
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