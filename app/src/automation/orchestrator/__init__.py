# app/src/automation/orchestrator/__init__.py
"""
Automation Orchestrator Module

This module contains the main orchestration logic split into focused components:
- AutomationOrchestrator: Core orchestrator class that delegates responsibilities
- ProcessingSteps: Handles individual processing steps (fetch, validate, process, etc.)
- UIIntegration: Handles UI-specific methods and callbacks
- ErrorHandler: Manages error handling and solution generation

The main entry point remains the same for backward compatibility.
"""

import sys
from .core import AutomationOrchestrator
from .processing_steps import ProcessingSteps
from .ui_integration import UIIntegration
from .error_handling import ErrorHandler

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

# Export the main function for backward compatibility
__all__ = ['AutomationOrchestrator', 'ProcessingSteps', 'UIIntegration', 'ErrorHandler', 'main']