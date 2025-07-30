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
        last_row_of_concept = None

        # Find existing project
        try:
            first_occurrence_row = concept_col.index(concept_name) + 1
            is_existing_project = True
            print(f"Found existing project '{concept_name}' at row {first_occurrence_row}.")

            # Find the last row of this concept by looking for the next non-empty concept or end of data
            last_row_of_concept = first_occurrence_row
            for i in range(first_occurrence_row, len(all_values)):
                if i < len(all_values):
                    current_row = all_values[i]
                    # If we find another concept name (non-empty in column A), stop here
                    if current_row[0] and current_row[0] != concept_name:
                        break
                    # If this row belongs to our concept (empty column A or same concept name)
                    if not current_row[0] or current_row[0] == concept_name:
                        last_row_of_concept = i + 1
                    else:
                        break
                else:
                    break
            
            print(f"Project spans from row {first_occurrence_row} to row {last_row_of_concept}")
            
            # Find highest version number in this concept's range
            highest_version = 0
            for i in range(first_occurrence_row - 1, last_row_of_concept):
                if i < len(all_values) and len(all_values[i]) > 1 and all_values[i][1].startswith('v'):
                    try:
                        version_num = int(all_values[i][1][1:])
                        if version_num > highest_version: 
                            highest_version = version_num
                    except (ValueError, IndexError): 
                        continue
            
            start_version = highest_version + 1
            insert_row_index = last_row_of_concept + 1
            
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
        if is_existing_project:
            # For existing projects, we need to extend the existing merged cell
            print(f"Extending existing project merge from row {first_occurrence_row} to {end_row_index}")
            try:
                # First, try to unmerge the existing range
                try:
                    sheet.unmerge_cells(f'A{first_occurrence_row}:A{last_row_of_concept}')
                except:
                    pass  # Might not be merged yet
                
                # Now merge the full range including new rows
                sheet.merge_cells(f'A{first_occurrence_row}:A{end_row_index}')
                print(f"Successfully merged A{first_occurrence_row}:A{end_row_index}")
                
            except Exception as merge_error:
                print(f"Warning: Could not merge cells: {merge_error}")
        else:
            # For new projects, add concept name and merge if multiple rows
            sheet.update_cell(insert_row_index, 1, concept_name)
            if len(rows_to_insert) > 1:
                try:
                    sheet.merge_cells(f'A{insert_row_index}:A{end_row_index}')
                    print(f"Successfully merged new project A{insert_row_index}:A{end_row_index}")
                except Exception as merge_error:
                    print(f"Warning: Could not merge cells: {merge_error}")

        # Add border formatting
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