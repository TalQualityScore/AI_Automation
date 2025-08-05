# app/src/automation/workflow_dialog/helpers.py
import os
import time

from ..workflow_data_models import ConfirmationData, ValidationIssue, ProcessingResult

def create_confirmation_data_from_orchestrator(card_data: dict, 
                                             processing_mode: str,
                                             project_info: dict,
                                             downloaded_videos: list,
                                             validation_issues: list = None):
    """Convert orchestrator data to ConfirmationData format"""
    
    project_name = project_info.get('project_name', 'Unknown Project')
    
    # Account Detection from Card Title
    account_mapping = {
        'OO': 'Olive Oil',
        'MCT': 'Main Client', 
        'PP': 'Pro Plant',
        'GH': 'Green House',
        'AT': 'Auto Tech'
    }
    
    # Extract account code from card name
    card_title = card_data.get('name', '')
    detected_account = 'Unknown Account'
    
    for code, full_name in account_mapping.items():
        if code in card_title.upper():
            detected_account = f"{code} ({full_name})"
            break
    
    # Platform Detection from Card Title  
    platform_mapping = {
        'FB': 'Facebook',
        'YT': 'YouTube', 
        'SHORTS': 'YouTube Shorts',
        'TT': 'TikTok',
        'TIKTOK': 'TikTok'
    }
    
    detected_platform = 'YouTube'  # Default
    
    for code, full_name in platform_mapping.items():
        if code in card_title.upper():
            detected_platform = full_name
            break
    
    # Determine templates based on processing mode
    templates = []
    if processing_mode == "connector_quiz":
        templates = [
            f"Add Blake connector ({detected_platform}/Connectors/)",
            f"Add quiz outro ({detected_platform}/Quiz/)",
            "Apply slide transition effects"
        ]
    elif processing_mode == "quiz_only":
        templates = [
            f"Add quiz outro ({detected_platform}/Quiz/)",
            "Apply slide transition effects"  
        ]
    elif processing_mode == "save_only":
        templates = ["Save and rename videos"]
    
    output_location = f"GH {project_name} {project_info.get('ad_type', '')} {project_info.get('test_name', '')} Quiz"
    
    file_count = len(downloaded_videos)
    if processing_mode == "save_only":
        estimated_time = f"{file_count * 30} seconds - {file_count * 60} seconds"
    else:
        estimated_time = f"{file_count * 2}-{file_count * 3} minutes"
    
    file_sizes = [(os.path.basename(video), 150) for video in downloaded_videos]
    
    issues = []
    if validation_issues:
        for issue in validation_issues:
            issues.append(ValidationIssue(
                severity=issue.get('severity', 'info'),
                message=issue.get('message', str(issue))
            ))
    
    return ConfirmationData(
        project_name=project_name,
        account=detected_account,
        platform=detected_platform,
        processing_mode=processing_mode.replace('_', ' ').upper(),
        client_videos=[os.path.basename(video) for video in downloaded_videos],
        templates_to_add=templates,
        output_location=output_location,
        estimated_time=estimated_time,
        issues=issues,
        file_sizes=file_sizes
    )

def create_processing_result_from_orchestrator(processed_files: list,
                                             start_time: float,
                                             output_folder: str,
                                             success: bool = True):
    """Convert orchestrator results to ProcessingResult format"""
    
    duration_seconds = time.time() - start_time
    duration_minutes = int(duration_seconds // 60)
    duration_secs = int(duration_seconds % 60)
    duration_str = f"{duration_minutes} minutes {duration_secs} seconds"
    
    result_files = []
    for file_info in processed_files:
        result_files.append({
            'version': file_info.get('version', 'v01'),
            'source_file': file_info.get('source_file', 'unknown'),
            'output_name': file_info.get('output_name', 'processed_video'),
            'description': file_info.get('description', 'Processed video')
        })
    
    return ProcessingResult(
        success=success,
        duration=duration_str,
        processed_files=result_files,
        output_folder=output_folder
    )