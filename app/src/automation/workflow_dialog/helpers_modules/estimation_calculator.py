# app/src/automation/workflow_dialog/helpers_modules/estimation_calculator.py
"""
Estimation Calculator Module
Calculates time and size estimates for processing
"""

class EstimationCalculator:
    """Calculates processing time and size estimates"""
    
    def calculate_time_estimate(self, file_count, processing_mode):
        """
        Calculate estimated processing time
        
        Args:
            file_count: Number of files to process
            processing_mode: Processing mode string
            
        Returns:
            String with formatted time estimate
        """
        
        if processing_mode == "save_only":
            return "Instant - Direct copying"
        
        # Different modes have different processing times
        if "vsl" in processing_mode.lower():
            # VSL videos take longer
            seconds_per_video = 30
        elif "svsl" in processing_mode.lower():
            # SVSL videos are medium
            seconds_per_video = 20
        else:
            # Quiz/connector are faster
            seconds_per_video = 10
        
        min_time = file_count * seconds_per_video
        max_time = file_count * seconds_per_video * 1.5
        
        return self._format_time_range(min_time, max_time)
    
    def calculate_size_estimate(self, file_sizes, processing_mode):
        """
        Calculate estimated output size
        
        Args:
            file_sizes: List of (filename, size_mb) tuples
            processing_mode: Processing mode string
            
        Returns:
            Float with estimated total size in MB
        """
        
        total_size = sum(size for _, size in file_sizes)
        
        if processing_mode == "save_only":
            return total_size
        
        # Add overhead for processing
        if "connector" in processing_mode:
            total_size *= 1.1  # 10% overhead
        
        if any(x in processing_mode for x in ["quiz", "svsl", "vsl"]):
            total_size *= 1.2  # 20% overhead for endpoints
        
        return round(total_size, 2)
    
    def _format_time_range(self, min_seconds, max_seconds):
        """Format a time range in human-readable format"""
        
        def format_time(seconds):
            if seconds < 60:
                return f"{int(seconds)} seconds"
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            if secs > 0:
                return f"{minutes}m {secs}s"
            return f"{minutes} minutes"
        
        min_str = format_time(min_seconds)
        max_str = format_time(max_seconds)
        
        if min_str == max_str:
            return min_str
        
        return f"{min_str} - {max_str} (includes transitions)"