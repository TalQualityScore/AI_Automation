# app/src/automation/workflow_dialog/helpers.py - UPDATED with complete account list
import os
import time

from ..workflow_data_models import ConfirmationData, ValidationIssue, ProcessingResult

def create_confirmation_data_from_orchestrator(card_data: dict, 
                                             processing_mode: str,
                                             project_info: dict,
                                             downloaded_videos: list,
                                             validation_issues: list = None):
    """Convert orchestrator data to ConfirmationData format - UPDATED with complete accounts"""
    
    project_name = project_info.get('project_name', 'Unknown Project')
    
    # UPDATED: Complete Account Detection with all current accounts
    account_mapping = {
        # Full acronym + name pairs
        'NB': 'Nature\'s Blend',
        'MK': 'Morning Kick',
        'DRC': 'Dermal Repair Complex',
        'TR': 'Total Restore',
        'MCT': 'MCT',
        'PC': 'Phyto Collagen', 
        'GD': 'Glucose Defense',
        'OO': 'Olive Oil',
        'MC': 'Morning Complete',
        'DS': 'Dark Spot',
        'BC3': 'Bio Complete 3',
        'PP': 'Pro Plant',
        'SPC': 'Superfood Complete',
        'MA': 'Metabolic Advanced',
        'KA': 'Keto Active',
        'BLR': 'BadLand Ranch',
        
        # Special cases (full names only or unique patterns)
        'Bio X4': 'Bio X4',
        'Upwellness': 'Upwellness',
        
        # Spanish variants
        'MK ES': 'Morning Kick Espanol',
        'MCT ES': 'MCT Espanol', 
        'DS ES': 'Dark Spots Espanol',
    }
    
    # Account Detection from Card Title
    card_title = card_data.get('name', '')
    detected_account = 'Unknown Account'
    detected_account_code = 'UNKNOWN'
    
    # First, try to find exact matches (prioritizing longer matches first)
    account_codes = sorted(account_mapping.keys(), key=len, reverse=True)
    
    for code in account_codes:
        if code.upper() in card_title.upper():
            detected_account = f"{code} ({account_mapping[code]})"
            detected_account_code = code
            print(f"✅ Account detected: {code} -> {account_mapping[code]}")
            break
    
    # If no exact match, try partial matching for full names
    if detected_account_code == 'UNKNOWN':
        for code, full_name in account_mapping.items():
            # Check if any significant word from the full name appears in the title
            name_words = full_name.lower().split()
            for word in name_words:
                if len(word) > 3 and word in card_title.lower():  # Only check words longer than 3 chars
                    detected_account = f"{code} ({full_name})"
                    detected_account_code = code
                    print(f"✅ Account detected by name: {word} -> {code} ({full_name})")
                    break
            if detected_account_code != 'UNKNOWN':
                break
    
    # Enhanced Platform Detection from Card Title
    platform_mapping = {
        'FB': 'Facebook',
        'FACEBOOK': 'Facebook',
        'YT': 'YouTube', 
        'YOUTUBE': 'YouTube',
        'SHORTS': 'YouTube Shorts',
        'TT': 'TikTok',
        'TIKTOK': 'TikTok',
        'SNAP': 'Snapchat',
        'SNAPCHAT': 'Snapchat',
        'IG': 'Instagram',
        'INSTAGRAM': 'Instagram',
        'INSTA': 'Instagram',
        'TWITTER': 'Twitter',
        'X': 'Twitter/X',
        'LINKEDIN': 'LinkedIn'
    }
    
    detected_platform = 'YouTube'  # Default
    detected_platform_code = 'YT'
    
    # Prioritize longer platform names first
    platform_codes = sorted(platform_mapping.keys(), key=len, reverse=True)
    
    for code in platform_codes:
        if code in card_title.upper():
            detected_platform = platform_mapping[code]
            detected_platform_code = code
            print(f"✅ Platform detected: {code} -> {detected_platform}")
            break
    
    # Store account and platform codes for sheet detection
    project_info['account_code'] = detected_account_code
    project_info['platform_code'] = detected_platform_code
    
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
    duration_minutes = int(duration_seconds // 60)
    duration_secs = int(duration_seconds % 60)
    duration_str = f"{duration_minutes} minutes {duration_secs} seconds"
    
    # Enhanced file information with durations
    result_files = []
    total_content_duration = 0
    
    for file_info in processed_files:
        # Mock duration calculation (in real implementation, you'd get this from FFmpeg)
        mock_duration_seconds = 125 + (len(result_files) * 15)  # Varying durations
        duration_minutes = mock_duration_seconds // 60
        duration_seconds_remainder = mock_duration_seconds % 60
        duration_formatted = f"{duration_minutes}:{duration_seconds_remainder:02d}"
        
        total_content_duration += mock_duration_seconds
        
        enhanced_file_info = {
            'version': file_info.get('version', 'v01'),
            'source_file': file_info.get('source_file', 'unknown'),
            'output_name': file_info.get('output_name', 'processed_video'),
            'description': file_info.get('description', 'Processed video'),
            'duration': duration_formatted,
            'duration_seconds': mock_duration_seconds,
            'file_size_mb': 145 + (len(result_files) * 50),  # Mock file sizes
            'processing_mode': 'Save as is' if 'save' in file_info.get('description', '').lower() else 'Enhanced with templates'
        }
        result_files.append(enhanced_file_info)
    
    # Create video connections data for detailed breakdown
    video_connections = []
    for i, file_info in enumerate(result_files):
        connection_info = {
            'source': file_info['source_file'],
            'final_duration': file_info['duration'],
            'components': []
        }
        
        # Add components based on processing mode
        if 'connector' in file_info['description'].lower():
            connection_info['components'] = [
                f"Client Video ({file_info['duration']})",
                "Blake Connector (20s)", 
                "Quiz Outro (15s)"
            ]
        elif 'quiz' in file_info['description'].lower():
            connection_info['components'] = [
                f"Client Video ({file_info['duration']})",
                "Quiz Outro (15s)"
            ]
        else:
            connection_info['components'] = [f"Client Video ({file_info['duration']})"]
        
        video_connections.append(connection_info)
    
    # Calculate total duration
    total_minutes = total_content_duration // 60
    total_seconds = total_content_duration % 60
    total_duration_str = f"{total_minutes}:{total_seconds:02d}"
    
    from ..workflow_data_models import ProcessingResult
    
    result = ProcessingResult(
        success=success,
        duration=duration_str,
        processed_files=result_files,
        output_folder=output_folder
    )
    
    # Add video connections for detailed breakdown
    result.video_connections = video_connections
    result.total_content_duration = total_duration_str
    result.total_file_size_mb = sum(f['file_size_mb'] for f in result_files)
    
    return result