# app/src/automation/orchestrator/ui_preparation.py
"""
UI Data Preparation Module
Handles preparation of confirmation data and project info parsing
Split from ui_integration.py for better organization
"""

from ..workflow_dialog.helpers import create_confirmation_data_from_orchestrator
from ..workflow_utils import parse_project_info

class UIPreparation:
    """Handles UI data preparation and account detection"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def prepare_confirmation_data(self):
        """Prepare data for the confirmation dialog - FIXED to preserve card title"""
        # Fetch basic card data for validation
        self.orchestrator.card_data = self.orchestrator.processing_steps.fetch_and_validate_card(
            self.orchestrator.trello_card_id
        )
        
        # IMPORTANT: Store the original card title for Google Sheets ROUTING ONLY
        self.orchestrator.original_card_title = self.orchestrator.card_data['name']
        print(f"🔍 UI PREPARATION - Stored original card title for routing: '{self.orchestrator.original_card_title}'")
        
        # Detect account and platform
        self._detect_account_and_platform()
        
        # Parse project info
        self.orchestrator.project_info = self._parse_project_info_for_ui(self.orchestrator.card_data)
        
        # Add detected codes to project_info
        self._add_detected_codes_to_project_info()
        
        # Determine processing mode
        self.orchestrator.processing_mode = self.orchestrator.parser.parse_card_instructions(
            self.orchestrator.card_data.get('desc', '')
        )
        
        # Validate assets
        asset_issues = self.orchestrator.validator.validate_assets(self.orchestrator.processing_mode)
        
        # Create and return confirmation data
        return self._create_confirmation_data(asset_issues)
    
    def _detect_account_and_platform(self):
        """Detect account and platform from card title"""
        try:
            from ..api_clients import AccountMapper
            mapper = AccountMapper()
            
            # Clear any cached data first
            mapper._clear_cache()
            
            print(f"🔍 ATTEMPTING ACCOUNT/PLATFORM DETECTION from: '{self.orchestrator.original_card_title}'")
            
            account_code, platform_code = mapper.extract_account_and_platform(
                self.orchestrator.original_card_title, 
                allow_fallback=True  # Show dialog if detection fails
            )
            
            print(f"✅ Account/Platform detected: Account='{account_code}', Platform='{platform_code}'")
            
            # Store for later use
            self.orchestrator.detected_account_code = account_code
            self.orchestrator.detected_platform_code = platform_code
            
            # Also store in card_data
            self.orchestrator.card_data['detected_account_code'] = account_code
            self.orchestrator.card_data['detected_platform_code'] = platform_code
            
        except Exception as detection_error:
            print(f"❌ CRITICAL: Account/Platform detection failed: {detection_error}")
            raise Exception(f"Cannot proceed without account/platform identification: {detection_error}")
    
    def _parse_project_info_for_ui(self, card_data):
        """Parse project info for UI display"""
        project_info = parse_project_info(card_data['name'])
        
        if not project_info:
            # Fallback: create basic project info from card name
            project_info = {
                'project_name': card_data['name'],
                'ad_type': 'Unknown',
                'test_name': '0000',
                'version_letter': ''
            }
        
        print(f"🔍 PARSED PROJECT INFO: {project_info}")
        return project_info
    
    def _add_detected_codes_to_project_info(self):
        """Add detected account/platform codes to project info"""
        self.orchestrator.project_info['detected_account_code'] = self.orchestrator.detected_account_code
        self.orchestrator.project_info['detected_platform_code'] = self.orchestrator.detected_platform_code
        self.orchestrator.project_info['account_code'] = self.orchestrator.detected_account_code
        self.orchestrator.project_info['platform_code'] = self.orchestrator.detected_platform_code
        
        print(f"📊 PROJECT INFO includes account/platform: {self.orchestrator.detected_account_code}/{self.orchestrator.detected_platform_code}")
    
    def _create_confirmation_data(self, asset_issues):
        """Create confirmation data for UI"""
        # Mock downloaded videos for UI (we'll download them during processing)
        mock_videos = ["video1.mp4", "video2.mp4", "video3.mp4"]  # Placeholder
        
        # Create confirmation data using the helper function
        confirmation_data = create_confirmation_data_from_orchestrator(
            card_data=self.orchestrator.card_data,
            processing_mode=self.orchestrator.processing_mode,
            project_info=self.orchestrator.project_info,
            downloaded_videos=mock_videos,
            validation_issues=asset_issues
        )
        
        # Store confirmation data for later access
        self.orchestrator.confirmation_data = confirmation_data
        
        return confirmation_data