# app/src/automation/api_clients/__init__.py
"""
API Clients Module - Refactored with Backward Compatibility

This module provides a clean, modular API client architecture while maintaining
backward compatibility with existing imports.

Usage:
    # New modular usage (recommended)
    from .trello_client import TrelloClient
    from .google_drive_client import GoogleDriveClient
    from .google_sheets_client import GoogleSheetsClient
    
    # Legacy usage (still works)
    from . import get_trello_card_data, download_files_from_gdrive, write_to_google_sheets
"""

from .config import get_google_creds, ACCOUNT_MAPPING, PLATFORM_MAPPING
from .trello_client import TrelloClient
from .google_drive_client import GoogleDriveClient
from .google_sheets_client import GoogleSheetsClient
from .account_mapper import AccountMapper

# Backward Compatibility Functions
# These maintain the original function signatures for existing code

def get_trello_card_data(card_id: str):
    """
    LEGACY FUNCTION: Backward compatibility wrapper
    Use TrelloClient.get_card_data() for new code
    """
    client = TrelloClient()
    return client.get_card_data(card_id)

def download_files_from_gdrive(folder_url: str, creds, monitor=None):
    """
    LEGACY FUNCTION: Backward compatibility wrapper  
    Use GoogleDriveClient.download_files_from_folder() for new code
    """
    client = GoogleDriveClient(creds)
    return client.download_files_from_folder(folder_url, monitor)

def write_to_google_sheets(concept_name: str, data_rows: list, creds):
    """
    LEGACY FUNCTION: Backward compatibility wrapper
    Use GoogleSheetsClient.write_to_sheet() for new code
    """
    client = GoogleSheetsClient(creds)
    return client.write_to_sheet(concept_name, data_rows, creds)

def find_correct_worksheet(concept_name: str, creds):
    """
    LEGACY FUNCTION: Backward compatibility wrapper
    Use GoogleSheetsClient.find_correct_worksheet() for new code
    """
    client = GoogleSheetsClient(creds)
    worksheet, error = client.find_correct_worksheet(concept_name)
    return worksheet, error

# Export all components for clean imports
__all__ = [
    # Configuration
    'get_google_creds',
    'ACCOUNT_MAPPING',
    'PLATFORM_MAPPING',
    
    # New Modular Classes (Recommended)
    'TrelloClient',
    'GoogleDriveClient', 
    'GoogleSheetsClient',
    'AccountMapper',
    
    # Legacy Functions (Backward Compatibility)
    'get_trello_card_data',
    'download_files_from_gdrive', 
    'write_to_google_sheets',
    'find_correct_worksheet',
]

# Module Information
__version__ = "2.0.0"
__author__ = "AI Automation Suite"
__description__ = "Modular API clients for Trello, Google Drive, and Google Sheets"

print("✅ API Clients v2.0.0 loaded - Modular architecture with backward compatibility")