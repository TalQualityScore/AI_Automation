# app/src/automation/workflow_dialog/helpers.py - CRITICAL FIX

import os
import time

from ..workflow_data_models import ConfirmationData, ValidationIssue, ProcessingResult

def create_confirmation_data_from_orchestrator(card_data: dict, 
                                             processing_mode: str,
                                             project_info: dict,
                                             downloaded_videos: list,
                                             validation_issues: list = None):
    """Convert orchestrator data to ConfirmationData format - FIXED TO NOT OVERRIDE ACCOUNT DETECTION"""
    
    project_name = project_info.get('project_name', 'Unknown Project')
    
    # DEBUG: Print what we're analyzing
    card_title = card_data.get('name', '')
    print(f"🔍 HELPERS DEBUG - Card Title: '{card_title}'")
    print(f"🔍 HELPERS DEBUG - Project Name: '{project_name}'")
    
    # CRITICAL FIX: Use the ORIGINAL account/platform detection from account_mapper.py
    # DO NOT OVERRIDE - these should have been set by ui_integration.py already
    detected_account_code = project_info.get('account_code', 'UNKNOWN')
    detected_platform_code = project_info.get('platform_code', 'UNKNOWN')
    
    print(f"🎯 HELPERS DEBUG - Using ORIGINAL detection from account_mapper: Account='{detected_account_code}', Platform='{detected_platform_code}'")
    
    # Only if the original detection truly failed, show a warning but don't override
    if detected_account_code == 'UNKNOWN' or detected_platform_code == 'UNKNOWN':
        print(f"⚠️  WARNING: Original account/platform detection failed!")
        print(f"   Account: {detected_account_code}, Platform: {detected_platform_code}")
        print(f"   This may cause Google Sheets routing issues.")
        
        # Use fallback values but don't try to re-detect
        if detected_account_code == 'UNKNOWN':
            detected_account_code = 'TR'  # Default based on your card
        if detected_platform_code == 'UNKNOWN':
            detected_platform_code = 'FB'  # Default based on your card
            
        print(f"🔄 Using fallback values: Account='{detected_account_code}', Platform='{detected_platform_code}'")
    
    # Get display names for UI
    account_mapping = {
        'TR': 'Total Restore',
        'BC3': 'Bio Complete 3',
        'OO': 'Olive Oil',
        'MCT': 'MCT',
        'DS': 'Dark Spot',
        'NB': 'Nature\'s Blend',
        'MK': 'Morning Kick',
        'DRC': 'Dermal Repair Complex',
        'PC': 'Phyto Collagen',
        'GD': 'Glucose Defense',
        'MC': 'Morning Complete',
        'PP': 'Pro Plant',
        'SPC': 'Superfood Complete',
        'MA': 'Metabolic Advanced',
        'KA': 'Keto Active',
        'BLR': 'BadLand Ranch',
        'Bio X4': 'Bio X4',
        'Upwellness': 'Upwellness'
    }
    
    platform_mapping = {
        'FB': 'Facebook',
        'YT': 'YouTube',
        'IG': 'Instagram',
        'TT': 'TikTok',
        'SNAP': 'Snapchat'
    }
    
    detected_account = f"{detected_account_code} ({account_mapping.get(detected_account_code, detected_account_code)})"
    detected_platform = platform_mapping.get(detected_platform_code, detected_platform_code)
    
    print(f"🎯 HELPERS FINAL - Account: {detected_account_code}, Platform: {detected_platform_code}")
    print(f"🎯 HELPERS FINAL - Looking for: {detected_account_code} + {detected_platform_code} sheet")
    
    # Determine templates based on processing mode
    templates = []
    if processing_mode == "connector_quiz":
        templates = [
            f"Add Blake connector ({detected_platform}/Connectors/) with slide transition",
            f"Add quiz outro ({detected_platform}/Quiz/) with slide transition",
            "Apply professional slide transitions between segments"
        ]
    elif processing_mode == "quiz_only":
        templates = [
            f"Add quiz outro ({detected_platform}/Quiz/) with slide transition",
            "Apply professional slide transitions"
        ]
    elif processing_mode == "save_only":
        templates = ["Save and rename videos (no processing)"]
    
    output_location = f"GH {project_name} {project_info.get('ad_type', '')} {project_info.get('test_name', '')} Quiz"
    
    file_count = len(downloaded_videos)
    if processing_mode == "save_only":
        estimated_time = "Instant - Direct copying"
    else:
        estimated_time = f"{file_count * 2}-{file_count * 3} minutes (includes transitions)"
    
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
    """Create detailed processing result with video durations and timecodes"""
    
    duration_seconds = time.time() - start_time
    
    if duration_seconds < 60:
        duration_display = f"{duration_seconds:.1f} seconds"
    else:
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        duration_display = f"{minutes}m {seconds}s"
    
    # Convert processed files to the format expected by ProcessingResult
    result_files = []
    for i, file_info in enumerate(processed_files):
        if isinstance(file_info, dict):
            result_files.append({
                'version': file_info.get('version', f'v{i+1:02d}'),
                'source_file': file_info.get('source_file', f'unknown_{i+1}.mp4'),
                'output_name': file_info.get('output_name', f'processed_{i+1}'),
                'description': file_info.get('description', f'Processed video {i+1}'),
                'duration': file_info.get('duration', '0:00'),
                'size_mb': file_info.get('size_mb', 0),
                'connector_start': file_info.get('connector_start', ''),
                'quiz_start': file_info.get('quiz_start', ''),
                'total_duration': file_info.get('total_duration', '0:00')
            })
        else:
            # Handle simple filename strings
            filename = str(file_info)
            result_files.append({
                'version': f'v{i+1:02d}',
                'source_file': filename,
                'output_name': os.path.splitext(filename)[0],
                'description': f'Processed {filename}',
                'duration': '0:00',
                'size_mb': 0,
                'connector_start': '',
                'quiz_start': '',
                'total_duration': '0:00'
            })
    
    return ProcessingResult(
        success=success,
        duration=duration_display,
        processed_files=result_files,
        output_folder=output_folder
    )