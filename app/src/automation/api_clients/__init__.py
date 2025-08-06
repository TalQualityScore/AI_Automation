# app/src/automation/api_clients/__init__.py - UPDATED WITH CUSTOM NAMES

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

def write_to_google_sheets_with_custom_name(routing_name: str, column1_name: str, data_rows: list, creds):
    """
    NEW FUNCTION: Write to sheets with custom column 1 name
    Uses routing_name to find worksheet, column1_name for actual content
    """
    client = GoogleSheetsClient(creds)
    return client.write_to_sheet_with_custom_name(routing_name, column1_name, data_rows, creds)

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
    'write_to_google_sheets_with_custom_name',  # NEW
    'find_correct_worksheet',
]

# Module Information
__version__ = "2.1.0"
__author__ = "AI Automation Suite"
__description__ = "Modular API clients with custom naming support"

print("✅ API Clients v2.1.0 loaded - Custom naming support added")