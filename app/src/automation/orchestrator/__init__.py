# app/src/automation/orchestrator/__init__.py
"""
Automation Orchestrator Module - REFACTORED

This module contains the main orchestration logic split into focused components:
- AutomationOrchestrator: Core orchestrator class that delegates responsibilities
- ProcessingSteps: Handles individual processing steps (fetch, validate, process, etc.)
- UIIntegration: Main UI integration orchestrator (now split into sub-modules)
  - UIPreparation: Handles data preparation and account detection
  - UIProcessing: Handles video processing with progress
  - UIProgress: Handles project name updates
  - UISheets: Handles Google Sheets and reporting
- ErrorHandler: Manages error handling and solution generation

The main entry point remains the same for backward compatibility.
"""

import sys
from .core import AutomationOrchestrator
from .processing_steps import ProcessingSteps
from .ui_integration_base import UIIntegration  # Changed from ui_integration to ui_integration_base
from .error_handling import ErrorHandler

# Also export the new modules for direct access if needed
from .ui_preparation import UIPreparation
from .ui_processing import UIProcessing
from .ui_progress import UIProgress
from .ui_sheets import UISheets

def main(card_id=None, use_ui=True):
    """Main entry point for automation - SIMPLIFIED"""
    orchestrator = AutomationOrchestrator()
    
    if use_ui:
        # Try UI mode first
        try:
            return orchestrator.execute_with_ui(card_id)  # card_id can be None
        except Exception as ui_error:
            print(f"UI mode failed: {ui_error}")
            if card_id:  # Only fallback if we have a card_id
                print("Falling back to headless mode...")
                orchestrator.execute(card_id)
            else:
                print("No card ID available for headless fallback.")
                return False
    else:
        # Direct headless execution (requires card_id)
        if card_id:
            orchestrator.execute(card_id)
            return True
        else:
            print("❌ Headless mode requires a Trello card ID")
            return False

# Export the main function and classes for backward compatibility
__all__ = [
    'AutomationOrchestrator', 
    'ProcessingSteps', 
    'UIIntegration',  # Main orchestrator
    'UIPreparation',  # New sub-modules
    'UIProcessing',
    'UIProgress', 
    'UISheets',
    'ErrorHandler', 
    'main'
]