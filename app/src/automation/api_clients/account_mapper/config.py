# app/src/automation/api_clients/account_mapper/config.py

# Account mapping - codes to display names
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

# Platform mapping - codes to display names
PLATFORM_MAPPING = {
    'FB': 'Facebook',
    'YT': 'YouTube',
    'IG': 'Instagram', 
    'TT': 'TikTok',
    'SNAP': 'Snapchat'
}

# FIXED: Enhanced platform detection mappings
PLATFORM_DETECTION_MAPPINGS = {
    # Input variations -> Standard code
    'FB': 'FB',
    'FACEBOOK': 'FB',
    'YT': 'YT',
    'YOUTUBE': 'YT',
    'IG': 'IG', 
    'INSTAGRAM': 'IG',
    'TT': 'TT',
    'TIKTOK': 'TT',
    'SNAP': 'SNAP',
    'SNAPCHAT': 'SNAP',  # FIXED: Add SNAPCHAT mapping
    'SNAP-CHAT': 'SNAP'
}

# FIXED: Worksheet name mappings (for Google Sheets)
WORKSHEET_NAME_MAPPINGS = {
    # Standard format: Account + " - " + Worksheet Platform Name
    'SNAP': 'Snapchat',  # SNAP code maps to "Snapchat" in worksheet names
    'FB': 'FB',
    'YT': 'YT', 
    'IG': 'IG',
    'TT': 'TT'
}

# Smart detection keywords for account detection
ACCOUNT_KEYWORDS = {
    'bc3': 'BC3',
    'bio complete': 'BC3',
    'biocomplete': 'BC3',
    'total restore': 'TR',
    'totalrestore': 'TR',
    'olive oil': 'OO',
    'oliveoil': 'OO',
    'mct': 'MCT',
    'dark spot': 'DS',
    'darkspot': 'DS',
    'morning kick': 'MK',
    'morningkick': 'MK',
}

# Smart detection keywords for platform detection  
PLATFORM_KEYWORDS = {
    'facebook': 'FB',
    'fb': 'FB',
    'youtube': 'YT',
    'yt': 'YT',
    'instagram': 'IG',
    'ig': 'IG',
    'tiktok': 'TT',
    'tt': 'TT',
    'snapchat': 'SNAP',  # FIXED: Add snapchat detection
    'snap': 'SNAP'
}