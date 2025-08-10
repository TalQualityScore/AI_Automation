# app/src/automation/orchestrator/processing/steps_coordinator.py
"""
Main ProcessingSteps coordinator class
Orchestrates all processing steps using specialized modules
"""

from .project_setup import ProjectSetup
from .video_processor import VideoProcessor
from .sheets_writer import SheetsWriter
from .video_sorter import VideoSorter

class ProcessingSteps:
    """Coordinates all processing steps for the orchestrator"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        
        # Initialize specialized modules
        self.project_setup = ProjectSetup(orchestrator)
        self.video_processor = VideoProcessor(orchestrator)
        self.sheets_writer = SheetsWriter(orchestrator)
        self.video_sorter = VideoSorter()
    
    def fetch_and_validate_card(self, trello_card_id):
        """Step 1: Fetch Trello card and validate basic data"""
        return self.project_setup.fetch_and_validate_card(trello_card_id)
    
    def parse_and_validate(self, card_data):
        """Step 2: Parse instructions and validate assets"""
        return self.project_setup.parse_and_validate(card_data)
    
    def download_and_setup(self, card_data, project_info):
        """Step 3: Download videos and set up project structure"""
        return self.project_setup.download_and_setup(card_data, project_info)
    
    def process_videos(self, client_videos, project_paths, project_info, processing_mode, creds):
        """Step 4: Process all videos based on mode"""
        # Sort videos first
        sorted_videos = self.video_sorter.sort_videos_by_version_letter(client_videos)
        
        # Process them
        return self.video_processor.process_all_videos(
            sorted_videos, project_paths, project_info, processing_mode, creds
        )
    
    def process_single_video(self, client_video, project_paths, project_info, processing_mode, 
                           version_num, target_width, target_height):
        """Process a single video file"""
        return self.video_processor.process_single_video(
            client_video, project_paths, project_info, processing_mode,
            version_num, target_width, target_height
        )
    
    def write_to_sheets(self, project_info, processed_files, creds):
        """Step 5: Write results to Google Sheets"""
        return self.sheets_writer.write_to_sheets(project_info, processed_files, creds)
    
    # Utility methods for backward compatibility
    def extract_version_letter(self, filename):
        """Extract version letter from filename"""
        return self.video_sorter.extract_version_letter(filename)
    
    def sort_videos_by_version_letter(self, videos):
        """Sort videos by version letter"""
        return self.video_sorter.sort_videos_by_version_letter(videos)
    
    def finalize_and_cleanup(self, processed_files, project_info, creds, project_paths):
        """
        Step 6: Organize files and cleanup - ENHANCED with better debugging and path resolution
        """
        print("\n--- Step 6: Organizing Files & Cleanup ---")
        
        try:
            # Import the cleanup utilities
            import os
            import shutil
            from ...api_clients.config import DOWNLOADS_DIR
            
            # ENHANCED: Better path debugging and resolution
            print(f"🔍 DEBUG - Checking project paths...")
            
            if not project_paths:
                print(f"❌ ERROR: project_paths not available")
                if hasattr(self.orchestrator, 'project_paths'):
                    project_paths = self.orchestrator.project_paths
                    print(f"✅ Retrieved project_paths from orchestrator")
                else:
                    print(f"❌ No project_paths found in orchestrator either")
                    return
            
            print(f"✅ Found project_paths: {list(project_paths.keys())}")
            
            # Multiple path checking strategies
            client_videos_path = None
            
            # Strategy 1: Direct client_videos key
            if 'client_videos' in project_paths:
                client_videos_path = project_paths['client_videos']
                print(f"📁 Found client_videos path: {client_videos_path}")
            
            # Strategy 2: Look for _Footage/Video/Client pattern
            elif 'base_output' in project_paths:
                base_path = project_paths['base_output']
                potential_client_path = os.path.join(base_path, '_Footage', 'Video', 'Client')
                if os.path.exists(potential_client_path):
                    client_videos_path = potential_client_path
                    print(f"📁 Found client path via base_output: {client_videos_path}")
                else:
                    # Try to create it
                    try:
                        os.makedirs(potential_client_path, exist_ok=True)
                        client_videos_path = potential_client_path
                        print(f"📁 Created client path via base_output: {client_videos_path}")
                    except Exception as create_error:
                        print(f"❌ Could not create client path: {create_error}")
            
            # Strategy 3: Search for any path containing "Client"
            else:
                for key, path in project_paths.items():
                    if 'Client' in path or 'client' in path:
                        client_videos_path = path
                        print(f"📁 Found client path via search ({key}): {client_videos_path}")
                        break
            
            if not client_videos_path:
                print("❌ ERROR: Could not determine client videos path")
                print(f"   Available paths: {project_paths}")
                return
            
            # ENHANCED: Better downloads directory checking
            downloads_path = DOWNLOADS_DIR
            print(f"🔍 Checking downloads directory: {downloads_path}")
            
            # Check absolute vs relative path
            if not os.path.isabs(downloads_path):
                abs_downloads_path = os.path.abspath(downloads_path)
                print(f"   Absolute path: {abs_downloads_path}")
            else:
                abs_downloads_path = downloads_path
            
            if not os.path.exists(abs_downloads_path):
                print(f"⚠️ Downloads directory not found at: {abs_downloads_path}")
                # Try alternative locations
                alt_paths = ["temp_downloads", "./temp_downloads", "../temp_downloads"]
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        abs_downloads_path = os.path.abspath(alt_path)
                        print(f"✅ Found downloads at alternative location: {abs_downloads_path}")
                        break
                else:
                    print("❌ No temp downloads found anywhere, skipping cleanup")
                    return
            
            # ENHANCED: Create client directory if it doesn't exist
            os.makedirs(client_videos_path, exist_ok=True)
            print(f"✅ Client videos directory ready: {client_videos_path}")
            
            # ENHANCED: Better file discovery and moving
            print(f"🔍 Scanning for video files in: {abs_downloads_path}")
            video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.wmv', '.flv', '.m4v')
            
            all_files = []
            try:
                all_files = os.listdir(abs_downloads_path)
                print(f"   Found {len(all_files)} total files")
            except Exception as list_error:
                print(f"❌ Error listing downloads directory: {list_error}")
                return
            
            video_files = [f for f in all_files if f.lower().endswith(video_extensions)]
            print(f"   Found {len(video_files)} video files: {video_files}")
            
            if not video_files:
                print("⚠️ No video files found to move")
                # Still clean up the directory if it's empty
                try:
                    if len(all_files) == 0:
                        shutil.rmtree(abs_downloads_path)
                        print(f"🧹 Cleaned up empty downloads directory")
                except Exception as cleanup_error:
                    print(f"⚠️ Could not clean up empty directory: {cleanup_error}")
                return
            
            # Move video files with enhanced error handling
            moved_count = 0
            failed_moves = []
            
            for filename in video_files:
                source_path = os.path.join(abs_downloads_path, filename)
                dest_path = os.path.join(client_videos_path, filename)
                
                try:
                    # Check if source file actually exists and is accessible
                    if not os.path.exists(source_path):
                        print(f"⚠️ Source file not found: {source_path}")
                        continue
                    
                    # Check if destination already exists
                    if os.path.exists(dest_path):
                        # Create unique name
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(dest_path):
                            dest_path = os.path.join(client_videos_path, f"{base}_{counter}{ext}")
                            counter += 1
                        print(f"   Destination exists, using: {os.path.basename(dest_path)}")
                    
                    # Perform the move
                    shutil.move(source_path, dest_path)
                    print(f"📁 ✅ Moved: {filename} → _Footage/Video/Client/")
                    moved_count += 1
                    
                except Exception as move_error:
                    print(f"❌ Failed to move {filename}: {move_error}")
                    failed_moves.append((filename, str(move_error)))
            
            # ENHANCED: Final cleanup with better error reporting
            try:
                remaining_files = os.listdir(abs_downloads_path)
                if not remaining_files:
                    shutil.rmtree(abs_downloads_path)
                    print(f"🧹 ✅ Cleaned up downloads directory")
                else:
                    print(f"⚠️ Downloads directory not empty, contains: {remaining_files}")
            except Exception as cleanup_error:
                print(f"⚠️ Could not clean up downloads directory: {cleanup_error}")
            
            # ENHANCED: Summary report
            print(f"📊 FILE ORGANIZATION SUMMARY:")
            print(f"   ✅ Successfully moved: {moved_count} videos")
            if failed_moves:
                print(f"   ❌ Failed moves: {len(failed_moves)}")
                for filename, error in failed_moves:
                    print(f"      - {filename}: {error}")
            print(f"   📁 Destination: {client_videos_path}")
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR during file organization: {e}")
            import traceback
            print(f"   Full traceback: {traceback.format_exc()}")
            # Don't fail the entire automation for cleanup issues