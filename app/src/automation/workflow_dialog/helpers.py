# app/src/automation/workflow_dialog/helpers.py - Updated for SVSL/VSL support

import os
import time
import threading
import sys

from ..workflow_data_models import ConfirmationData, ValidationIssue, ProcessingResult

def create_confirmation_data_from_orchestrator(card_data: dict, 
                                             processing_mode: str,
                                             project_info: dict,
                                             downloaded_videos: list,
                                             validation_issues: list = None):
    """Convert orchestrator data to ConfirmationData format with SVSL/VSL support"""
    
    project_name = project_info.get('project_name', 'Unknown Project')
    
    # DEBUG: Print what we're analyzing
    card_title = card_data.get('name', '')
    print(f"🔍 HELPERS DEBUG - Card Title: '{card_title}'")
    print(f"🔍 HELPERS DEBUG - Project Name: '{project_name}'")
    print(f"🔍 HELPERS DEBUG - Processing Mode: '{processing_mode}'")
    print(f"🔍 HELPERS DEBUG - Available project_info keys: {list(project_info.keys())}")
    
    # FIXED: Try multiple sources for account/platform data
    detected_account_code = None
    detected_platform_code = None
    
    # Source 1: Check if already stored in project_info with various possible keys
    possible_account_keys = ['account_code', 'account', 'detected_account', 'detected_account_code']
    possible_platform_keys = ['platform_code', 'platform', 'detected_platform', 'detected_platform_code']
    
    for key in possible_account_keys:
        if key in project_info and project_info[key] and project_info[key] != 'UNKNOWN':
            detected_account_code = project_info[key]
            print(f"🎯 FOUND ACCOUNT in project_info['{key}']: '{detected_account_code}'")
            break
    
    for key in possible_platform_keys:
        if key in project_info and project_info[key] and project_info[key] != 'UNKNOWN':
            detected_platform_code = project_info[key]
            print(f"🎯 FOUND PLATFORM in project_info['{key}']: '{detected_platform_code}'")
            break
    
    # Source 2: Try to get from card_data if available
    if not detected_account_code or not detected_platform_code:
        if 'detected_account_code' in card_data:
            detected_account_code = card_data['detected_account_code']
            print(f"🎯 FOUND ACCOUNT in card_data: '{detected_account_code}'")
        if 'detected_platform_code' in card_data:
            detected_platform_code = card_data['detected_platform_code']
            print(f"🎯 FOUND PLATFORM in card_data: '{detected_platform_code}'")
    
    # Source 3: Try to re-detect from card title if still missing
    if (not detected_account_code or not detected_platform_code or 
        detected_account_code == 'UNKNOWN' or detected_platform_code == 'UNKNOWN'):
        
        print(f"🔍 ATTEMPTING FRESH DETECTION from card title...")
        
        try:
            # Import and use account mapper to re-detect
            from ..api_clients.account_mapper import AccountMapper
            mapper = AccountMapper()
            
            # Try detection without dialogs first
            fresh_account, fresh_platform = mapper.extract_account_and_platform(card_title, allow_fallback=False)
            
            if fresh_account and fresh_account != 'UNKNOWN':
                detected_account_code = fresh_account
                print(f"✅ FRESH ACCOUNT DETECTION: Account='{detected_account_code}'")
            
            if fresh_platform and fresh_platform != 'UNKNOWN':
                detected_platform_code = fresh_platform
                print(f"✅ FRESH PLATFORM DETECTION: Platform='{detected_platform_code}'")
            
            # Check if we got a complete detection
            if (detected_account_code and detected_account_code != 'UNKNOWN' and 
                detected_platform_code and detected_platform_code != 'UNKNOWN'):
                print(f"✅ FRESH DETECTION COMPLETE: Account='{detected_account_code}', Platform='{detected_platform_code}'")
            else:
                print(f"⚠️ PARTIAL DETECTION - will need user fallback: Account='{detected_account_code}', Platform='{detected_platform_code}'")
                
        except Exception as e:
            print(f"❌ ERROR during fresh detection: {e}")
    
    print(f"🎯 CURRENT STATUS: Account='{detected_account_code}', Platform='{detected_platform_code}'")
    
    # Source 4: FALLBACK DIALOG - Show user selection if still unknown
    if (not detected_account_code or not detected_platform_code or 
        detected_account_code == 'UNKNOWN' or detected_platform_code == 'UNKNOWN'):
        
        print(f"⚠️ ACCOUNT/PLATFORM DETECTION FAILED - Showing user fallback dialog")
        
        # ENHANCED DEBUG: Check environment before attempting dialog
        print(f"🔍 DEBUG - Threading info:")
        print(f"   Current thread: {threading.current_thread().name}")
        print(f"   Is main thread: {threading.current_thread() is threading.main_thread()}")
        
        # Check if we can show dialog
        if threading.current_thread() is threading.main_thread():
            try:
                print(f"✅ MAIN THREAD - Can show fallback dialog")
                
                # Show fallback dialog
                from ..api_clients.account_mapper.fallback_dialog import FallbackSelectionDialog
                fallback_dialog = FallbackSelectionDialog()
                
                # Pass the card title and any partial detections
                detected_account_code, detected_platform_code = fallback_dialog.show_fallback_selection(
                    card_title=card_title,
                    detected_account=detected_account_code if detected_account_code != 'UNKNOWN' else None,
                    detected_platform=detected_platform_code if detected_platform_code != 'UNKNOWN' else None,
                    card_url=card_data.get('shortUrl', '')
                )
                
                # Check if user cancelled
                if detected_account_code is None or detected_platform_code is None:
                    print("❌ USER CHOSE TO EXIT PROGRAM - Terminating application")
                    print("🔴 Program terminated by user choice in verification dialog")
                    sys.exit(0)  # Exit the entire program

                print(f"✅ USER FALLBACK SELECTION: Account='{detected_account_code}', Platform='{detected_platform_code}'")
                
            except Exception as dialog_error:
                print(f"❌ FALLBACK DIALOG ERROR: {dialog_error}")
                print(f"❌ ERROR TYPE: {type(dialog_error).__name__}")
                print(f"❌ ERROR ARGS: {dialog_error.args}")
                
                # Get detailed traceback
                import traceback
                print(f"❌ FULL TRACEBACK:")
                traceback.print_exc()
                
                # Emergency defaults
                detected_account_code = 'TR'
                detected_platform_code = 'FB'
                print(f"🔄 Using emergency defaults: Account='{detected_account_code}', Platform='{detected_platform_code}'")
        else:
            print(f"❌ BACKGROUND THREAD - Cannot show dialog, using defaults")
            detected_account_code = 'TR'
            detected_platform_code = 'FB'
    
    # Ensure we have valid values
    if not detected_account_code or detected_account_code == 'UNKNOWN':
        detected_account_code = 'TR'
    if not detected_platform_code or detected_platform_code == 'UNKNOWN':
        detected_platform_code = 'FB'
    
    # CRITICAL: Store the correct values back in project_info for other components
    project_info['account_code'] = detected_account_code
    project_info['platform_code'] = detected_platform_code
    project_info['detected_account_code'] = detected_account_code
    project_info['detected_platform_code'] = detected_platform_code
    
    print(f"✅ FINAL RESULT: Account='{detected_account_code}', Platform='{detected_platform_code}'")
    
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
        'SNAP': 'Snapchat',
        'REELS': 'Reels'
    }
    
    detected_account = f"{detected_account_code} ({account_mapping.get(detected_account_code, detected_account_code)})"
    detected_platform = platform_mapping.get(detected_platform_code, detected_platform_code)
    
    print(f"🎯 HELPERS FINAL - Account: {detected_account_code}, Platform: {detected_platform_code}")
    print(f"🎯 HELPERS FINAL - Processing Mode: {processing_mode}")
    
    # Determine templates based on processing mode - UPDATED FOR SVSL/VSL
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
    elif processing_mode == "connector_svsl":
        templates = [
            f"Add Blake connector ({detected_platform}/Connectors/) with slide transition",
            f"Add SVSL ({detected_platform}/SVSL/) with slide transition",
            "Apply professional slide transitions between segments"
        ]
    elif processing_mode == "svsl_only":
        templates = [
            f"Add SVSL ({detected_platform}/SVSL/) with slide transition",
            "Apply professional slide transitions"
        ]
    elif processing_mode == "connector_vsl":
        templates = [
            f"Add Blake connector ({detected_platform}/Connectors/) with slide transition",
            f"Add VSL ({detected_platform}/VSL/) with slide transition",
            "Apply professional slide transitions between segments"
        ]
    elif processing_mode == "vsl_only":
        templates = [
            f"Add VSL ({detected_platform}/VSL/) with slide transition",
            "Apply professional slide transitions"
        ]
    elif processing_mode == "save_only":
        templates = ["Save and rename videos (no processing)"]
    
    # Determine output location based on processing mode
    endpoint_type = "Quiz"  # Default
    if "svsl" in processing_mode:
        endpoint_type = "SVSL"
    elif "vsl" in processing_mode:
        endpoint_type = "VSL"
    
    output_location = f"GH {project_name} {project_info.get('ad_type', '')} {project_info.get('test_name', '')} {endpoint_type}"
    
    file_count = len(downloaded_videos)
    if processing_mode == "save_only":
        estimated_time = "Instant - Direct copying"
    else:
        estimated_time = f"{file_count * 2}-{file_count * 3} minutes (includes transitions)"
    
    file_sizes = [(os.path.basename(video), 150) for video in downloaded_videos]
    
    issues = []
    if validation_issues:
        for issue in validation_issues:
            # Check if issue is already a ValidationIssue object
            if isinstance(issue, ValidationIssue):
                issues.append(issue)
            # Handle dictionary format
            elif isinstance(issue, dict):
                issues.append(ValidationIssue(
                    severity=issue.get('severity', 'info'),
                    message=issue.get('message', str(issue))
                ))
            # Handle other formats
            else:
                issues.append(ValidationIssue(
                    severity='info',
                    message=str(issue)
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
            # Determine what type of endpoint was used
            endpoint_type = "quiz"
            if 'svsl_path' in file_info:
                endpoint_type = "svsl"
            elif 'vsl_path' in file_info:
                endpoint_type = "vsl"
            
            result_files.append({
                'version': file_info.get('version', f'v{i+1:02d}'),
                'source_file': file_info.get('source_file', f'unknown_{i+1}.mp4'),
                'output_name': file_info.get('output_name', f'processed_{i+1}'),
                'description': file_info.get('description', f'Processed video {i+1}'),
                'duration': file_info.get('duration', '0:00'),
                'size_mb': file_info.get('size_mb', 0),
                'connector_start': file_info.get('connector_start', ''),
                'endpoint_start': file_info.get(f'{endpoint_type}_start', ''),
                'total_duration': file_info.get('total_duration', '0:00'),
                'endpoint_type': endpoint_type
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
                'endpoint_start': '',
                'total_duration': '0:00',
                'endpoint_type': 'quiz'
            })
    
    return ProcessingResult(
        success=success,
        duration=duration_display,
        processed_files=result_files,
        output_folder=output_folder
    )