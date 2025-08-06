# app/src/automation/api_clients/config.py
"""
API Configuration and Constants
Centralized configuration for all API integrations
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- API CREDENTIALS ---
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# --- GOOGLE API CONFIGURATION ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets", 
    "https://www.googleapis.com/auth/drive"
]
SERVICE_ACCOUNT_FILE = "credentials.json"

# --- DOWNLOAD CONFIGURATION ---
DOWNLOADS_DIR = "temp_downloads"
DOWNLOAD_TIMEOUT = 600  # 10 minutes

# --- ACCOUNT MAPPING ---
# Maps account codes to display names in Google Sheets
ACCOUNT_MAPPING = {
    'BC3': 'BC3',
    'BLR': 'BLR', 
    'TR': 'TR',
    'PP': 'PP',
    'OO': 'Olive Oil',  # Special case - full name in sheets
    'NB': 'NB',
    'MK': 'MK',
    'DRC': 'DRC',
    'MCT': 'MCT',
    'PC': 'PC', 
    'GD': 'GD',
    'MC': 'MC',
    'DS': 'DS',
    'SPC': 'SPC',
    'MA': 'MA',
    'KA': 'KA',
    'Bio X4': 'Bio X4',
    'Upwellness': 'Upwellness',
}

# --- PLATFORM MAPPING ---
# Maps platform codes to display names
PLATFORM_MAPPING = {
    'FB': 'Facebook',
    'FACEBOOK': 'Facebook',
    'YT': 'YouTube',
    'YOUTUBE': 'YouTube',
    'SHORTS': 'YouTube Shorts',
    'TT': 'TikTok',
    'TIKTOK': 'TikTok',
    'SNAP': 'Snapchat',
    'SNAPCHAT': 'Snapchat',
    'IG': 'Instagram',
    'INSTAGRAM': 'Instagram',
    'INSTA': 'Instagram',
    'TWITTER': 'Twitter',
    'X': 'Twitter/X',
    'LINKEDIN': 'LinkedIn'
}

def get_google_creds():
    """Get Google API credentials"""
    try:
        from google.oauth2.service_account import Credentials
        return Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    except FileNotFoundError:
        print(f"ERROR: Google credentials file not found at '{SERVICE_ACCOUNT_FILE}'.")
        return None