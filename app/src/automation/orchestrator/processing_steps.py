# app/src/automation/orchestrator/processing_steps.py
"""
REDIRECT FILE - For backward compatibility
The ProcessingSteps class has been refactored into smaller modules
located in the processing/ folder for better maintainability.

This file ensures existing imports continue to work.
"""

# Import from the new modular structure
from .processing import ProcessingSteps

# Export for backward compatibility
__all__ = ['ProcessingSteps']

# Log that we're using the new modular version
print("📦 ProcessingSteps loaded from new modular structure (processing/)")

# Optional: Add deprecation warning (uncomment if you want to phase this out later)
# import warnings
# warnings.warn(
#     "Importing ProcessingSteps from processing_steps.py is deprecated. "
#     "Please import from processing/ instead: "
#     "from app.src.automation.orchestrator.processing import ProcessingSteps",
#     DeprecationWarning,
#     stacklevel=2
# )