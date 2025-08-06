# app/src/automation/workflow_utils.py - FIXED VERSION LETTER EXTRACTION

import os
import shutil
import time
import tempfile

def parse_project_info(folder_name):
    """Parse project information from folder name - FIXED TO EXTRACT CORRECT VERSION LETTERS"""
    print(f"Parsing folder name: {folder_name}")
    
    # Import here to avoid circular imports
    from ...naming_generator import clean_project_name
    
    # FIXED: Better patterns with priority order - focusing on extracting from actual filenames
    patterns = [
        # Pattern 1: Standard OO format - OO_[FULL_PROJECT]_AD_[TYPE]-[NUMBER]
        r'OO_(.*?)_AD_([A-Z]+)-(\d+).*?([A-Z])_\d+\.mp4',
        
        # Pattern 2: Standard OO format without file extension  
        r'OO_(.*?)_AD_([A-Z]+)-(\d+).*?([A-Z])_\d+',
        
        # Pattern 3: AD-It format - OO_[FULL_PROJECT]_AD-It_[TYPE]-[NUMBER]
        r'OO_(.*?)_AD-It_([A-Z]+)-(\d+).*?([A-Z])_?\d*',
        
        # Pattern 4: AD-It format without letter
        r'OO_(.*?)_AD-It_([A-Z]+)-(\d+)',
        
        # Pattern 5: Modern format with OPT - [COMPANY]_[PREFIX]_[PROJECT]_OPT_[ADTYPE]-[NUMBER]_[DATE][LETTER]
        # FIXED: Don't extract version letter from here, get it from actual filenames later
        r'([A-Z0-9_]+)_([A-Z0-9]+)_(.*?)_OPT_([A-Z]+)-(\d+)',
        
        # Pattern 6: GH prefix format - should extract the FULL project part, not just prefix
        r'GH\s+OO_(.*?)_AD[_-](?:It_)?([A-Z]+)-(\d+)',
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, folder_name)
        if match:
            groups = match.groups()
            print(f"Pattern {i+1} matched with {len(groups)} groups: {groups}")
            
            if i in [0, 1]:  # Standard OO patterns with letter
                if len(groups) >= 4:
                    raw_project_name = groups[0]
                    ad_type = groups[1]
                    test_name = groups[2]
                    version_letter = groups[3] if len(groups) > 3 else ""
                else:
                    raw_project_name = groups[0]
                    ad_type = groups[1]
                    test_name = groups[2]
                    version_letter = ""
                project_name = clean_project_name(raw_project_name)
                
            elif i in [2, 3]:  # AD-It patterns
                raw_project_name = groups[0]
                ad_type = groups[1]
                test_name = groups[2]
                version_letter = groups[3] if len(groups) > 3 else ""
                project_name = clean_project_name(raw_project_name)
                
            elif i == 4:  # Modern format with OPT - FIXED
                company = groups[0]
                prefix = groups[1]
                raw_project_name = groups[2]
                ad_type = groups[3]
                test_name = groups[4]
                # CRITICAL FIX: Don't try to extract version letter from pattern match
                # We'll extract it from actual filenames later
                version_letter = ""
                combined_name = f"{company} {raw_project_name}".replace('_', ' ')
                project_name = clean_project_name(combined_name)
                    
            elif i == 5:  # GH format - FIXED to extract full project name
                raw_project_name = groups[0]  # This should be the full project name after OO_
                ad_type = groups[1]
                test_name = groups[2]
                version_letter = ""
                project_name = clean_project_name(raw_project_name)
            
            # CRITICAL FIX: Extract version letter from the FULL folder name using better pattern
            # Look for _250416D pattern specifically
            if not version_letter:
                # Try to find version letter from date+letter pattern in the full folder name
                version_letter_match = re.search(r'_(\d{6})([A-D])(?:\s|$|\))', folder_name)
                if version_letter_match:
                    version_letter = version_letter_match.group(2)
                    print(f"🔍 EXTRACTED VERSION LETTER from date pattern: '{version_letter}'")
                else:
                    # Fallback: look for any pattern with test number + letter
                    version_letter_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)([A-D])(?:\s|$|\))', folder_name) 
                    if version_letter_match:
                        version_letter = version_letter_match.group(2)
                        print(f"🔍 EXTRACTED VERSION LETTER from test pattern: '{version_letter}'")
                    else:
                        version_letter = ""
                        print(f"🔍 NO VERSION LETTER found in folder name")
            
            print(f"Extracted: '{raw_project_name}' -> '{project_name}' (Type: {ad_type}, Test: {test_name}, Letter: {version_letter})")
            
            return {
                "project_name": project_name,
                "ad_type": ad_type, 
                "test_name": test_name,
                "version_letter": version_letter
            }
    
    print(f"No pattern matched. Attempting manual extraction...")
    
    # Manual fallback extraction - ENHANCED for ANY account prefix
    import re
    ad_type_match = re.search(r'(VTD|STOR|ACT)', folder_name)
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', folder_name)
    
    if ad_type_match and test_name_match:
        # Try different account prefix patterns
        project_patterns = [
            r'([A-Z]+W?)_(.*?)_AD_(?:VTD|STOR|ACT)',
            r'([A-Z]+)_(.*?)_AD-It_(?:VTD|STOR|ACT)',
            r'([A-Z]+)_(.*?)_AD_(?:VTD|STOR|ACT)',
            r'([A-Z]+)_(.*?)_(?:VTD|STOR|ACT)',
        ]
        
        for pattern in project_patterns:
            project_match = re.search(pattern, folder_name)
            if project_match:
                groups = project_match.groups()
                if len(groups) >= 2:
                    raw_project_name = groups[1]
                    if len(raw_project_name) > 3 or not raw_project_name.isupper():
                        from ...naming_generator import clean_project_name
                        project_name = clean_project_name(raw_project_name)
                        
                        # Try to extract version letter
                        version_letter = ""
                        version_letter_match = re.search(r'_(\d{6})([A-D])(?:\s|$|\))', folder_name)
                        if version_letter_match:
                            version_letter = version_letter_match.group(2)
                        
                        print(f"Manual extraction: '{raw_project_name}' -> '{project_name}' (Letter: {version_letter})")
                        
                        return {
                            "project_name": project_name,
                            "ad_type": ad_type_match.group(1),
                            "test_name": test_name_match.group(1),
                            "version_letter": version_letter
                        }
    
    print(f"Failed to parse folder name: {folder_name}")
    return None

