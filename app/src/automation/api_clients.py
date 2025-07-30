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
    """Fetches card name and G-Drive link from description."""
    url = f"https://api.trello.com/1/cards/{card_id}"
    query = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    try:
        response = requests.get(url, params=query, timeout=10)
        response.raise_for_status()
        card = response.json()
        gdrive_link_match = re.search(r'(https?://drive\.google\.com/drive/folders/[\w-]+)', card['desc'])
        if not gdrive_link_match:
            return None, "Google Drive link not found in Trello card description."
        return {"name": card['name'], "gdrive_url": gdrive_link_match.group(1)}, None
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

        try:
            first_occurrence_row = concept_col.index(concept_name) + 1
            is_existing_project = True
            print(f"Found existing project '{concept_name}'.")

            merged_range = next((r for r in sheet.merged_cells if r.start_row_index < first_occurrence_row <= r.end_row_index), None)
            last_row_of_concept = merged_range.end_row_index if merged_range else first_occurrence_row
            
            highest_version = 0
            for i in range(first_occurrence_row - 1, last_row_of_concept):
                if len(all_values[i]) > 1 and all_values[i][1].startswith('v'):
                    try:
                        version_num = int(all_values[i][1][1:])
                        if version_num > highest_version: highest_version = version_num
                    except (ValueError, IndexError): continue
            
            start_version = highest_version + 1
            insert_row_index = last_row_of_concept + 1
        except ValueError:
            print(f"Project '{concept_name}' not found. Creating new entry.")

        if not data_rows: return None, start_version

        # Prepare data with correct column structure
        rows_to_insert = []
        for row in data_rows:
            # New structure: [Concept (blank)], [Version], [Desc], [Name]
            rows_to_insert.append([""] + row)
        
        # Write data first
        sheet.insert_rows(rows_to_insert, row=insert_row_index, value_input_option='USER_ENTERED')
        
        # Then, format the newly added rows
        end_row_index = insert_row_index + len(rows_to_insert) - 1
        
        # Add the concept name to the first new row and merge
        sheet.update_cell(insert_row_index, 1, concept_name)
        if is_existing_project:
            sheet.merge_cells(f'A{first_occurrence_row}:A{end_row_index}')
        elif len(rows_to_insert) > 1:
            sheet.merge_cells(f'A{insert_row_index}:A{end_row_index}')

        # Add border
        sheet.format(f'A{insert_row_index}:D{end_row_index}', {"borders": {"top": {"style": "SOLID"}, "bottom": {"style": "SOLID"}, "left": {"style": "SOLID"}, "right": {"style": "SOLID"}}})

        return None, start_version
    except gspread.exceptions.WorksheetNotFound:
        return f"Worksheet '{WORKSHEET_NAME}' not found.", 1
    except Exception as e:
        return f"An unexpected Google Sheets error occurred: {e}", 1