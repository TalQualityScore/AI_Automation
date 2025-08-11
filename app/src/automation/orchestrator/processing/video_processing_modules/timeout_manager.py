# app/src/automation/orchestrator/processing/video_processing_modules/timeout_manager.py
"""
Timeout Manager Module
Manages dynamic timeouts based on processing mode
"""

class TimeoutManager:
    """Manages processing timeouts based on video type"""
    
    def get_processing_timeout(self, processing_mode):
        """
        Get appropriate timeout based on processing mode
        
        Args:
            processing_mode: Processing mode string
            
        Returns:
            Timeout in seconds
        """
        if "vsl" in processing_mode.lower():
            # VSL videos can be up to 50 minutes long
            timeout_seconds = 3600  # 60 minutes
            print(f"⏱️ Using extended timeout for VSL: {timeout_seconds} seconds (60 minutes)")
        
        elif "svsl" in processing_mode.lower():
            # SVSL videos are typically 10-30 minutes
            timeout_seconds = 1800  # 30 minutes
            print(f"⏱️ Using extended timeout for SVSL: {timeout_seconds} seconds (30 minutes)")
        
        else:
            # Quiz and connector videos are shorter
            timeout_seconds = 600  # 10 minutes
            print(f"⏱️ Using standard timeout: {timeout_seconds} seconds (10 minutes)")
        
        return timeout_seconds