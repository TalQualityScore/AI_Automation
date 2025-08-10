# app/src/automation/orchestrator/processing/__init__.py
"""
Processing Module - Handles all video processing steps
Broken down into smaller, manageable components for better maintainability
"""

from .steps_coordinator import ProcessingSteps

# Export the main class for backward compatibility
__all__ = ['ProcessingSteps']

# Module info
__version__ = "2.0.0"
__author__ = "AI Automation Suite"
__description__ = "Modular video processing pipeline"

print("✅ Processing Module v2.0.0 loaded")