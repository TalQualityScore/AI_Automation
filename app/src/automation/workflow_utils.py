# app/src/automation/workflow_utils.py - FIXED: Restore original folder structure

import os
import shutil
import time
import tempfile
import re   

def parse_project_info(folder_name):
    """Parse project information from folder name - FIXED TO EXTRACT CORRECT VERSION LETTERS"""
    print(f"Parsing folder name: {folder_name}")
    
    # Import here to avoid circular imports
    from app.naming_generator import clean_project_name
    
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
            
            if i < 2:  # Standard OO patterns
                if len(groups) >= 4:
                    raw_project_name = groups[0]
                    ad_type = groups[1]
                    test_name = groups[2]
                    version_letter = groups[3]
                else:
                    raw_project_name = groups[0]
                    ad_type = groups[1]
                    test_name = groups[2]
                    version_letter = ""
                    
                project_name = clean_project_name(raw_project_name)
                
                print(f"Extracted: '{raw_project_name}' -> '{project_name}' (Type: {ad_type}, Test: {test_name}, Letter: {version_letter})")
                
                return {
                    "project_name": project_name,
                    "ad_type": ad_type,
                    "test_name": test_name,
                    "version_letter": version_letter
                }
                
            elif i == 2 or i == 3:  # AD-It patterns
                raw_project_name = groups[0]
                ad_type = groups[1]
                test_name = groups[2]
                version_letter = groups[3] if len(groups) > 3 else ""
                
                project_name = clean_project_name(raw_project_name)
                
                print(f"Extracted: '{raw_project_name}' -> '{project_name}' (Type: {ad_type}, Test: {test_name}, Letter: {version_letter})")
                
                return {
                    "project_name": project_name,
                    "ad_type": ad_type,
                    "test_name": test_name,
                    "version_letter": version_letter
                }
                
            elif i == 4:  # Modern OPT format
                if len(groups) >= 5:
                    company = groups[0]
                    prefix = groups[1]
                    raw_project_name = groups[2]
                    ad_type = groups[3]
                    test_name = groups[4]
                    
                    # Build combined project name
                    combined_name = f"{company} {prefix} {raw_project_name}"
                    project_name = clean_project_name(combined_name)
                    
                    # CRITICAL FIX: Remove account prefixes immediately after cleaning
                    # Import the function directly to avoid path issues
                    def remove_account_prefix(project_name):
                        """Remove account prefixes like 'AGMD', 'BC3', etc. from project name"""
                        account_prefixes = [
                            'AGMD', 'BC3', 'TR', 'OO', 'MCT', 'DS', 'NB', 'MK', 
                            'DRC', 'PC', 'GD', 'MC', 'PP', 'SPC', 'MA', 'KA', 'BLR',
                            'GMD', 'TOTAL', 'RESTORE', 'BIO', 'COMPLETE', 'OLIVE', 'OIL'
                        ]
                        
                        words = project_name.split()
                        
                        # Remove account prefixes from the beginning
                        while words:
                            first_word = words[0].upper()
                            if first_word in account_prefixes:
                                print(f"🧹 REMOVING ACCOUNT PREFIX: '{words[0]}'")
                                words = words[1:]
                            else:
                                break
                        
                        # Also check for combined prefixes like "AGMD BC3"
                        if len(words) >= 2:
                            combined = f"{words[0]} {words[1]}".upper()
                            if any(prefix in combined for prefix in account_prefixes):
                                while words and len(words[0]) <= 4 and words[0].upper() in account_prefixes:
                                    print(f"🧹 REMOVING ADDITIONAL PREFIX: '{words[0]}'")
                                    words = words[1:]
                        
                        cleaned_name = ' '.join(words) if words else project_name
                        
                        if cleaned_name != project_name:
                            print(f"🧹 ACCOUNT PREFIX REMOVAL: '{project_name}' → '{cleaned_name}'")
                        
                        return cleaned_name if cleaned_name.strip() else project_name

                    # Apply the account prefix removal
                    project_name = remove_account_prefix(project_name)
                    
                    # Try to extract version letter from folder name separately
                    version_letter = ""
                    version_letter_match = re.search(r'_(\d+)([A-Z])(?:\s|$|\))', folder_name)
                    if version_letter_match:
                        version_letter = version_letter_match.group(2)
                    
                    print(f"Extracted: '{combined_name}' -> '{project_name}' (Type: {ad_type}, Test: {test_name}, Letter: {version_letter})")
                    
                    return {
                        "project_name": project_name,
                        "ad_type": ad_type,
                        "test_name": test_name,
                        "version_letter": version_letter
                    }
                    
            elif i == 5:  # GH prefix format
                raw_project_name = groups[0]
                ad_type = groups[1]
                test_name = groups[2]
                
                project_name = clean_project_name(raw_project_name)
                
                # Try to extract version letter from folder name
                version_letter = ""
                version_letter_match = re.search(r'_(\d+)([A-Z])(?:\s|$|\))', folder_name)
                if version_letter_match:
                    version_letter = version_letter_match.group(2)
                
                print(f"Extracted: '{raw_project_name}' -> '{project_name}' (Type: {ad_type}, Test: {test_name}, Letter: {version_letter})")
                
                return {
                    "project_name": project_name,
                    "ad_type": ad_type,
                    "test_name": test_name,
                    "version_letter": version_letter
                }
    
    # Manual extraction as fallback
    print(f"🔄 NO PATTERNS MATCHED - Attempting manual extraction...")
    
    # Try to extract components manually
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
                        project_name = clean_project_name(raw_project_name)
                        
                        # Try to extract version letter
                        version_letter = ""
                        version_letter_match = re.search(r'_(\d+)([A-Z])(?:\s|$|\))', folder_name)
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
    """Creates the ORIGINAL project folder structure with _AME, _Audio, _Copy, _Footage, _Thumbnails"""
    
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    project_path = os.path.join(desktop_path, project_folder_name)
    
    try:
        # Create main project folder
        os.makedirs(project_path, exist_ok=True)
        
        # FIXED: Create the ORIGINAL folder structure
        subfolders = {
            "audio": "_Audio", 
            "copy": "_Copy", 
            "footage": "_Footage", 
            "thumbs": "_Thumbnails", 
            "ame": "_AME"
        }
        
        # Create main subfolders
        for key, folder in subfolders.items():
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        # Audio subfolders
        audio_sub = ["Music", "SFX", "Source", "VO"]
        for sub in audio_sub:
            os.makedirs(os.path.join(project_path, subfolders["audio"], sub), exist_ok=True)
        
        # Footage subfolders  
        footage_sub = ["Images", "PSD", "Vector", "Video"]
        for sub in footage_sub:
            os.makedirs(os.path.join(project_path, subfolders["footage"], sub), exist_ok=True)
        
        # Video subfolders
        video_sub = ["Client", "Quality Score", "Rendered", "Stock"]
        for sub in video_sub:
            os.makedirs(os.path.join(project_path, subfolders["footage"], "Video", sub), exist_ok=True)
        
        print(f"📁 PROJECT STRUCTURE CREATED AT: '{project_path}'")
        
        # FIXED: Return dictionary with correct paths AND aliases for compatibility
        return {
            # Original structure
            "project_folder": project_path,
            "audio": os.path.join(project_path, "_Audio"),
            "copy": os.path.join(project_path, "_Copy"),
            "footage": os.path.join(project_path, "_Footage"),
            "thumbnails": os.path.join(project_path, "_Thumbnails"),
            "ame": os.path.join(project_path, "_AME"),
            "client_videos": os.path.join(project_path, "_Footage", "Video", "Client"),
            
            # Aliases for compatibility with existing code
            "project_root": project_path,
            "source_videos": os.path.join(project_path, "_Footage", "Video", "Client"),
            "processed_videos": os.path.join(project_path, "_AME"),
            "breakdown_files": os.path.join(project_path, "_Copy")
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