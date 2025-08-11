# app/src/automation/workflow_ui_components/confirmation_tab.py
"""
Backward Compatibility Import
Redirects to the new modular confirmation tab
"""

# Simple import redirect for backward compatibility
from .confirmation_tab.main_tab import ConfirmationTab

# This ensures existing imports still work:
# from ..workflow_ui_components import ConfirmationTab
# or
# from .confirmation_tab import ConfirmationTab