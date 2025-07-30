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
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME", "Creative Log")
DOWNLOADS_DIR = "temp_downloads"

# --- FUNCTIONS ---

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
            "desc": card_desc,  # Now includes full description
            "gdrive_url": gdrive_link_match.group(1)
        }, None
        
    except requests.exceptions.RequestException as e:
        return None, f"Trello API request failed: {e}"

def download_files_from_gdrive(folder_url, creds):
    """Downloads all video files from a Google Drive folder."""
    if not creds: return None, "Google credentials not available."
    try:
        drive_service = build("drive", "v3", credentials=creds)
        folder_id = folder_url.split('/')[-1]
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        query = f"'{folder_id}' in parents and mimeType contains 'video/'"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get("files", [])
        if not items: return None, "No video files found in the Google Drive folder."
        
        downloaded_files = []
        for item in items:
            file_id, file_name = item['id'], item['name']
            local_path = os.path.join(DOWNLOADS_DIR, file_name)
            print(f"Downloading {file_name}...")
            request = drive_service.files().get_media(fileId=file_id)
            with open(local_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status: print(f"Download {int(status.progress() * 100)}%.")
            downloaded_files.append(local_path)
        return downloaded_files, None
    except HttpError as e:
        return None, f"Google Drive API error: {e}"

def write_to_google_sheets(concept_name, data_rows, creds):
    """Intelligently finds and updates a project in Google Sheets."""
    if not creds: return "Google credentials not available.", 1
    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        all_values = sheet.get_all_values()
        concept_col = [row[0] for row in all_values] if all_values else []
        
        start_version = 1
        insert_row_index = len(all_values) + 1
        is_existing_project = False
        first_occurrence_row = None
        actual_last_row = None

        # Find existing project
        try:
            first_occurrence_row = concept_col.index(concept_name) + 1
            is_existing_project = True
            print(f"Found existing project '{concept_name}' at row {first_occurrence_row}.")

            # Get actual merged cell ranges using Google Sheets API
            actual_last_row = get_merged_cell_end_row(creds, first_occurrence_row)
            if not actual_last_row:
                # Fallback to text-based scanning
                actual_last_row = first_occurrence_row
                for i in range(first_occurrence_row, len(all_values)):
                    if i < len(all_values):
                        current_row = all_values[i]
                        if current_row[0] and current_row[0] != concept_name:
                            break
                        actual_last_row = i + 1
                    else:
                        break
            
            print(f"Project spans from row {first_occurrence_row} to row {actual_last_row}")
            
            # Find highest version number in this concept's range
            highest_version = 0
            for i in range(first_occurrence_row - 1, actual_last_row):
                if i < len(all_values) and len(all_values[i]) > 1 and all_values[i][1].startswith('v'):
                    try:
                        version_num = int(all_values[i][1][1:])
                        if version_num > highest_version: 
                            highest_version = version_num
                    except (ValueError, IndexError): 
                        continue
            
            start_version = highest_version + 1
            insert_row_index = actual_last_row + 1
            
        except ValueError:
            print(f"Project '{concept_name}' not found. Creating new entry.")

        if not data_rows: return None, start_version

        # Prepare data with correct column structure
        rows_to_insert = []
        for row in data_rows:
            # Structure: [Concept (blank for continuation)], [Version], [Desc], [Name]
            rows_to_insert.append([""] + row)
        
        print(f"Inserting {len(rows_to_insert)} rows at row {insert_row_index}")
        
        # Write data first
        sheet.insert_rows(rows_to_insert, row=insert_row_index, value_input_option='USER_ENTERED')
        
        # Calculate the new end row after insertion
        end_row_index = insert_row_index + len(rows_to_insert) - 1
        
        # Handle concept name and merging
        if is_existing_project and actual_last_row:
            # For existing projects, extend the existing merged cell
            print(f"Extending existing project merge from row {first_occurrence_row} to {end_row_index}")
            success = extend_merged_range(sheet, creds, first_occurrence_row, actual_last_row, end_row_index)
            if not success:
                print("Could not extend merged range, but data was still inserted successfully")
        else:
            # For new projects, add concept name and merge if multiple rows
            print("Adding concept name for new project")
            sheet.update_cell(insert_row_index, 1, concept_name)
            if len(rows_to_insert) > 1:
                success = create_new_merged_range(sheet, insert_row_index, end_row_index)
                if not success:
                    print("Could not merge new project cells, but data was still inserted successfully")

        # Add border formatting (optional, don't fail if it doesn't work)
        try:
            sheet.format(f'A{insert_row_index}:D{end_row_index}', {
                "borders": {
                    "top": {"style": "SOLID"}, 
                    "bottom": {"style": "SOLID"}, 
                    "left": {"style": "SOLID"}, 
                    "right": {"style": "SOLID"}
                }
            })
        except Exception as format_error:
            print(f"Warning: Could not format borders: {format_error}")

        print(f"Successfully added {len(rows_to_insert)} rows to Google Sheets")
        return None, start_version
        
    except gspread.exceptions.WorksheetNotFound:
        return f"Worksheet '{WORKSHEET_NAME}' not found.", 1
    except Exception as e:
        return f"An unexpected Google Sheets error occurred: {e}", 1

def get_merged_cell_end_row(creds, first_occurrence_row):
    """Get the actual end row of a merged cell range using Google Sheets API."""
    try:
        sheets_service = build("sheets", "v4", credentials=creds)
        spreadsheet_data = sheets_service.spreadsheets().get(
            spreadsheetId=GOOGLE_SHEET_ID,
            includeGridData=False
        ).execute()
        
        # Find the worksheet by name to get its ID
        worksheet_id = None
        for sheet_info in spreadsheet_data['sheets']:
            if sheet_info['properties']['title'] == WORKSHEET_NAME:
                worksheet_id = sheet_info['properties']['sheetId']
                break
        
        if worksheet_id is not None:
            # Get merged cells for this worksheet
            for sheet_info in spreadsheet_data['sheets']:
                if sheet_info['properties']['sheetId'] == worksheet_id:
                    merges = sheet_info.get('merges', [])
                    for merge in merges:
                        # Convert to 1-based indexing and check if it contains our row
                        start_row = merge['startRowIndex'] + 1
                        end_row = merge['endRowIndex']  # Exclusive, so last row is end_row - 1
                        start_col = merge['startColumnIndex'] + 1
                        
                        if (start_row <= first_occurrence_row < end_row and start_col == 1):  # Column A
                            print(f"Found matching merged range: rows {start_row} to {end_row - 1}")
                            return end_row - 1  # Convert to inclusive
                    break
        
        return None
    except Exception as e:
        print(f"Warning: Could not get merged cells via API: {e}")
        return None

def extend_merged_range(sheet, creds, first_row, old_last_row, new_last_row):
    """Safely extend an existing merged range."""
    try:
        # First, try to unmerge the existing range
        existing_range = f'A{first_row}:A{old_last_row}'
        print(f"Attempting to unmerge existing range: {existing_range}")
        
        try:
            sheet.unmerge_cells(existing_range)
            print("Successfully unmerged existing range")
        except Exception as unmerge_error:
            print(f"Could not unmerge existing range: {unmerge_error}")
            # Try alternative: use Google Sheets API to unmerge
            try:
                sheets_service = build("sheets", "v4", credentials=creds)
                worksheet_id = get_worksheet_id(sheets_service, GOOGLE_SHEET_ID, WORKSHEET_NAME)
                if worksheet_id is not None:
                    request_body = {
                        'requests': [{
                            'unmergeCells': {
                                'range': {
                                    'sheetId': worksheet_id,
                                    'startRowIndex': first_row - 1,
                                    'endRowIndex': old_last_row,
                                    'startColumnIndex': 0,
                                    'endColumnIndex': 1
                                }
                            }
                        }]
                    }
                    sheets_service.spreadsheets().batchUpdate(
                        spreadsheetId=GOOGLE_SHEET_ID, 
                        body=request_body
                    ).execute()
                    print("Successfully unmerged using Sheets API")
            except Exception as api_unmerge_error:
                print(f"Could not unmerge using API either: {api_unmerge_error}")
                return False
        
        # Now merge the extended range
        new_range = f'A{first_row}:A{new_last_row}'
        print(f"Attempting to merge new range: {new_range}")
        sheet.merge_cells(new_range)
        print(f"Successfully merged extended range: {new_range}")
        return True
        
    except Exception as e:
        print(f"Error extending merged range: {e}")
        return False

def create_new_merged_range(sheet, start_row, end_row):
    """Create a new merged range for a new project."""
    try:
        new_range = f'A{start_row}:A{end_row}'
        print(f"Creating new merged range: {new_range}")
        sheet.merge_cells(new_range)
        print(f"Successfully created new merged range: {new_range}")
        return True
    except Exception as e:
        print(f"Error creating new merged range: {e}")
        return False

def get_worksheet_id(sheets_service, spreadsheet_id, worksheet_name):
    """Get the worksheet ID for a given worksheet name."""
    try:
        spreadsheet_data = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            includeGridData=False
        ).execute()
        
        for sheet_info in spreadsheet_data['sheets']:
            if sheet_info['properties']['title'] == worksheet_name:
                return sheet_info['properties']['sheetId']
        return None
    except Exception as e:
        print(f"Error getting worksheet ID: {e}")
        return None