# app/src/automation/api_clients.py - CORRECTED VERSION

import os
import re
import gspread
import requests
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# --- CONFIGURATION ---
load_dotenv()
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "credentials.json"
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
DOWNLOADS_DIR = "temp_downloads"

# CORRECTED account mapping to match worksheet format (Account - Platform)
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

def get_google_creds():
    """Initializes Google API credentials."""
    try:
        return Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    except FileNotFoundError:
        print(f"ERROR: Google credentials file not found at '{SERVICE_ACCOUNT_FILE}'.")
        return None

def get_trello_card_data(card_id):
    """Fetches card name, description, and G-Drive link from description."""
    url = f"https://api.trello.com/1/cards/{card_id}"
    query = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    try:
        response = requests.get(url, params=query, timeout=10)
        response.raise_for_status()
        card = response.json()
        
        card_name = card['name']
        card_desc = card['desc']
        
        gdrive_link_match = re.search(r'(https?://drive\.google\.com/drive/folders/[\w-]+)', card_desc)
        if not gdrive_link_match:
            return None, "Google Drive link not found in Trello card description."
        
        return {
            "name": card_name, 
            "desc": card_desc,
            "gdrive_url": gdrive_link_match.group(1)
        }, None
        
    except requests.exceptions.RequestException as e:
        return None, f"Trello API request failed: {e}"

