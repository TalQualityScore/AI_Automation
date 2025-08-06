# app/src/automation/api_clients/google_drive_client.py
"""
Google Drive API Client
Handles file downloads from Google Drive folders
"""

import os
from typing import List, Optional, Tuple
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from .config import DOWNLOADS_DIR, DOWNLOAD_TIMEOUT

class GoogleDriveClient:
    """Handles Google Drive API operations"""
    
    def __init__(self, credentials):
        """
        Initialize Google Drive client
        
        Args:
            credentials: Google API credentials object
        """
        self.credentials = credentials
        self.service = None
        if credentials:
            try:
                self.service = build("drive", "v3", credentials=credentials)
            except Exception as e:
                print(f"❌ Failed to initialize Google Drive service: {e}")
    
    def download_files_from_folder(self, folder_url: str, monitor=None) -> Tuple[Optional[List[str]], Optional[str]]:
        """
        Download all video files from a Google Drive folder
        
        Args:
            folder_url: Google Drive folder URL
            monitor: Optional activity monitor for progress updates
            
        Returns:
            Tuple of (downloaded_file_paths, error_message)
        """
        
        if not self.service:
            return None, "Google Drive service not initialized"
        
        try:
            if monitor:
                monitor.update_activity("Connecting to Google Drive...")
            
            # Extract folder ID from URL
            folder_id = self._extract_folder_id(folder_url)
            if not folder_id:
                return None, "Could not extract folder ID from Google Drive URL"
            
            # Create downloads directory
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            
            if monitor:
                monitor.update_activity("Searching for video files...")
            
            # Get list of video files in folder
            video_files = self._get_video_files(folder_id)
            
            if not video_files:
                return None, "No video files found in the Google Drive folder"
            
            if monitor:
                monitor.update_activity(f"Found {len(video_files)} video files to download")
            
            # Download each file
            downloaded_files = []
            for i, file_info in enumerate(video_files):
                file_id = file_info['id']
                file_name = file_info['name']
                file_size = int(file_info.get('size', 0))
                
                local_path = os.path.join(DOWNLOADS_DIR, file_name)
                
                if monitor:
                    monitor.update_activity(f"Starting download: {file_name}")
                
                success = self._download_single_file(file_id, file_name, local_path, monitor)
                
                if success:
                    downloaded_files.append(local_path)
                    if monitor:
                        monitor.update_activity(f"Completed: {file_name} ({i+1}/{len(video_files)})")
                else:
                    return None, f"Failed to download file: {file_name}"
            
            if monitor:
                monitor.update_activity(f"All downloads completed: {len(downloaded_files)} files")
            
            return downloaded_files, None
            
        except HttpError as e:
            error_msg = f"Google Drive API error: {e}"
            print(f"❌ {error_msg}")
            return None, error_msg
        except Exception as e:
            error_msg = f"Unexpected download error: {e}"
            print(f"❌ {error_msg}")
            return None, error_msg
    
    def _extract_folder_id(self, folder_url: str) -> Optional[str]:
        """Extract folder ID from Google Drive URL"""
        try:
            # URL format: https://drive.google.com/drive/folders/FOLDER_ID
            folder_id = folder_url.split('/')[-1]
            if folder_id and len(folder_id) > 10:  # Basic validation
                return folder_id
        except Exception:
            pass
        return None
    
    def _get_video_files(self, folder_id: str) -> List[dict]:
        """Get list of video files in the folder"""
        try:
            query = f"'{folder_id}' in parents and mimeType contains 'video/'"
            results = self.service.files().list(
                q=query, 
                fields="files(id, name, size)"
            ).execute()
            
            files = results.get("files", [])
            print(f"📁 Found {len(files)} video files in folder")
            
            return files
            
        except Exception as e:
            print(f"❌ Error getting file list: {e}")
            return []
    
    def _download_single_file(self, file_id: str, file_name: str, local_path: str, monitor=None) -> bool:
        """
        Download a single file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            file_name: Name of the file
            local_path: Local path to save the file
            monitor: Optional activity monitor
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            print(f"📥 Downloading {file_name}...")
            
            request = self.service.files().get_media(fileId=file_id)
            
            with open(local_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                last_progress = 0
                
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        
                        # Update progress every 5% or when done
                        if progress - last_progress >= 5 or done:
                            if monitor:
                                monitor.update_activity(f"Downloading {file_name}: {progress}%")
                            print(f"Download {progress}%")
                            last_progress = progress
            
            print(f"✅ Downloaded: {file_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {file_name}: {e}")
            return False
    
    def cleanup_downloads(self):
        """Clean up downloaded files"""
        try:
            if os.path.exists(DOWNLOADS_DIR):
                import shutil
                shutil.rmtree(DOWNLOADS_DIR)
                print(f"🧹 Cleaned up downloads directory: {DOWNLOADS_DIR}")
        except Exception as e:
            print(f"⚠️ Could not clean up downloads: {e}")