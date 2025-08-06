# app/src/automation/api_clients/google_sheets_client.py
"""
Google Sheets API Client
Handles project tracking and data logging
FIXES: BC3 FB routing with exact worksheet matching
"""

import gspread
from typing import List, Optional, Tuple
from .config import GOOGLE_SHEET_ID
from .account_mapper import AccountMapper

class GoogleSheetsClient:
    """Handles Google Sheets API operations"""
    
    def __init__(self, credentials):
        """
        Initialize Google Sheets client
        
        Args:
            credentials: Google API credentials object
        """
        self.credentials = credentials
        self.client = None
        self.spreadsheet = None
        self.account_mapper = AccountMapper()
        
        if credentials:
            try:
                self.client = gspread.authorize(credentials)
                self.spreadsheet = self.client.open_by_key(GOOGLE_SHEET_ID)
            except Exception as e:
                print(f"❌ Failed to initialize Google Sheets client: {e}")
    
    def write_to_sheet(self, concept_name: str, data_rows: List[List], credentials) -> Tuple[Optional[str], int]:
        """
        CORRECTED: Write project data to correct worksheet with smart insertion
        
        Args:
            concept_name: Project name from card title
            data_rows: Data rows to insert
            credentials: Google credentials (for backward compatibility)
            
        Returns:
            Tuple of (error_message, start_version_number)
        """
        
        if not self.spreadsheet:
            return "Google Sheets not initialized", 1
        
        try:
            print(f"📝 Writing to Google Sheets: '{concept_name}'")
            
            # Find the correct worksheet using corrected logic
            worksheet, error = self.find_correct_worksheet(concept_name)
            if error:
                return error, 1
            
            print(f"📋 Selected worksheet: '{worksheet.title}'")
            
            if not data_rows:
                return None, 1  # Return version 1 if no data to write
            
            # Find insertion point and write data
            start_version = self._insert_project_data(worksheet, concept_name, data_rows)
            
            print(f"✅ Successfully wrote {len(data_rows)} rows to worksheet '{worksheet.title}'")
            return None, start_version
            
        except Exception as e:
            error_msg = f"Google Sheets write error: {e}"
            print(f"❌ {error_msg}")
            return error_msg, 1
    
    def find_correct_worksheet(self, concept_name: str) -> Tuple[Optional[object], Optional[str]]:
        """
        CORRECTED: Find correct worksheet using direct card title parsing
        
        Args:
            concept_name: Card title (e.g., "BC3 FB - New Ads from...")
            
        Returns:
            Tuple of (worksheet_object, error_message)
        """
        
        if not self.spreadsheet:
            return None, "Google Sheets not initialized"
        
        try:
            # Extract account and platform using CORRECTED logic
            account_code, platform_code = self.account_mapper.extract_account_and_platform(concept_name)
            
            print(f"🔍 SHEETS CLIENT - Account: '{account_code}', Platform: '{platform_code}'")
            
            # Get all worksheet titles
            worksheets = self.spreadsheet.worksheets()
            worksheet_titles = [ws.title for ws in worksheets]
            
            print(f"📋 Available worksheets: {worksheet_titles}")
            
            # Look for exact match using corrected logic
            target_worksheet = self.account_mapper.find_exact_worksheet_match(
                worksheet_titles, account_code, platform_code
            )
            
            if target_worksheet:
                print(f"✅ EXACT MATCH FOUND: '{target_worksheet}'")
                return self.spreadsheet.worksheet(target_worksheet), None
            else:
                print(f"⚠️ No exact match found, using first worksheet: '{worksheet_titles[0]}'")
                return self.spreadsheet.worksheet(worksheet_titles[0]), None
                
        except Exception as e:
            return None, f"Error finding worksheet: {e}"
    
    def _insert_project_data(self, worksheet, concept_name: str, data_rows: List[List]) -> int:
        """
        ENHANCED: Insert project data with smart positioning and formatting
        
        Args:
            worksheet: Google Sheets worksheet object
            concept_name: Project name
            data_rows: Data rows to insert
            
        Returns:
            Starting version number
        """
        
        try:
            # Find absolute last row with any content
            all_values = worksheet.get_all_values()
            last_content_row = 0
            for i, row in enumerate(all_values):
                if any(cell.strip() for cell in row if cell):
                    last_content_row = i + 1
            
            # Always insert at end
            insert_row_index = last_content_row + 1
            print(f"📝 Adding new project at row {insert_row_index}")
            
            # Get starting version number (simplified for now)
            start_version = 1
            
            # Prepare data with correct column structure
            rows_to_insert = []
            for i, row in enumerate(data_rows):
                if i == 0:
                    # First row gets concept name in column A
                    rows_to_insert.append([concept_name] + row)
                else:
                    # Subsequent rows have empty column A
                    rows_to_insert.append([""] + row)
            
            print(f"📝 Inserting {len(rows_to_insert)} rows starting at row {insert_row_index}")
            
            # Write data using individual cell updates (more reliable)
            for row_offset, row_data in enumerate(rows_to_insert):
                current_row = insert_row_index + row_offset
                for col_offset, cell_value in enumerate(row_data):
                    if cell_value:  # Only write non-empty cells
                        worksheet.update_cell(current_row, col_offset + 1, str(cell_value))
            
            # Apply formatting
            self._apply_project_formatting(worksheet, insert_row_index, len(rows_to_insert))
            
            return start_version
            
        except Exception as e:
            print(f"❌ Error inserting project data: {e}")
            return 1
    
    def _apply_project_formatting(self, worksheet, start_row: int, num_rows: int):
        """
        Apply professional formatting to the inserted project data
        
        Args:
            worksheet: Google Sheets worksheet
            start_row: Starting row index
            num_rows: Number of rows to format
        """
        
        try:
            end_row = start_row + num_rows - 1
            
            # Apply top border
            top_border_range = f'A{start_row}:D{start_row}'
            worksheet.format(top_border_range, {
                "borders": {
                    "top": {"style": "SOLID_THICK", "color": {"red": 0, "green": 0, "blue": 0}}
                }
            })
            
            # Apply bottom border
            bottom_border_range = f'A{end_row}:D{end_row}'
            worksheet.format(bottom_border_range, {
                "borders": {
                    "bottom": {"style": "SOLID_THICK", "color": {"red": 0, "green": 0, "blue": 0}}
                }
            })
            
            # Merge and format column A for project name (if multiple rows)
            if num_rows > 1:
                try:
                    merge_range = f'A{start_row}:A{end_row}'
                    worksheet.merge_cells(merge_range)
                    
                    # Apply vertical alignment, horizontal alignment, and text wrapping
                    worksheet.format(merge_range, {
                        "verticalAlignment": "MIDDLE",
                        "horizontalAlignment": "CENTER",  # FIXED: Added horizontal centering
                        "wrapStrategy": "WRAP",
                        "textFormat": {"bold": False}
                    })
                    
                    print(f"✅ Applied formatting with merged cells, borders, and horizontal centering")
                    
                except Exception as format_error:
                    print(f"⚠️ Warning: Could not apply cell formatting: {format_error}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not apply formatting: {e}")
    
    def get_worksheet_names(self) -> List[str]:
        """Get list of all worksheet names"""
        if not self.spreadsheet:
            return []
        
        try:
            worksheets = self.spreadsheet.worksheets()
            return [ws.title for ws in worksheets]
        except Exception as e:
            print(f"❌ Error getting worksheet names: {e}")
            return []