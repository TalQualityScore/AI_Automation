# app/src/automation/workflow_dialog/helpers.py - FIXED STANDALONE VERSION
"""
Workflow Dialog Helpers - Standalone Implementation
Fixed to avoid module import issues and attribute access errors
"""

import os
from ..workflow_data_models import ConfirmationData, ValidationIssue

def create_confirmation_data_from_orchestrator(card_data: dict, 
                                              processing_mode: str,
                                              project_info: dict,
                                              downloaded_videos: list,
                                              validation_issues: list = None):
    """
    Convert orchestrator data to ConfirmationData format
    FIXED: Standalone implementation to avoid import errors
    """
    
    print(f"🔄 Creating confirmation data...")

    # DEBUG: Show what videos are being passed
    print("=" * 50)
    print(f"DEBUG: Downloaded videos passed to helpers:")
    print(f"  Count: {len(downloaded_videos)}")
    for i, video in enumerate(downloaded_videos):
        print(f"  Video {i+1}: {video}")
    print("=" * 50)
    
    # Step 1: Get project name
    project_name = project_info.get('project_name', 'Unknown Project')
    
    # Step 2: Get account and platform from project_info (already detected)
    account_code = project_info.get('account_code', 'TR')
    platform_code = project_info.get('platform_code', 'FB')
    
    # Create display names
    account_mapping = {
        'OO': 'Olive Oil',
        'MCT': 'MCT',
        'BC3': 'Bio Complete 3', 
        'TR': 'Total Restore',
        'DS': 'Dark Spot',
        'NB': 'Natures Blend',
        'MK': 'Morning Kick'
    }
    
    platform_mapping = {
        'FB': 'Facebook',
        'YT': 'YouTube',
        'IG': 'Instagram',
        'TT': 'TikTok',
        'SNAP': 'Snapchat'
    }
    
    account_display = account_mapping.get(account_code, account_code)
    platform_display = platform_mapping.get(platform_code, platform_code)
    
    # Step 3: Generate templates based on processing mode
    templates = _generate_templates(processing_mode, platform_display)
    
    # Step 4: Calculate estimated time
    estimated_time = _calculate_time_estimate(len(downloaded_videos), processing_mode)
    
    # Step 5: Build output location
    output_location = _build_output_location(project_name, processing_mode)
    
    # Step 6: Get file sizes
    file_sizes = _get_file_sizes(downloaded_videos)
    
    # Step 7: Convert validation_issues to issues (CRITICAL FIX)
    issues = []
    if validation_issues:
        for issue in validation_issues:
            # Convert ValidationIssue objects to the format expected by ConfirmationData
            if hasattr(issue, 'message'):
                issues.append(ValidationIssue(
                    severity=getattr(issue, 'severity', 'info'),
                    message=issue.message
                ))
            else:
                # If it's just a string message
                issues.append(ValidationIssue(
                    severity='warning',
                    message=str(issue)
                ))
    
    # Step 8: Create the ConfirmationData object with CORRECT attribute names
    confirmation_data = ConfirmationData(
        project_name=project_name,
        account=account_display,
        platform=platform_display,
        processing_mode=processing_mode.replace('_', ' ').title(),
        client_videos=[os.path.basename(v) for v in downloaded_videos],
        templates_to_add=templates,
        output_location=output_location,
        estimated_time=estimated_time,
        issues=issues,  # ← CORRECT: Using 'issues' not 'validation_issues'
        file_sizes=file_sizes
    )
    
    print(f"✅ Confirmation data created successfully")
    print(f"   Project: {project_name}")
    print(f"   Account: {account_display}")
    print(f"   Platform: {platform_display}")
    print(f"   Mode: {processing_mode}")
    print(f"   Videos: {len(downloaded_videos)}")
    print(f"   Issues: {len(issues)}")
    
    return confirmation_data


def _generate_templates(processing_mode: str, platform_display: str) -> list:
    """Generate template descriptions based on processing mode"""
    templates = []
    
    if 'connector' in processing_mode.lower():
        templates.append(f"Blake Connector for {platform_display}")
    
    if 'quiz' in processing_mode.lower():
        templates.append(f"Quiz Outro for {platform_display}")
    elif 'svsl' in processing_mode.lower():
        templates.append(f"SVSL Template for {platform_display}")
    elif 'vsl' in processing_mode.lower():
        templates.append(f"VSL Template for {platform_display}")
    
    if not templates:
        templates.append("No additional templates")
    
    return templates


def _calculate_time_estimate(video_count: int, processing_mode: str) -> str:
    """Calculate estimated processing time"""
    base_time_per_video = 2  # minutes
    
    # Adjust based on processing mode complexity
    if 'connector' in processing_mode.lower():
        base_time_per_video += 1
    
    if 'svsl' in processing_mode.lower() or 'vsl' in processing_mode.lower():
        base_time_per_video += 1
    
    total_minutes = video_count * base_time_per_video
    
    if total_minutes < 60:
        return f"{total_minutes} minutes"
    else:
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours}h {minutes}m"


def _build_output_location(project_name: str, processing_mode: str) -> str:
    """Build output location string"""
    endpoint_type = "Quiz"  # Default
    
    if "svsl" in processing_mode.lower():
        endpoint_type = "SVSL"
    elif "vsl" in processing_mode.lower():
        endpoint_type = "VSL"
    
    return f"GH {project_name} {endpoint_type}"


def _get_file_sizes(video_paths: list) -> list:
    """Get file sizes for videos"""
    file_sizes = []
    
    for path in video_paths:
        try:
            if os.path.exists(path):
                size_bytes = os.path.getsize(path)
                size_mb = round(size_bytes / (1024 * 1024), 2)
                file_sizes.append((os.path.basename(path), size_mb))
            else:
                # For mock videos, use placeholder sizes
                file_sizes.append((os.path.basename(path), 0.0))
        except Exception:
            file_sizes.append((os.path.basename(path), 0.0))
    
    return file_sizes


def create_processing_result_from_orchestrator(processed_files: list,
                                              start_time: float,
                                              output_folder: str,
                                              success: bool = True):
    """
    Create processing result from orchestrator data
    FIXED: Standalone implementation
    """
    
    import time
    from ..workflow_data_models import ProcessingResult
    
    # Calculate duration
    duration_seconds = time.time() - start_time
    duration_minutes = int(duration_seconds // 60)
    duration_seconds = int(duration_seconds % 60)
    
    if duration_minutes > 0:
        duration_str = f"{duration_minutes}m {duration_seconds}s"
    else:
        duration_str = f"{duration_seconds}s"
    
    # Create result object
    result = ProcessingResult(
        success=success,
        duration=duration_str,
        processed_files=processed_files or [],
        output_folder=output_folder,
        error_message="",
        error_solution=""
    )
    
    print(f"✅ Processing result created: {duration_str}")
    return result


# Export the main functions
__all__ = [
    'create_confirmation_data_from_orchestrator',
    'create_processing_result_from_orchestrator'
]