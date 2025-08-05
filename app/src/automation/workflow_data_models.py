# app/src/automation/workflow_data_models.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ValidationIssue:
    """Data structure for validation issues"""
    severity: str  # "warning", "error", "info"
    message: str

@dataclass
class ConfirmationData:
    """All data needed for the confirmation popup"""
    project_name: str
    account: str
    platform: str
    processing_mode: str
    client_videos: List[str]
    templates_to_add: List[str]
    output_location: str
    estimated_time: str
    issues: List[ValidationIssue]
    file_sizes: List[tuple]  # (filename, size_mb)

@dataclass
class ProcessingResult:
    """Enhanced results from processing operation with detailed video information"""
    success: bool
    duration: str
    processed_files: List[Dict]  # Enhanced with duration, file_size_mb, etc.
    output_folder: str
    error_message: str = ""
    error_solution: str = ""
    video_connections: List[Dict] = None  # NEW: Detailed breakdown of video assembly
    total_content_duration: str = ""  # NEW: Total duration of all content
    total_file_size_mb: int = 0  # NEW: Total file size