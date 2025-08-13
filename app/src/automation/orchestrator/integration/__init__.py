# app/src/automation/orchestrator/integration/__init__.py
"""
Integration Module - Modular UI Integration System
Split from the 500+ line ui_integration_base.py into focused modules
"""

from .main_integration import UIIntegration
from .single_mode_processor import SingleModeProcessor
from .multi_mode_processor import MultiModeProcessor
from .mode_utilities import ModeUtilities
from .error_handling import IntegrationErrorHandler

# Export the main class for backward compatibility
__all__ = [
    'UIIntegration',
    'SingleModeProcessor', 
    'MultiModeProcessor',
    'ModeUtilities',
    'IntegrationErrorHandler'
]

# Version info
__version__ = "2.0.0"
__modular__ = True
__original_file__ = "ui_integration_base.py"
__original_lines__ = 500

print(f"✅ Integration Module v{__version__} loaded")
print(f"   Original: {__original_lines__} lines in 1 file")
print(f"   New: ~80 lines per file across 5 modules")