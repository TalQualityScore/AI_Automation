# app/src/automation/orchestrator/core.py
import time

# Import new modular components
from ..robust_monitoring import RobustMonitoringSystem
from ..validation_engine import ValidationEngine
from ..instruction_parser import InstructionParser

# Import UI components
from ..unified_workflow_dialog import UnifiedWorkflowDialog
from ..workflow_dialog.helpers import (create_confirmation_data_from_orchestrator, 
                                     create_processing_result_from_orchestrator)

from .processing_steps import ProcessingSteps
from .ui_integration_base import UIIntegration
from .error_handling import ErrorHandler

class AutomationOrchestrator:
    """Enhanced orchestrator with UI integration - Core class with delegated responsibilities"""
    
    def __init__(self):
        self.monitor = RobustMonitoringSystem()
        self.validator = ValidationEngine()
        self.parser = InstructionParser()
        self.trello_card_id = None
        self.start_time = None
        
        # Data for UI integration
        self.card_data = None
        self.processing_mode = None
        self.project_info = None
        self.downloaded_videos = None
        self.project_paths = None
        self.creds = None
        self.processed_files = None
        
        # Delegate responsibilities to focused classes
        self.processing_steps = ProcessingSteps(self)
        self.ui_integration = UIIntegration(self)
        self.error_handler = ErrorHandler(self)
    
    def execute_with_ui(self, trello_card_id=None):
        """Execute automation with UI workflow"""
        
        # If no card ID provided, show popup to get it
        if not trello_card_id:
            print("🎬 Starting AI Automation Suite - Getting Trello Card...")
            trello_card_id = UnifiedWorkflowDialog.get_trello_card_id()
            if not trello_card_id:
                print("❌ No Trello card ID provided. Automation cancelled.")
                return False
        
        self.trello_card_id = trello_card_id
        self.start_time = time.time()
        
        try:
            print("🚀 Starting AI Automation with UI Workflow")
            print(f"Card ID: {trello_card_id}")
            print("="*60)
            
            # Prepare data for confirmation dialog (delegated to UI integration)
            confirmation_data = self.ui_integration.prepare_confirmation_data()
            
            # Show unified workflow dialog
            dialog = UnifiedWorkflowDialog()
            success = dialog.show_workflow(
                confirmation_data=confirmation_data,
                processing_callback=self.ui_integration.ui_processing_callback
            )
            
            if success:
                print("\n" + "="*60)
                print("🎉 Automation completed successfully with UI!")
                print(f"📁 Project folder: {self.project_paths['project_root'] if self.project_paths else 'Unknown'}")
                print(f"📊 Processed {len(self.processed_files) if self.processed_files else 0} video(s)")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("❌ Automation cancelled by user")
                print("="*60)
            
            return success
            
        except Exception as e:
            self.error_handler.handle_automation_error(e, trello_card_id)
            return False
    
    def execute(self, trello_card_id):
        """Legacy headless execution - fallback for command line"""
        self.trello_card_id = trello_card_id
        self.start_time = time.time()
        
        try:
            print("🚀 Starting AI Automation (Headless Mode)")
            print(f"Card ID: {trello_card_id}")
            print("="*60)
            
            # Step 1: Fetch and Validate Card Data
            self.card_data = self.processing_steps.fetch_and_validate_card(trello_card_id)
            
            # Step 2: Parse Instructions and Validate Assets
            self.processing_mode, self.project_info = self.processing_steps.parse_and_validate(self.card_data)
            
            # Step 3: Setup Project and Download Files
            self.creds, self.downloaded_videos, self.project_paths = self.processing_steps.setup_project(self.card_data, self.project_info)
            
            # Step 4: Process Videos
            self.processed_files = self.processing_steps.process_videos(
                self.downloaded_videos, self.project_paths, self.project_info, 
                self.processing_mode, self.creds
            )
            
            # Step 5: Log Results and Cleanup
            self.processing_steps.finalize_and_cleanup(self.processed_files, self.project_info, self.creds, self.project_paths)
            
            print("\n" + "="*60)
            print("🎉 Automation finished successfully!")
            print(f"📁 Project folder: {self.project_paths['project_root']}")
            print(f"📊 Processed {len(self.processed_files)} video(s)")
            print("="*60)
            
        except Exception as e:
            self.error_handler.handle_automation_error(e, trello_card_id)
            
    class ActivityMonitor:
        """Simple activity monitor for long-running operations"""
        
        def __init__(self):
            self.active = False
            
        def execute_with_activity_monitoring(self, func, operation_name, no_activity_timeout=300):
            """
            Execute a function with activity monitoring
            
            Args:
                func: Function to execute
                operation_name: Name for logging
                no_activity_timeout: Timeout in seconds (not enforced in simple version)
            
            Returns:
                Result from the function
            """
            print(f"⏱️ Starting: {operation_name}")
            self.active = True
            
            try:
                result = func()
                print(f"✅ Completed: {operation_name}")
                return result
            except Exception as e:
                print(f"❌ Failed: {operation_name} - {str(e)}")
                raise
            finally:
                self.active = False