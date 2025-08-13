# app/src/automation/workflow_ui_components/confirmation_tab/project_section/dropdown_handlers.py
"""
Dropdown Handlers - Account/Platform Logic
Handles all dropdown-related data and selections
"""

class DropdownHandlers:
    """Handles account and platform dropdown logic"""
    
    def __init__(self, project_section):
        self.ps = project_section
    
    def get_account_options(self):
        """Get CORRECT account options from actual config.py"""
        return [
            "TR - Total Restore",
            "BC3 - Bio Complete 3",
            "OO - Olive Oil",
            "MCT - MCT",
            "DS - Dark Spot",
            "NB - Nature's Blend",
            "MK - Morning Kick",
            "DRC - Dermal Repair Complex",
            "PC - Phyto Collagen",
            "GD - Glucose Defense",
            "MC - Morning Complete",
            "PP - Pro Plant",
            "SPC - Superfood Complete",
            "MA - Metabolic Advanced",
            "KA - Keto Active",
            "BLR - BadLand Ranch",
            "Bio X4 - Bio X4",
            "Upwellness - Upwellness"
        ]
    
    def get_platform_options(self):
        """Platform options"""
        return [
            "FB - Facebook",
            "YT - YouTube",
            "IG - Instagram", 
            "TT - TikTok",
            "SNAP - Snapchat"
        ]
    
    def get_default_account_selection(self):
        """Get default account selection based on current data"""
        current_account = getattr(self.ps.data, 'account', 'TR')
        
        print(f"DEBUG: Looking for account code: {current_account}")
        
        for option in self.get_account_options():
            if option.startswith(current_account + ' - '):
                print(f"DEBUG: Found matching account: {option}")
                return option
        
        print(f"DEBUG: No match found for '{current_account}', using default TR - Total Restore")
        return "TR - Total Restore"
    
    def get_default_platform_selection(self):
        """Get default platform selection based on current data"""
        current_platform = getattr(self.ps.data, 'platform', 'FB')
        
        print(f"DEBUG: Looking for platform code: {current_platform}")
        
        for option in self.get_platform_options():
            if option.startswith(current_platform + ' - '):
                print(f"DEBUG: Found matching platform: {option}")
                return option
        
        print(f"DEBUG: No match found for '{current_platform}', using default FB - Facebook")
        return "FB - Facebook"
    
    def extract_code_from_selection(self, selection):
        """Extract code from 'CODE - Description' format"""
        if selection and ' - ' in selection:
            code = selection.split(' - ')[0]
            print(f"DEBUG: Extracted code '{code}' from selection '{selection}'")
            return code
        return selection
    
    def find_account_by_code(self, code):
        """Find account option by code"""
        for option in self.get_account_options():
            if option.startswith(code + ' - '):
                return option
        return None
    
    def find_platform_by_code(self, code):
        """Find platform option by code"""
        for option in self.get_platform_options():
            if option.startswith(code + ' - '):
                return option
        return None
    
    def get_account_codes(self):
        """Get list of just account codes"""
        return [option.split(' - ')[0] for option in self.get_account_options()]
    
    def get_platform_codes(self):
        """Get list of just platform codes"""
        return [option.split(' - ')[0] for option in self.get_platform_options()]
    
    def validate_account_code(self, code):
        """Validate if account code exists"""
        return code in self.get_account_codes()
    
    def validate_platform_code(self, code):
        """Validate if platform code exists"""
        return code in self.get_platform_codes()
    
    def get_account_display_name(self, code):
        """Get display name for account code"""
        for option in self.get_account_options():
            if option.startswith(code + ' - '):
                return option.split(' - ')[1]
        return code
    
    def get_platform_display_name(self, code):
        """Get display name for platform code"""
        for option in self.get_platform_options():
            if option.startswith(code + ' - '):
                return option.split(' - ')[1]
        return code