# app/src/automation/orchestrator/processing/project_setup.py
"""
Project Setup Module - Handles card fetching, validation, and project setup
"""

import os
from ...api_clients import (get_trello_card_data, download_files_from_gdrive, get_google_creds)
from ...workflow_utils import create_project_structure
from ....naming_generator import generate_project_folder_name

class ProjectSetup:
    """Handles project initialization and setup"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def fetch_and_validate_card(self, trello_card_id):
        """Step 1: Fetch Trello card and validate basic data"""
        print("\n--- Step 1: Fetching Trello & Parsing Project Info ---")
        
        def fetch_card_data():
            card_data, error = get_trello_card_data(trello_card_id)
            if error:
                raise Exception(f"Failed to fetch Trello card: {error}")
            return card_data
        
        card_data = self.orchestrator.monitor.execute_with_activity_monitoring(
            fetch_card_data, 
            "Trello Card Fetch", 
            no_activity_timeout=60
        )
        
        # Validate card data
        validation_issues = self.orchestrator.validator.validate_trello_card(card_data)
        
        if not self.orchestrator.validator.show_validation_results(validation_issues):
            raise Exception("Validation failed - cannot proceed")
        
        return card_data
    
    def parse_and_validate(self, card_data):
        """Step 2: Parse instructions and validate assets"""
        print("\n--- Step 2: Parsing Instructions & Validating Assets ---")
        
        processing_mode = self.orchestrator.parser.parse_card_instructions(card_data.get('desc', ''))
        
        # Validate required assets exist
        asset_issues = self.orchestrator.validator.validate_assets(processing_mode)
        
        if not self.orchestrator.validator.show_validation_results(asset_issues):
            raise Exception("Required assets missing - cannot proceed")
        
        return processing_mode
    
    def download_and_setup(self, card_data, project_info):
        """Step 3: Download videos and set up project structure"""
        print("\n--- Step 3: Downloading Videos & Setting Up Project ---")
        
        # Get Google credentials
        def get_creds():
            creds = get_google_creds()  # Returns Credentials object directly
            if not creds:
                raise Exception("Failed to get Google credentials")
            return creds
        
        creds = self.orchestrator.monitor.execute_with_activity_monitoring(
            get_creds,
            "Google Authentication",
            no_activity_timeout=60
        )
        
        # Extract Google Drive link
        gdrive_link = self.orchestrator.validator.extract_gdrive_link(card_data.get('desc', ''))
        
        # Download videos
        def download_videos():
            videos, error = download_files_from_gdrive(gdrive_link, creds)
            if error:
                raise Exception(f"Failed to download videos: {error}")
            return videos
        
        downloaded_videos = self.orchestrator.monitor.execute_with_activity_monitoring(
            download_videos,
            "Video Download",
            no_activity_timeout=300
        )
        
        # Create project structure
        def create_structure():
            # Get processing mode from orchestrator
            processing_mode = getattr(self.orchestrator, 'processing_mode', '')
            
            # Determine ad_type_selection based on the actual processing mode
            ad_type_selection = "Quiz"  # Default
            
            if 'svsl' in processing_mode.lower():
                ad_type_selection = "SVSL"
            elif 'vsl' in processing_mode.lower():
                ad_type_selection = "VSL"
            else:
                ad_type_selection = "Quiz"
            
            print(f"📁 Creating folder with type: {ad_type_selection} (based on mode: {processing_mode})")
            
            # Use first downloaded video if available, otherwise use placeholder
            first_video = downloaded_videos[0] if downloaded_videos else "placeholder.mp4"
            
            # Generate folder name with all required arguments
            project_folder = generate_project_folder_name(
                project_info['project_name'],
                first_video,
                ad_type_selection
            )
            
            # Call create_project_structure - it returns just a paths dictionary
            paths = create_project_structure(project_folder)
            
            # Validate we got a valid result
            if not paths:
                raise Exception("Failed to create project structure: No paths returned")
            
            # IMPORTANT: Ensure _AME folder exists
            ame_folder = os.path.join(paths['project_root'], '_AME')
            if not os.path.exists(ame_folder):
                os.makedirs(ame_folder)
                print(f"📁 Created _AME folder: {ame_folder}")
            
            # Add _AME path to paths dictionary
            paths['_AME'] = ame_folder
            
            return paths
        
        project_paths = self.orchestrator.monitor.execute_with_activity_monitoring(
            create_structure,
            "Project Structure Creation",
            no_activity_timeout=60
        )
        
        print(f"✅ Downloaded {len(downloaded_videos)} videos")
        print(f"✅ Project structure created at: {project_paths['project_root']}")
        print(f"✅ Output folder ready at: {project_paths['_AME']}")
        
        return creds, downloaded_videos, project_paths