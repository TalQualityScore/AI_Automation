# app/src/automation/api_clients/account_mapper/dialog_modules/dialog_constants.py
"""
Dialog Constants Module
Contains all mappings and constants for the dialog
"""

class DialogConstants:
    """Constants and mappings for the fallback dialog"""
    
    # Window settings
    WINDOW_WIDTH = 500
    WINDOW_HEIGHT = 500
    WINDOW_TITLE = "⚠️ Verification Required"
    
    # Colors
    BG_COLOR = 'white'
    HEADER_COLOR = '#d9534f'
    TEXT_COLOR = '#333'
    SUBTITLE_COLOR = '#666'
    BUTTON_SUCCESS_COLOR = '#28a745'
    
    # Fonts
    HEADER_FONT = ('Segoe UI', 16, 'bold')
    INSTRUCTION_FONT = ('Segoe UI', 11)
    LABEL_FONT = ('Segoe UI', 11, 'bold')
    COMBO_FONT = ('Segoe UI', 10)
    BUTTON_FONT = ('Segoe UI', 12, 'bold')
    CONTEXT_FONT = ('Segoe UI', 9)
    
    # Timeouts
    MAX_WAIT_TIME = 120  # 2 minutes
    POLL_INTERVAL = 0.1  # 100ms
    
    # Account mapping
    ACCOUNT_MAPPING = {
        'TR': 'Total Restore',
        'BC3': 'Bio Complete 3',
        'OO': 'Olive Oil',
        'MCT': 'MCT',
        'DS': 'Dark Spot',
        'NB': 'Nature\'s Blend',
        'MK': 'Morning Kick',
        'DRC': 'Dermal Repair Complex',
        'PC': 'Phyto Collagen',
        'GD': 'Glucose Defense',
        'MC': 'Morning Complete',
        'PP': 'Pro Plant',
        'SPC': 'Superfood Complete',
        'MA': 'Metabolic Advanced',
        'KA': 'Keto Active',
        'BLR': 'BadLand Ranch',
        'Bio X4': 'Bio X4',
        'Upwellness': 'Upwellness'
    }
    
    # Platform mapping
    PLATFORM_MAPPING = {
        'FB': 'Facebook',
        'YT': 'YouTube',
        'IG': 'Instagram',
        'TT': 'TikTok',
        'SNAP': 'Snapchat'
    }
    
    @classmethod
    def get_account_options(cls):
        """Get formatted account options for dropdown"""
        return [f"{code} - {name}" for code, name in cls.ACCOUNT_MAPPING.items()]
    
    @classmethod
    def get_platform_options(cls):
        """Get formatted platform options for dropdown"""
        return [f"{code} - {name}" for code, name in cls.PLATFORM_MAPPING.items()]
    
    @classmethod
    def get_default_account(cls, detected_account=None):
        """Get default account selection"""
        if detected_account and detected_account in cls.ACCOUNT_MAPPING:
            return f"{detected_account} - {cls.ACCOUNT_MAPPING[detected_account]}"
        return "TR - Total Restore"
    
    @classmethod
    def get_default_platform(cls, detected_platform=None):
        """Get default platform selection"""
        if detected_platform and detected_platform in cls.PLATFORM_MAPPING:
            return f"{detected_platform} - {cls.PLATFORM_MAPPING[detected_platform]}"
        return "FB - Facebook"