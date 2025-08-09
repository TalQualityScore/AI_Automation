# app/src/automation/workflow_utils_modules/__init__.py
"""
Workflow utilities module - split from the original workflow_utils.py
Exports all functions to maintain backward compatibility
"""

from .project_parser import parse_project_info
from .project_structure import create_project_structure
from .folder_parser import (
    extract_folder_name_from_drive_link,
    parse_standard_format,
    parse_alternative_format,
    parse_legacy_format
)
from .validation import (
    validate_project_info,
    clean_project_name,
    extract_version_letter
)

# Export all functions for backward compatibility
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