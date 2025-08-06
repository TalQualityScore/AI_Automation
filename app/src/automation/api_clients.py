# app/src/automation/api_clients.py - UPDATED with complete account list for smart sheet detection

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

# UPDATED: Complete account mapping for sheet detection
ACCOUNT_MAPPING = {
    # Full acronym + name pairs
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
    'BC3': 'Bio Complete 3',
    'PP': 'Pro Plant',
    'SPC': 'Superfood Complete',
    'MA': 'Metabolic Advanced',
    'KA': 'Keto Active',
    'BLR': 'BadLand Ranch',
    
    # Special cases
    'Bio X4': 'Bio X4',
    'Upwellness': 'Upwellness',
    
    # Spanish variants
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
    """ENHANCED: Find the correct worksheet based on account and platform with UPDATED accounts"""
    if not creds: 
        return None, "Google credentials not available."
    
    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        
        # Extract account and platform from concept name
        account_code, platform = _extract_account_and_platform(concept_name)
        
        print(f"🔍 Looking for worksheet matching account: '{account_code}' and platform: '{platform}'")
        
        # Get all worksheet titles
        worksheets = spreadsheet.worksheets()
        worksheet_titles = [ws.title for ws in worksheets]
        
        print(f"📋 Available worksheets: {worksheet_titles}")
        
        # ENHANCED MATCHING LOGIC with updated accounts
        best_match = _find_best_worksheet_match(worksheet_titles, account_code, platform)
        
        if best_match:
            print(f"✅ Selected worksheet: '{best_match}'")
            return spreadsheet.worksheet(best_match), None
        else:
            # Fallback to first worksheet or default
            print(f"⚠️ No specific match found, using first available worksheet: '{worksheet_titles[0]}'")
            return spreadsheet.worksheet(worksheet_titles[0]), None
            
    except Exception as e:
        return None, f"Error finding correct worksheet: {e}"

def _extract_account_and_platform(concept_name):
    """Extract account code and determine platform from project context - UPDATED"""
    
    # Check all account codes (prioritizing longer ones first to avoid partial matches)
    account_codes = sorted(ACCOUNT_MAPPING.keys(), key=len, reverse=True)
    account_code = "UNKNOWN"
    
    concept_upper = concept_name.upper()
    
    for code in account_codes:
        if code.upper() in concept_upper:
            account_code = code
            print(f"✅ Account code found in concept: {code}")
            break
    
    # If no direct match, try partial matching with full names
    if account_code == "UNKNOWN":
        for code, full_name in ACCOUNT_MAPPING.items():
            name_words = full_name.upper().split()
            for word in name_words:
                if len(word) > 3 and word in concept_upper:
                    account_code = code
                    print(f"✅ Account found by name match: {word} -> {code}")
                    break
            if account_code != "UNKNOWN":
                break
    
    # Platform detection - still simplified for now
    # You might want to add more context-based platform detection here
    platform = "YT"  # Default to YouTube
    
    return account_code, platform

def _find_best_worksheet_match(worksheet_titles, account_code, platform):
    """Find the best matching worksheet using fuzzy matching - UPDATED with all accounts"""
    
    # Get account variations for the detected code
    account_variations = [account_code]
    if account_code in ACCOUNT_MAPPING:
        full_name = ACCOUNT_MAPPING[account_code]
        account_variations.extend([
            full_name,
            full_name.replace('\'', ''),  # Handle apostrophes
            full_name.replace(' ', ''),   # Handle spaces
            full_name.upper(),
            full_name.lower()
        ])
    
    # Platform name variations
    platform_names = {
        "YT": ["YouTube", "YT", "Youtube", "YOUTUBE"],
        "FB": ["Facebook", "FB", "FACEBOOK"],
        "SNAP": ["Snapchat", "Snap", "SNAPCHAT"],
        "TT": ["TikTok", "TT", "TIKTOK"],
        "IG": ["Instagram", "IG", "INSTAGRAM", "Insta"],
        "TWITTER": ["Twitter", "X", "TWITTER"],
        "LINKEDIN": ["LinkedIn", "LINKEDIN"]
    }
    
    platform_variations = platform_names.get(platform, [platform])
    
    print(f"🔍 Searching for account variations: {account_variations}")
    print(f"🔍 Searching for platform variations: {platform_variations}")
    
    best_match = None
    best_score = 0
    
    for worksheet_title in worksheet_titles:
        score = 0
        title_upper = worksheet_title.upper()
        
        # Check for account match (higher priority)
        account_matched = False
        for account_var in account_variations:
            if account_var.upper() in title_upper:
                score += 50
                account_matched = True
                print(f"📊 Account match found in '{worksheet_title}': {account_var} (+50 points)")
                break
        
        # Check for platform match
        platform_matched = False
        for platform_var in platform_variations:
            if platform_var.upper() in title_upper:
                score += 30
                platform_matched = True
                print(f"📊 Platform match found in '{worksheet_title}': {platform_var} (+30 points)")
                break
        
        # Bonus for having both account and platform
        if account_matched and platform_matched:
            score += 25
            print(f"📊 Combination bonus for '{worksheet_title}' (+25 points)")
        
        # Additional bonus for exact patterns (account - platform or platform - account)
        for account_var in account_variations:
            for platform_var in platform_variations:
                # Check patterns like "MCT - YouTube" or "YouTube - MCT"
                pattern1 = f"{account_var.upper()}.*{platform_var.upper()}"
                pattern2 = f"{platform_var.upper()}.*{account_var.upper()}"
                if re.search(pattern1, title_upper) or re.search(pattern2, title_upper):
                    score += 15
                    print(f"📊 Pattern bonus for '{worksheet_title}' (+15 points)")
                    break
        
        print(f"📊 Total score for '{worksheet_title}': {score}")
        
        if score > best_score:
            best_score = score
            best_match = worksheet_title
            print(f"🏆 New best match: '{worksheet_title}' (score: {score})")
    
    print(f"🎯 Final selection: '{best_match}' with score {best_score}")
    return best_match if best_score > 0 else None

def write_to_google_sheets(concept_name, data_rows, creds):
    """ENHANCED: Write to intelligently selected worksheet with UPDATED account support"""
    if not creds: 
        return "Google credentials not available.", 1
    
    try:
        # Find the correct worksheet using updated account mapping
        sheet, error = find_correct_worksheet(concept_name, creds)
        if error:
            return error, 1
        
        print(f"📝 Writing to worksheet: '{sheet.title}'")
        
        # Use the existing logic but with the smart-selected sheet
        all_values = sheet.get_all_values()
        
        start_version = 1
        is_existing_project = False
        first_occurrence_row = None
        actual_last_row = None

        # Check if this project already exists
        concept_col = [row[0] if row else "" for row in all_values]
        try:
            first_occurrence_row = concept_col.index(concept_name) + 1
            is_existing_project = True
            print(f"📋 Found existing project '{concept_name}' at row {first_occurrence_row} in worksheet '{sheet.title}'.")

            # Find the actual last row of this project
            actual_last_row = first_occurrence_row
            for i in range(first_occurrence_row, len(all_values)):
                if i < len(all_values):
                    current_row = all_values[i]
                    if current_row[0] and current_row[0] != concept_name:
                        break
                    if any(current_row):
                        actual_last_row = i + 1
            
            print(f"📋 Existing project spans from row {first_occurrence_row} to row {actual_last_row}")
            
            # Find highest version number in this range
            highest_version = 0
            for i in range(first_occurrence_row - 1, actual_last_row):
                if (i < len(all_values) and len(all_values[i]) > 1 and 
                    all_values[i][1] and all_values[i][1].startswith('v')):
                    try:
                        version_num = int(all_values[i][1][1:])
                        if version_num > highest_version: 
                            highest_version = version_num
                    except (ValueError, IndexError): 
                        continue
            
            start_version = highest_version + 1
            
        except ValueError:
            print(f"📋 Project '{concept_name}' not found in worksheet '{sheet.title}'. Creating new entry.")

        if not data_rows: 
            return None, start_version

        # Find the absolute last row with any content
        last_content_row = 0
        for i, row in enumerate(all_values):
            if any(cell.strip() for cell in row if cell):
                last_content_row = i + 1

        if is_existing_project:
            insert_row_index = actual_last_row + 1
            print(f"📝 Will insert new versions for existing project at row {insert_row_index}")
        else:
            insert_row_index = last_content_row + 1
            print(f"📝 New project: inserting at row {insert_row_index}")

        # Prepare data with correct column structure
        rows_to_insert = []
        for i, row in enumerate(data_rows):
            if i == 0:
                rows_to_insert.append([concept_name] + row)
            else:
                rows_to_insert.append([""] + row)

        print(f"📝 Inserting {len(rows_to_insert)} rows starting at row {insert_row_index} in worksheet '{sheet.title}'")

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
                if is_existing_project:
                    full_range = f'A{first_occurrence_row}:A{end_row_index}'
                    print(f"📝 Extending merge for existing project: {full_range}")
                    try:
                        sheet.unmerge_cells(f'A{first_occurrence_row}:A{actual_last_row}')
                    except:
                        pass
                    sheet.merge_cells(full_range)
                else:
                    merge_range = f'A{insert_row_index}:A{end_row_index}'
                    print(f"📝 Creating merge for new project: {merge_range}")
                    sheet.merge_cells(merge_range)
                    
            except Exception as merge_error:
                print(f"⚠️ Warning: Could not merge cells: {merge_error}")

        # Apply border formatting
        try:
            top_border_range = f'A{insert_row_index}:D{insert_row_index}'
            sheet.format(top_border_range, {
                "borders": {
                    "top": {"style": "SOLID_THICK", "color": {"red": 0, "green": 0, "blue": 0}}
                }
            })
            
            bottom_border_range = f'A{end_row_index}:D{end_row_index}'
            sheet.format(bottom_border_range, {
                "borders": {
                    "bottom": {"style": "SOLID_THICK", "color": {"red": 0, "green": 0, "blue": 0}}
                }
            })
            
            print(f"✅ Applied formatting to worksheet '{sheet.title}'")
        except Exception as format_error:
            print(f"⚠️ Warning: Could not format borders: {format_error}")

        print(f"✅ Successfully added {len(rows_to_insert)} rows to worksheet '{sheet.title}'")
        return None, start_version
        
    except gspread.exceptions.WorksheetNotFound as e:
        return f"Worksheet not found: {e}", 1
    except Exception as e:
        return f"An unexpected Google Sheets error occurred: {e}", 1