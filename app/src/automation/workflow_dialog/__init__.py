# app/src/automation/workflow_dialog/__init__.py
"""
Workflow Dialog Module - Simplified imports to avoid circular dependencies
"""

# Import helper functions first (no dependencies)
from .helpers import (
    create_confirmation_data_from_orchestrator,
    create_processing_result_from_orchestrator
)

# Import the main dialog class
try:
    from .dialog_controller import UnifiedWorkflowDialog
except ImportError as e:
    print(f"Warning: Could not import UnifiedWorkflowDialog: {e}")
    # Fallback - we'll define this later
    UnifiedWorkflowDialog = None

# For backward compatibility
__all__ = [
    'UnifiedWorkflowDialog',
    'create_confirmation_data_from_orchestrator',
    'create_processing_result_from_orchestrator'
]