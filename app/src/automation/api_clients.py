# app/src/automation/api_clients.py - COMPLETE FIXES

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

# COMPLETE account mapping for sheet detection
ACCOUNT_MAPPING = {
    'NB': 'Nature\'s Blend',
    'MK': 'Morning Kick',
    'DRC': 'Dermal Repair Complex',
    'TR': 'Total Restore',
    'MCT': 'MCT',
    'PC': 'Phyto Collagen', 
    'GD': 'Glucose Defense',
    'OO': 'Olive Oil',
    'MC': 'Morning Complete',
    'DS': 'Dark Spot',
    'BC3': 'Bio Complete 3',  # Key account for BC3 detection
    'PP': 'Pro Plant',
    'SPC': 'Superfood Complete',
    'MA': 'Metabolic Advanced',
    'KA': 'Keto Active',
    'BLR': 'BadLand Ranch',
    'Bio X4': 'Bio X4',
    'Upwellness': 'Upwellness',
    'MK ES': 'Morning Kick Espanol',
    'MCT ES': 'MCT Espanol', 
    'DS ES': 'Dark Spots Espanol',
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
                        
                        if progress - last_progress >= 5 or done:  # Every 5% or when done
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
    """COMPLETELY FIXED: Enhanced BC3 detection and platform parsing"""
    if not creds: 
        return None, "Google credentials not available."
    
    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        
        # COMPLETELY REWRITTEN: Better account and platform extraction
        account_code, platform = _extract_account_and_platform_fixed(concept_name)
        
        print(f"🔍 FIXED DETECTION - Account: '{account_code}', Platform: '{platform}'")
        print(f"🔍 Full concept name: '{concept_name}'")
        
        # Get all worksheet titles
        worksheets = spreadsheet.worksheets()
        worksheet_titles = [ws.title for ws in worksheets]
        
        print(f"📋 Available worksheets: {worksheet_titles}")
        
        # COMPLETELY REWRITTEN matching logic
        best_match = _find_best_worksheet_match_fixed(worksheet_titles, account_code, platform)
        
        if best_match:
            print(f"✅ FINAL SELECTION: '{best_match}'")
            return spreadsheet.worksheet(best_match), None
        else:
            print(f"⚠️ No match found, using first worksheet: '{worksheet_titles[0]}'")
            return spreadsheet.worksheet(worksheet_titles[0]), None
            
    except Exception as e:
        return None, f"Error finding correct worksheet: {e}"

def _extract_account_and_platform_fixed(concept_name):
    """FIXED: Force BC3 detection and look for FB in concept name"""
    
    concept_upper = concept_name.upper()
    print(f"🔍 DEBUGGING - Full concept: '{concept_name}'")
    print(f"🔍 DEBUGGING - Upper concept: '{concept_upper}'")
    
    # FORCE BC3 DETECTION - Check for BC3 patterns more aggressively
    account_code = "UNKNOWN"
    
    if "BC3" in concept_upper:
        account_code = "BC3"
        print(f"✅ BC3 DETECTED - Direct match")
    elif "BIO COMPLETE" in concept_upper:
        account_code = "BC3"
        print(f"✅ BC3 DETECTED - Bio Complete match")
    elif "BIOCOMPLETE" in concept_upper:
        account_code = "BC3"
        print(f"✅ BC3 DETECTED - BioComplete match")
    else:
        # Check other account codes
        for code in sorted(ACCOUNT_MAPPING.keys(), key=len, reverse=True):
            if code != "BC3" and code.upper() in concept_upper:
                account_code = code
                print(f"✅ Account code detected: {code}")
                break
    
    # ENHANCED PLATFORM DETECTION - Look harder for FB
    platform = "YT"  # Default
    
    # Check for Facebook indicators first (priority over YT default)
    if "FACEBOOK" in concept_upper or "FB" in concept_upper:
        platform = "FB"
        print(f"✅ Platform detected: FACEBOOK/FB -> FB")
    elif "YOUTUBE" in concept_upper or " YT " in concept_upper or concept_upper.endswith("YT"):
        platform = "YT"
        print(f"✅ Platform detected: YOUTUBE/YT -> YT")
    elif "SNAP" in concept_upper:
        platform = "SNAP"
        print(f"✅ Platform detected: SNAP -> SNAP")
    elif "TIKTOK" in concept_upper or " TT " in concept_upper:
        platform = "TT"
        print(f"✅ Platform detected: TIKTOK/TT -> TT")
    elif "INSTAGRAM" in concept_upper or " IG " in concept_upper:
        platform = "IG"
        print(f"✅ Platform detected: INSTAGRAM/IG -> IG")
    else:
        print(f"⚠️ No platform detected, defaulting to YT")
    
    print(f"🎯 FINAL DETECTION - Account: '{account_code}', Platform: '{platform}'")
    print(f"🎯 Looking for worksheet with: {account_code} + {platform}")
    
    return account_code, platform

def _find_best_worksheet_match_fixed(worksheet_titles, account_code, platform):
    """FIXED: Force BC3-FB matching with explicit checks"""
    
    print(f"🔍 FORCE MATCHING - Account: {account_code}, Platform: {platform}")
    print(f"🔍 Available worksheets: {worksheet_titles}")
    
    # SPECIAL CASE: If BC3 + FB, look explicitly for BC3 FB combinations
    if account_code == "BC3" and platform == "FB":
        print(f"🎯 SPECIAL BC3-FB CASE - Looking for BC3 + FB combinations")
        
        # Check for explicit BC3 FB matches first
        for title in worksheet_titles:
            title_upper = title.upper()
            if ("BC3" in title_upper or "BC" in title_upper or "BIO" in title_upper) and ("FB" in title_upper or "FACEBOOK" in title_upper):
                print(f"🎯 DIRECT BC3-FB MATCH FOUND: '{title}'")
                return title
        
        # If no direct match, look for BC3 sheets (any platform)
        for title in worksheet_titles:
            title_upper = title.upper()
            if "BC3" in title_upper or "BIO" in title_upper:
                print(f"🎯 BC3 FALLBACK MATCH: '{title}'")
                return title
    
    # Regular matching for other cases
    best_match = None
    best_score = 0
    
    for worksheet_title in worksheet_titles:
        score = 0
        title_upper = worksheet_title.upper()
        
        print(f"\n📊 SCORING '{worksheet_title}':")
        
        # Account matching (50 points)
        account_found = False
        if account_code == "BC3":
            if "BC3" in title_upper or "BC" in title_upper or "BIO" in title_upper:
                score += 50
                account_found = True
                print(f"   ✅ BC3 Account match (+50)")
        else:
            if account_code.upper() in title_upper:
                score += 50 
                account_found = True
                print(f"   ✅ Account match: {account_code} (+50)")
        
        # Platform matching (30 points)
        platform_found = False
        if platform == "FB" and ("FB" in title_upper or "FACEBOOK" in title_upper):
            score += 30
            platform_found = True
            print(f"   ✅ FB Platform match (+30)")
        elif platform == "YT" and ("YT" in title_upper or "YOUTUBE" in title_upper):
            score += 30
            platform_found = True
            print(f"   ✅ YT Platform match (+30)")
        elif platform.upper() in title_upper:
            score += 30
            platform_found = True
            print(f"   ✅ Platform match: {platform} (+30)")
        
        # Combination bonus (20 points)
        if account_found and platform_found:
            score += 20
            print(f"   ✅ Combination bonus (+20)")
        
        # BC3 SUPER BONUS (100 extra points for exact BC3-FB match)
        if account_code == "BC3" and platform == "FB" and account_found and platform_found:
            score += 100
            print(f"   🎯 BC3-FB SUPER MATCH BONUS (+100)")
        
        print(f"   📊 TOTAL SCORE: {score}")
        
        if score > best_score:
            best_score = score
            best_match = worksheet_title
            print(f"   🏆 NEW BEST MATCH!")
    
    print(f"\n🎯 FINAL RESULT: '{best_match}' with score {best_score}")
    return best_match if best_score > 0 else None

def write_to_google_sheets(concept_name, data_rows, creds):
    """COMPLETELY SIMPLIFIED: Always add to end - no more project scanning (Issue #5)"""
    if not creds: 
        return "Google credentials not available.", 1
    
    try:
        # Find the correct worksheet
        sheet, error = find_correct_worksheet(concept_name, creds)
        if error:
            return error, 1
        
        print(f"📝 Writing to worksheet: '{sheet.title}'")
        
        # COMPLETELY SIMPLIFIED: Always add to end, no project scanning
        if not data_rows: 
            return None, 1  # Return version 1 if no data to write
        
        # Find the absolute last row with any content
        all_values = sheet.get_all_values()
        last_content_row = 0
        for i, row in enumerate(all_values):
            if any(cell.strip() for cell in row if cell):
                last_content_row = i + 1
        
        # SIMPLIFIED: Always insert at end
        insert_row_index = last_content_row + 1
        print(f"📝 SIMPLIFIED: Adding new project at row {insert_row_index} (always at end)")
        
        # Get starting version number (simplified - just use 1)
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