# app/src/automation/orchestrator/ui_preparation.py - ENHANCED FOR USER SELECTIONS
"""
UI Data Preparation Module
Handles preparation of confirmation data and project info parsing
Enhanced to respect user dropdown selections and prevent auto-detection override
"""

from ..workflow_dialog.helpers import create_confirmation_data_from_orchestrator
from ..workflow_utils import parse_project_info

class UIPreparation:
    """Handles UI data preparation and account detection with user selection support"""
    
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
        
        # Detect account and platform (only if not already user-selected)
        self._detect_account_and_platform()
        
        # Parse project info
        self.orchestrator.project_info = self._parse_project_info_for_ui(self.orchestrator.card_data)
        
        # Add detected codes to project_info
        self._add_detected_codes_to_project_info()
        
        # Determine processing mode (only if not already user-selected)
        self._determine_processing_mode()
        
        # CRITICAL FIX: Update validator with detected account/platform before validation
        self.orchestrator.validator.set_account_platform(
            self.orchestrator.detected_account_code, 
            self.orchestrator.detected_platform_code
        )
        print(f"🔧 ValidationEngine updated: Account={self.orchestrator.detected_account_code}, Platform={self.orchestrator.detected_platform_code}")

        # Validate assets
        asset_issues = self.orchestrator.validator.validate_assets(self.orchestrator.processing_mode)

        
        # Create and return confirmation data
        return self._create_confirmation_data(asset_issues)
    
    def _detect_account_and_platform(self):
        """Detect account and platform from card title (respects user selections)"""
        # NEW: Check if user has already made selections via dropdowns
        if (hasattr(self.orchestrator, 'user_selected_account') and 
            hasattr(self.orchestrator, 'user_selected_platform') and
            self.orchestrator.user_selected_account and 
            self.orchestrator.user_selected_platform):
            
            print(f"🎯 USING USER SELECTIONS: Account={self.orchestrator.user_selected_account}, Platform={self.orchestrator.user_selected_platform}")
            
            # Use user selections instead of auto-detection
            self.orchestrator.detected_account_code = self.orchestrator.user_selected_account
            self.orchestrator.detected_platform_code = self.orchestrator.user_selected_platform
            
            # Also store in card_data
            self.orchestrator.card_data['detected_account_code'] = self.orchestrator.user_selected_account
            self.orchestrator.card_data['detected_platform_code'] = self.orchestrator.user_selected_platform
            
            print(f"✅ User selections applied: Account='{self.orchestrator.user_selected_account}', Platform='{self.orchestrator.user_selected_platform}'")
            return
        
        # Original auto-detection logic (only runs if no user selections)
        try:
            from ..api_clients import AccountMapper
            mapper = AccountMapper()
            
            # Clear any cached data first
            mapper._clear_cache()
            
            print(f"🔍 ATTEMPTING AUTO-DETECTION from: '{self.orchestrator.original_card_title}'")
            
            account_code, platform_code = mapper.extract_account_and_platform(
                self.orchestrator.original_card_title, 
                allow_fallback=True  # Show dialog if detection fails
            )
            
            print(f"✅ Auto-detection result: Account='{account_code}', Platform='{platform_code}'")
            
            # Store for later use
            self.orchestrator.detected_account_code = account_code
            self.orchestrator.detected_platform_code = platform_code
            
            # Also store in card_data
            self.orchestrator.card_data['detected_account_code'] = account_code
            self.orchestrator.card_data['detected_platform_code'] = platform_code
            
        except Exception as detection_error:
            print(f"❌ CRITICAL: Account/Platform detection failed: {detection_error}")
            raise Exception(f"Cannot proceed without account/platform identification: {detection_error}")
    
    def _determine_processing_mode(self):
        """Determine processing mode (respects user selections)"""
        # NEW: Check if user has already selected a processing mode via dropdown
        if (hasattr(self.orchestrator, 'user_selected_mode') and 
            self.orchestrator.user_selected_mode):
            
            print(f"🎯 USING USER SELECTED MODE: {self.orchestrator.user_selected_mode}")
            self.orchestrator.processing_mode = self.orchestrator.user_selected_mode
            return
        
        # Original auto-parsing logic (only runs if no user selection)
        print(f"🔍 AUTO-DETECTING processing mode from card description")
        self.orchestrator.processing_mode = self.orchestrator.parser.parse_card_instructions(
            self.orchestrator.card_data.get('desc', '')
        )
        print(f"✅ Auto-detected processing mode: {self.orchestrator.processing_mode}")
    
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
        """Create confirmation data for UI with proper dropdown population"""
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
        
        # NEW: Enhance confirmation data with account/platform for dropdown display
        confirmation_data.account = self.orchestrator.detected_account_code
        confirmation_data.platform = self.orchestrator.detected_platform_code
        confirmation_data.processing_mode = self.orchestrator.processing_mode
        
        print(f"📋 CONFIRMATION DATA prepared with dropdowns:")
        print(f"   Account: {confirmation_data.account}")
        print(f"   Platform: {confirmation_data.platform}")
        print(f"   Processing Mode: {confirmation_data.processing_mode}")
        
        # Store confirmation data for later access
        self.orchestrator.confirmation_data = confirmation_data
        
        return confirmation_data
    
    def update_with_user_selections(self, user_selections):
        """NEW: Update orchestrator with user selections from dropdowns"""
        print(f"🔄 UPDATING ORCHESTRATOR with user selections: {user_selections}")
        
        if user_selections.get('account_code'):
            self.orchestrator.detected_account_code = user_selections['account_code']
            self.orchestrator.user_selected_account = user_selections['account_code']
            
            if hasattr(self.orchestrator, 'project_info'):
                self.orchestrator.project_info['account_code'] = user_selections['account_code']
                self.orchestrator.project_info['detected_account_code'] = user_selections['account_code']
        
        if user_selections.get('platform_code'):
            self.orchestrator.detected_platform_code = user_selections['platform_code']
            self.orchestrator.user_selected_platform = user_selections['platform_code']
            
            if hasattr(self.orchestrator, 'project_info'):
                self.orchestrator.project_info['platform_code'] = user_selections['platform_code']
                self.orchestrator.project_info['detected_platform_code'] = user_selections['platform_code']
        
        if user_selections.get('processing_mode'):
            self.orchestrator.processing_mode = user_selections['processing_mode']
            self.orchestrator.user_selected_mode = user_selections['processing_mode']
        
        if user_selections.get('project_name'):
            self.orchestrator.updated_project_name = user_selections['project_name']
            
            if hasattr(self.orchestrator, 'project_info'):
                self.orchestrator.project_info['project_name'] = user_selections['project_name']
        
        # Update validator with new account/platform
        if (user_selections.get('account_code') or user_selections.get('platform_code')) and hasattr(self.orchestrator, 'validator'):
            account = user_selections.get('account_code', self.orchestrator.detected_account_code)
            platform = user_selections.get('platform_code', self.orchestrator.detected_platform_code)
            
            self.orchestrator.validator.set_account_platform(account, platform)
            print(f"🔧 Validator updated with user selections: {account}/{platform}")
        
        print(f"✅ Orchestrator updated with all user selections")