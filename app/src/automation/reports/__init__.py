# app/src/automation/reports/__init__.py

"""
Reports Module for AI Automation Suite

This module handles generation of various reports including:
- Processing breakdown reports with video timings
- Future: Performance analytics reports
- Future: Error analysis reports
"""

from .breakdown_report import (
    generate_breakdown_report,
    get_video_duration,
    format_duration,
    format_timecode,
    integrate_with_processing
)

__all__ = [
    'generate_breakdown_report',
    'get_video_duration', 
    'format_duration',
    'format_timecode',
    'integrate_with_processing'
]