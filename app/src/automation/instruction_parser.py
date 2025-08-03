# app/src/automation/instruction_parser.py
import re

class InstructionParser:
    """Handles parsing of Trello card instructions and processing mode detection"""
    
    def parse_card_instructions(self, card_description):
        """Parse the card description using a standardized approach."""
        desc_lower = card_description.lower()
        
        print(f"Parsing card description: {card_description[:100]}...")
        
        # PRIORITY 1: Check for "save as is" or "save as" first (most important)
        save_patterns = [
            "save as is",
            "save as", 
            "save them as is",
            "save it as is",
            "just save"
        ]
        
        for pattern in save_patterns:
            if pattern in desc_lower:
                print(f"Detected 'save as is' pattern: '{pattern}' - will only rename and save files")
                return "save_only"
        
        # PRIORITY 2: Look for EXPLICIT "no connector" or "only quiz" instructions
        no_connector_patterns = [
            "no need.*connector",
            "only.*quiz",
            "connect only to quiz", 
            "quiz.*no.*connector",
            "without.*connector",
            "skip.*connector",
            "bypass.*connector"
        ]
        
        for pattern in no_connector_patterns:
            if re.search(pattern, desc_lower):
                print(f"Detected 'quiz only' pattern: '{pattern}' - will add quiz only")
                return "quiz_only"
        
        # PRIORITY 3: Look for combination patterns (connector + quiz)
        quiz_connector_patterns = [
            "quiz outro.*connector",
            "connector.*quiz outro", 
            "quiz.*blake connector",
            "blake connector.*quiz",
            "combine.*quiz.*connector",
            "combine.*connector.*quiz",
            "with.*connector.*quiz",
            "connector.*and.*quiz"
        ]
        
        for pattern in quiz_connector_patterns:
            if re.search(pattern, desc_lower):
                print(f"Detected quiz + connector pattern: '{pattern}' - will add connector + quiz")
                return "connector_quiz"
        
        # PRIORITY 4: Look for general processing instructions
        processing_verbs = ["combine", "connect", "add", "merge", "stitch", "join", "attach"]
        quiz_keywords = ["quiz", "outro"]
        
        # Don't trigger on "quiz funnel" mentions
        if "quiz funnel" in desc_lower or "testing queue" in desc_lower:
            print("Detected 'quiz funnel' or 'testing queue' - defaulting to save only")
            return "save_only"
        
        has_processing_verb = any(verb in desc_lower for verb in processing_verbs)
        has_quiz_keyword = any(keyword in desc_lower for keyword in quiz_keywords)
        
        if has_processing_verb and has_quiz_keyword:
            # Default to quiz only unless connector is explicitly mentioned
            if "connector" in desc_lower or "blake" in desc_lower:
                print("Detected processing verb + quiz + connector - will add connector + quiz")
                return "connector_quiz"
            else:
                print("Detected processing verb + quiz (no connector mentioned) - will add quiz only")
                return "quiz_only"
        
        # PRIORITY 5: Default fallback
        print("No specific processing instructions found - defaulting to save only")
        return "save_only"