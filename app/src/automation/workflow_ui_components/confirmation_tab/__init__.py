# app/src/automation/workflow_ui_components/confirmation_tab/__init__.py
"""
Confirmation Tab Module
Modular confirmation tab with organized sections
"""

from .main_tab import ConfirmationTab

# Import for backward compatibility - these were previously imported from confirmation_tab
from ...workflow_data_models import ConfirmationData, ValidationIssue

__all__ = ['ConfirmationTab', 'ConfirmationData', 'ValidationIssue']