def create_project_structure(project_folder_name):
    """Creates the standard project folder structure."""
    
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    project_path = os.path.join(desktop_path, project_folder_name)
    
    try:
        # Create main project folder
        os.makedirs(project_path, exist_ok=True)
        
        # Create subfolders
        subfolders = ["Source_Videos", "Processed_Videos", "Breakdown_Files"]
        for subfolder in subfolders:
            subfolder_path = os.path.join(project_path, subfolder)
            os.makedirs(subfolder_path, exist_ok=True)
        
        print(f"📁 PROJECT STRUCTURE CREATED AT: '{project_path}'")
        
        return {
            "project_folder": project_path,
            "source_videos": os.path.join(project_path, "Source_Videos"),
            "processed_videos": os.path.join(project_path, "Processed_Videos"),
            "breakdown_files": os.path.join(project_path, "Breakdown_Files")
        }
        
    except Exception as e:
        print(f"❌ ERROR creating project structure: {e}")
        return None

def copy_videos_to_source_folder(downloaded_videos, source_folder):
    """Copy downloaded videos to the source folder."""
    
    copied_videos = []
    
    for video_path in downloaded_videos:
        try:
            if os.path.exists(video_path):
                filename = os.path.basename(video_path)
                destination = os.path.join(source_folder, filename)
                
                shutil.copy2(video_path, destination)
                copied_videos.append(destination)
                print(f"📁 Copied: {filename}")
            else:
                print(f"⚠️ Video not found: {video_path}")
                
        except Exception as e:
            print(f"❌ Error copying {video_path}: {e}")
    
    return copied_videos

def cleanup_temp_files(temp_folder):
    """Clean up temporary files and folders."""
    
    try:
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
            print(f"🧹 Cleaned up temporary folder: {temp_folder}")
    except Exception as e:
        print(f"⚠️ Warning: Could not clean up {temp_folder}: {e}")

def get_video_file_info(video_path):
    """Get basic information about a video file."""
    
    try:
        if not os.path.exists(video_path):
            return None
        
        file_size = os.path.getsize(video_path)
        file_size_mb = round(file_size / (1024 * 1024), 1)
        
        return {
            "filename": os.path.basename(video_path),
            "full_path": video_path,
            "size_bytes": file_size,
            "size_mb": file_size_mb,
            "extension": os.path.splitext(video_path)[1].lower()
        }
        
    except Exception as e:
        print(f"❌ Error getting video info for {video_path}: {e}")
        return None

def validate_video_files(video_paths):
    """Validate that video files exist and are accessible."""
    
    valid_videos = []
    invalid_videos = []
    
    for video_path in video_paths:
        if os.path.exists(video_path) and os.path.isfile(video_path):
            # Check if it's a video file by extension
            ext = os.path.splitext(video_path)[1].lower()
            if ext in ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv']:
                valid_videos.append(video_path)
            else:
                invalid_videos.append(f"{video_path} (not a video file)")
        else:
            invalid_videos.append(f"{video_path} (file not found)")
    
    return valid_videos, invalid_videos

def create_temp_working_directory():
    """Create a temporary working directory for processing."""
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="ai_automation_")
        print(f"📁 Created temporary working directory: {temp_dir}")
        return temp_dir
    except Exception as e:
        print(f"❌ Error creating temporary directory: {e}")
        return None

def move_files_to_final_location(temp_files, final_folder):
    """Move processed files from temp location to final project folder."""
    
    moved_files = []
    
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                filename = os.path.basename(temp_file)
                final_path = os.path.join(final_folder, filename)
                
                shutil.move(temp_file, final_path)
                moved_files.append(final_path)
                print(f"📁 Moved to final location: {filename}")
            else:
                print(f"⚠️ Temp file not found: {temp_file}")
                
        except Exception as e:
            print(f"❌ Error moving {temp_file}: {e}")
    
    return moved_files