def download_files_from_gdrive(folder_url, creds, monitor=None):
    """Downloads all video files from a Google Drive folder with activity monitoring."""
    if not creds: 
        return None, "Google credentials not available."
    
    try:
        if monitor:
            monitor.update_activity("Connecting to Google Drive...")
        
        drive_service = build("drive", "v3", credentials=creds)
        folder_id = folder_url.split('/')[-1]
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        
        if monitor:
            monitor.update_activity("Searching for video files...")
        
        query = f"'{folder_id}' in parents and mimeType contains 'video/'"
        results = drive_service.files().list(q=query, fields="files(id, name, size)").execute()
        items = results.get("files", [])
        
        if not items: 
            return None, "No video files found in the Google Drive folder."
        
        if monitor:
            monitor.update_activity(f"Found {len(items)} video files to download")
        
        downloaded_files = []
        for i, item in enumerate(items):
            file_id, file_name = item['id'], item['name']
            file_size = int(item.get('size', 0))
            local_path = os.path.join(DOWNLOADS_DIR, file_name)
            
            if monitor:
                monitor.update_activity(f"Starting download: {file_name}")
            
            print(f"Downloading {file_name}...")
            request = drive_service.files().get_media(fileId=file_id)
            
            with open(local_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                last_progress = 0
                
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        
                        if progress - last_progress >= 5 or done:
                            if monitor:
                                monitor.update_activity(f"Downloading {file_name}: {progress}%")
                            print(f"Download {progress}%.")
                            last_progress = progress
            
            downloaded_files.append(local_path)
            
            if monitor:
                monitor.update_activity(f"Completed: {file_name} ({i+1}/{len(items)})")
        
        if monitor:
            monitor.update_activity(f"All downloads completed: {len(downloaded_files)} files")
        
        return downloaded_files, None
        
    except HttpError as e:
        return None, f"Google Drive API error: {e}"
    except Exception as e:
        return None, f"Unexpected download error: {e}"

def find_correct_worksheet(concept_name, creds):
    """CORRECTED: Match exact worksheet format 'Account - Platform'"""
    if not creds: 
        return None, "Google credentials not available."
    
    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        
        # Extract account and platform from concept name
        account_code, platform = _extract_account_and_platform_corrected(concept_name)
        
        print(f"🔍 CORRECTED DETECTION - Account: '{account_code}', Platform: '{platform}'")
        print(f"🔍 Full concept name: '{concept_name}'")
        
        # Get all worksheet titles
        worksheets = spreadsheet.worksheets()
        worksheet_titles = [ws.title for ws in worksheets]
        
        print(f"📋 Available worksheets: {worksheet_titles}")
        
        # Look for exact match in format "Account - Platform"
        target_worksheet = _find_exact_worksheet_match(worksheet_titles, account_code, platform)
        
        if target_worksheet:
            print(f"✅ EXACT MATCH FOUND: '{target_worksheet}'")
            return spreadsheet.worksheet(target_worksheet), None
        else:
            print(f"⚠️ No exact match found, using first worksheet: '{worksheet_titles[0]}'")
            return spreadsheet.worksheet(worksheet_titles[0]), None
            
    except Exception as e:
        return None, f"Error finding correct worksheet: {e}"

def _extract_account_and_platform_corrected(concept_name):
    """CORRECTED: Extract from card title format 'BC3 FB - New Ads from...'"""
    
    print(f"🔍 ANALYZING CONCEPT: '{concept_name}'")
    
    # Extract the prefix before " - " (e.g., "BC3 FB" from "BC3 FB - New Ads from...")
    if " - " in concept_name:
        prefix = concept_name.split(" - ")[0].strip()
        print(f"🔍 EXTRACTED PREFIX: '{prefix}'")
        
        # Split prefix into account and platform
        parts = prefix.split()
        if len(parts) >= 2:
            account_code = parts[0]  # "BC3"
            platform = parts[1]      # "FB"
            print(f"✅ PARSED: Account='{account_code}', Platform='{platform}'")
            return account_code, platform
        elif len(parts) == 1:
            # Only account provided, default to YT
            account_code = parts[0]
            platform = "YT"
            print(f"✅ SINGLE PART: Account='{account_code}', Platform='{platform}' (defaulted)")
            return account_code, platform
    
    # Fallback: try to detect from anywhere in the concept name
    print(f"⚠️ FALLBACK DETECTION")
    concept_upper = concept_name.upper()
    
    # Account detection
    account_code = "UNKNOWN"
    for code in sorted(ACCOUNT_MAPPING.keys(), key=len, reverse=True):
        if code in concept_upper:
            account_code = code
            print(f"✅ FALLBACK Account detected: {code}")
            break
    
    # Platform detection
    platform = "YT"  # Default
    if "FB" in concept_upper or "FACEBOOK" in concept_upper:
        platform = "FB"
    elif "YT" in concept_upper or "YOUTUBE" in concept_upper:
        platform = "YT"
    
    print(f"🎯 FINAL: Account='{account_code}', Platform='{platform}'")
    return account_code, platform

def _find_exact_worksheet_match(worksheet_titles, account_code, platform):
    """CORRECTED: Find exact match for 'Account - Platform' format"""
    
    # Get the display name for the account
    display_name = ACCOUNT_MAPPING.get(account_code, account_code)
    
    # Try exact format: "Account - Platform"
    target_format = f"{display_name} - {platform}"
    
    print(f"🎯 LOOKING FOR EXACT MATCH: '{target_format}'")
    
    for worksheet_title in worksheet_titles:
        if worksheet_title == target_format:
            print(f"✅ EXACT MATCH FOUND: '{worksheet_title}'")
            return worksheet_title
    
    print(f"❌ NO EXACT MATCH FOUND")
    return None

def write_to_google_sheets(concept_name, data_rows, creds):
    """CORRECTED: Always add to end with proper formatting"""
    if not creds: 
        return "Google credentials not available.", 1
    
    try:
        # Find the correct worksheet
        sheet, error = find_correct_worksheet(concept_name, creds)
        if error:
            return error, 1
        
        print(f"📝 Writing to worksheet: '{sheet.title}'")
        
        if not data_rows: 
            return None, 1  # Return version 1 if no data to write
        
        # Find the absolute last row with any content
        all_values = sheet.get_all_values()
        last_content_row = 0
        for i, row in enumerate(all_values):
            if any(cell.strip() for cell in row if cell):
                last_content_row = i + 1
        
        # Always insert at end
        insert_row_index = last_content_row + 1
        print(f"📝 Adding new project at row {insert_row_index}")
        
        # Get starting version number (simplified)
        start_version = 1
        
        # Prepare data with correct column structure
        rows_to_insert = []
        for i, row in enumerate(data_rows):
            if i == 0:
                rows_to_insert.append([concept_name] + row)
            else:
                rows_to_insert.append([""] + row)
        
        print(f"📝 Inserting {len(rows_to_insert)} rows starting at row {insert_row_index}")
        
        # Write data using individual cell updates
        for row_offset, row_data in enumerate(rows_to_insert):
            current_row = insert_row_index + row_offset
            for col_offset, cell_value in enumerate(row_data):
                if cell_value:
                    sheet.update_cell(current_row, col_offset + 1, str(cell_value))
        
        end_row_index = insert_row_index + len(rows_to_insert) - 1
        
        # Merge column A for the concept name (only for multiple rows)
        if len(rows_to_insert) > 1:
            try:
                merge_range = f'A{insert_row_index}:A{end_row_index}'
                print(f"📝 Merging cells: {merge_range}")
                sheet.merge_cells(merge_range)
            except Exception as merge_error:
                print(f"⚠️ Warning: Could not merge cells: {merge_error}")
        
        # Apply formatting
        try:
            # Top border
            top_border_range = f'A{insert_row_index}:D{insert_row_index}'
            sheet.format(top_border_range, {
                "borders": {
                    "top": {"style": "SOLID_THICK", "color": {"red": 0, "green": 0, "blue": 0}}
                }
            })
            
            # Bottom border
            bottom_border_range = f'A{end_row_index}:D{end_row_index}'
            sheet.format(bottom_border_range, {
                "borders": {
                    "bottom": {"style": "SOLID_THICK", "color": {"red": 0, "green": 0, "blue": 0}}
                }
            })
            
            # Vertical alignment and text wrapping for merged cells
            if len(rows_to_insert) > 1:
                merged_cell_range = f'A{insert_row_index}:A{end_row_index}'
                sheet.format(merged_cell_range, {
                    "verticalAlignment": "MIDDLE",
                    "wrapStrategy": "WRAP",
                    "textFormat": {"bold": False}
                })
                print(f"✅ Applied formatting with vertical alignment and text wrapping")
            
        except Exception as format_error:
            print(f"⚠️ Warning: Could not format: {format_error}")
        
        print(f"✅ Successfully added {len(rows_to_insert)} rows to worksheet '{sheet.title}'")
        return None, start_version
        
    except Exception as e:
        return f"An unexpected Google Sheets error occurred: {e}", 1