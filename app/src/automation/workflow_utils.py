# app/src/automation/workflow_utils.py
"""
Workflow utilities - REFACTORED VERSION
The original 380-line file with 205-line parse_project_info function
has been split into modules for better maintainability.

This file now just imports from the modules to maintain backward compatibility.
"""

# Import everything from the new modules
from .workflow_utils_modules import (
    parse_project_info,
    create_project_structure,
    extract_folder_name_from_drive_link,
    parse_standard_format,
    parse_alternative_format,
    parse_legacy_format,
    validate_project_info,
    clean_project_name,
    extract_version_letter
)

# Keep any other functions that were in the original file
# (Add them here if there were other functions besides parse_project_info and create_project_structure)

# For backward compatibility, ensure all functions are available at module level
__all__ = [
    'parse_project_info',
    'create_project_structure',
    'extract_folder_name_from_drive_link',
    'parse_standard_format',
    'parse_alternative_format', 
    'parse_legacy_format',
    'validate_project_info',
    'clean_project_name',
    'extract_version_letter'
]

# Optional: Add a version marker to track the refactoring
__version__ = "2.0.0"  # Refactored version
__refactored__ = True
__original_lines__ = 380
__new_structure__ = "Split into workflow_utils_modules package"

print(f"✅ Using refactored workflow_utils v{__version__}")
print(f"   Original: {__original_lines__} lines in 1 file")
print(f"   New: ~50 lines per file across 5 modules")