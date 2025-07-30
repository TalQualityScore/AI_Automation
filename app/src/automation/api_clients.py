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
            "desc": card_desc,
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
        
        start_version = 1
        is_existing_project = False
        first_occurrence_row = None
        actual_last_row = None

        # Check if this project already exists
        concept_col = [row[0] if row else "" for row in all_values]
        try:
            first_occurrence_row = concept_col.index(concept_name) + 1
            is_existing_project = True
            print(f"Found existing project '{concept_name}' at row {first_occurrence_row}.")

            # Find the actual last row of this project
            actual_last_row = first_occurrence_row
            for i in range(first_occurrence_row, len(all_values)):
                if i < len(all_values):
                    current_row = all_values[i]
                    # If we hit another concept name, we've found the boundary
                    if current_row[0] and current_row[0] != concept_name:
                        break
                    # If this row has any content, it belongs to our project
                    if any(current_row):
                        actual_last_row = i + 1
            
            print(f"Existing project spans from row {first_occurrence_row} to row {actual_last_row}")
            
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
            print(f"Project '{concept_name}' not found. Creating new entry.")

        if not data_rows: return None, start_version

        # Find the absolute last row with any content
        last_content_row = 0
        for i, row in enumerate(all_values):
            if any(cell.strip() for cell in row if cell):
                last_content_row = i + 1

        if is_existing_project:
            # For existing projects, insert right after the last row of this project
            insert_row_index = actual_last_row + 1
            print(f"Will insert new versions for existing project at row {insert_row_index}")
        else:
            # For new projects, use the buffer method then clean up
            buffer_space = 10
            insert_row_index = last_content_row + buffer_space
            print(f"New project: Last content at row {last_content_row}, inserting at row {insert_row_index} (with {buffer_space} row buffer)")

        # Prepare data with correct column structure
        rows_to_insert = []
        for i, row in enumerate(data_rows):
            if i == 0:
                # First row gets the concept name
                rows_to_insert.append([concept_name] + row)
            else:
                # Subsequent rows get empty concept column
                rows_to_insert.append([""] + row)

        print(f"Inserting {len(rows_to_insert)} rows starting at row {insert_row_index}")

        # Write data using individual cell updates
        for row_offset, row_data in enumerate(rows_to_insert):
            current_row = insert_row_index + row_offset
            for col_offset, cell_value in enumerate(row_data):
                if cell_value:  # Only write non-empty values
                    sheet.update_cell(current_row, col_offset + 1, str(cell_value))
                    
        end_row_index = insert_row_index + len(rows_to_insert) - 1

        # FIXED: For new projects only - Clean up empty rows and move data to proper position
        if not is_existing_project:
            print("Cleaning up empty buffer rows and moving data...")
            try:
                # Calculate the new position (right after last content)
                new_insert_row = last_content_row + 1
                
                # If we need to move the data (it's not already in the right place)
                if insert_row_index != new_insert_row:
                    print(f"Moving data from row {insert_row_index} to row {new_insert_row}")
                    
                    # Read the data we just wrote
                    range_to_read = f'A{insert_row_index}:D{end_row_index}'
                    response = sheet.get(range_to_read)
                    written_data = response.get('values', []) if hasattr(response, 'get') else response
                    
                    # Write it to the correct position
                    new_end_row = new_insert_row + len(written_data) - 1
                    for row_offset, row_data in enumerate(written_data):
                        current_row = new_insert_row + row_offset
                        for col_offset, cell_value in enumerate(row_data):
                            if col_offset < len(row_data) and row_data[col_offset]:
                                sheet.update_cell(current_row, col_offset + 1, str(row_data[col_offset]))
                    
                    # Clear the old location
                    clear_range = f'A{insert_row_index}:D{end_row_index}'
                    sheet.batch_clear([clear_range])
                    
                    # Update our tracking variables to the NEW position
                    insert_row_index = new_insert_row
                    end_row_index = new_end_row
                    
                print(f"Successfully moved data to correct position: rows {insert_row_index}-{end_row_index}")
                    
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up empty rows: {cleanup_error}")

        # FIXED: Merge column A for the concept name (only for multiple rows)
        if len(rows_to_insert) > 1:
            try:
                if is_existing_project:
                    # Extend existing merge to include new rows
                    full_range = f'A{first_occurrence_row}:A{end_row_index}'
                    print(f"Extending merge for existing project: {full_range}")
                    # First unmerge existing
                    try:
                        sheet.unmerge_cells(f'A{first_occurrence_row}:A{actual_last_row}')
                    except:
                        pass  # Might not be merged
                    # Then merge the full range
                    sheet.merge_cells(full_range)
                else:
                    # Create new merge for new project (use FINAL position)
                    merge_range = f'A{insert_row_index}:A{end_row_index}'
                    print(f"Creating merge for new project: {merge_range}")
                    sheet.merge_cells(merge_range)
                    
            except Exception as merge_error:
                print(f"Warning: Could not merge cells: {merge_error}")

        # Apply border formatting (top and bottom borders only, thick black) - USE FINAL POSITION
        try:
            # Apply thick black border to top row only (FINAL position)
            top_border_range = f'A{insert_row_index}:D{insert_row_index}'
            sheet.format(top_border_range, {
                "borders": {
                    "top": {"style": "SOLID_THICK", "color": {"red": 0, "green": 0, "blue": 0}}
                }
            })
            
            # Apply thick black border to bottom row only (FINAL position)  
            bottom_border_range = f'A{end_row_index}:D{end_row_index}'
            sheet.format(bottom_border_range, {
                "borders": {
                    "bottom": {"style": "SOLID_THICK", "color": {"red": 0, "green": 0, "blue": 0}}
                }
            })
            
            print(f"Applied thick black borders to top row {insert_row_index} and bottom row {end_row_index}")
        except Exception as format_error:
            print(f"Warning: Could not format borders: {format_error}")

        print(f"Successfully added {len(rows_to_insert)} rows to Google Sheets")
        return None, start_version
        
    except gspread.exceptions.WorksheetNotFound:
        return f"Worksheet '{WORKSHEET_NAME}' not found.", 1
    except Exception as e:
        return f"An unexpected Google Sheets error occurred: {e}", 1