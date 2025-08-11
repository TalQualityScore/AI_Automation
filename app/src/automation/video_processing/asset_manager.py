# app/src/automation/video_processing/asset_manager.py
"""
Asset Manager Module
Manages video assets (connectors, quiz, SVSL, VSL)
"""

import os
from typing import Optional
from .processor_config import ProcessorConfig

class AssetManager:
    """Manages access to video assets"""
    
    def __init__(self, account_code: str = None, platform_code: str = None):
        self.config = ProcessorConfig()
        self.account_code = account_code
        self.platform_code = platform_code
    
    def set_account_platform(self, account_code: str, platform_code: str):
        """Update account and platform codes"""
        self.account_code = account_code
        self.platform_code = platform_code
        print(f"📁 Asset Manager Updated: Account={account_code}, Platform={platform_code}")
    
    def get_asset_path(self, asset_type: str) -> Optional[str]:
        """Get the path to a specific asset type"""
        if not self.account_code or not self.platform_code:
            # Fallback to old structure
            print(f"⚠️ No account/platform set, using legacy paths")
            return self._get_legacy_path(asset_type)
        
        # Build path based on new structure
        asset_path = os.path.join(
            self.config.ASSETS_BASE_PATH, 
            self.account_code, 
            self.platform_code, 
            asset_type
        )
        
        # Check if path exists
        if not os.path.exists(asset_path) and asset_type in ["SVSL", "VSL"]:
            # Try direct account level for SVSL/VSL
            asset_path = os.path.join(
                self.config.ASSETS_BASE_PATH, 
                self.account_code, 
                asset_type
            )
        
        return asset_path if os.path.exists(asset_path) else None
    
    def _get_legacy_path(self, asset_type: str) -> Optional[str]:
        """Get legacy asset path for backward compatibility"""
        legacy_paths = {
            "Connectors": os.path.join(self.config.SCRIPT_DIR, "Assets", "Videos", "connectors"),
            "Quiz": os.path.join(self.config.SCRIPT_DIR, "Assets", "Videos", "quiz_outro"),
        }
        return legacy_paths.get(asset_type)
    
    def _get_first_video_in_directory(self, directory: str) -> Optional[str]:
        """Get the first video file in a directory"""
        if not directory or not os.path.exists(directory):
            return None
        
        files = [
            f for f in os.listdir(directory)
            if f.lower().endswith(tuple(self.config.SUPPORTED_VIDEO_FORMATS))
        ]
        
        if files:
            return os.path.join(directory, files[0])
        return None
    
    def get_connector_video(self) -> Optional[str]:
        """Get the first available connector video"""
        connector_path = self.get_asset_path("Connectors")
        
        if not connector_path:
            print(f"⚠️ Connector directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        video = self._get_first_video_in_directory(connector_path)
        if not video:
            print(f"⚠️ No connector videos found in {connector_path}")
        
        return video
    
    def get_quiz_video(self) -> Optional[str]:
        """Get the first available quiz outro video"""
        quiz_path = self.get_asset_path("Quiz")
        
        if not quiz_path:
            print(f"⚠️ Quiz outro directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        video = self._get_first_video_in_directory(quiz_path)
        if not video:
            print(f"⚠️ No quiz outro videos found in {quiz_path}")
        
        return video
    
    def get_svsl_video(self) -> Optional[str]:
        """Get the first available SVSL video"""
        svsl_path = self.get_asset_path("SVSL")
        
        if not svsl_path:
            print(f"⚠️ SVSL directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        video = self._get_first_video_in_directory(svsl_path)
        if not video:
            print(f"⚠️ No SVSL videos found in {svsl_path}")
        
        return video
    
    def get_vsl_video(self) -> Optional[str]:
        """Get the first available VSL video"""
        vsl_path = self.get_asset_path("VSL")
        
        if not vsl_path:
            print(f"⚠️ VSL directory not found for {self.account_code}/{self.platform_code}")
            return None
        
        video = self._get_first_video_in_directory(vsl_path)
        if not video:
            print(f"⚠️ No VSL videos found in {vsl_path}")
        
        return video