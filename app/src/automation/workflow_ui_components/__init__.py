# app/src/automation/workflow_ui_components/__init__.py
"""
Workflow UI Components Module

This module contains all the UI components for the automation workflow:
- WorkflowTheme: Handles theming and styling
- ConfirmationTab: Shows project confirmation dialog
- ProcessingTab: Shows progress during processing
- ResultsTab: Shows success/error results
- NotificationPopup: Handles notification settings
- Helper functions: open_folder, copy_to_clipboard, generate_error_solution
"""

from .theme import WorkflowTheme
from .confirmation_tab import ConfirmationTab, ConfirmationData, ValidationIssue
from .processing_tab import ProcessingTab
from .results_tab import ResultsTab
from .notification_popup import NotificationPopup
from .helpers import open_folder, copy_to_clipboard, generate_error_solution

__all__ = [
    'WorkflowTheme',
    'ConfirmationTab',
    'ConfirmationData',  # Added this
    'ValidationIssue',   # Added this
    'ProcessingTab',
    'ResultsTab',
    'NotificationPopup',
    'open_folder',
    'copy_to_clipboard',
    'generate_error_solution'
]