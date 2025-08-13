# app/src/automation/workflow_ui_components/confirmation_tab/summary_section/time_calculators.py
"""
Time Calculators - Processing Time Estimation Logic
Handles calculating estimated processing times for different modes
"""

class TimeCalculators:
    """Handles time estimation calculations"""
    
    def __init__(self, summary_section):
        self.ss = summary_section  # Reference to main SummarySection
        
        # Base time per video per mode (in minutes)
        self.time_per_video_per_mode = {
            "save_only": 0.5,
            "quiz_only": 2,
            "vsl_only": 2.5,
            "svsl_only": 2.5,
            "connector_quiz": 3,
            "connector_vsl": 3.5,
            "connector_svsl": 3.5
        }
        
        # Overhead times (in minutes)
        self.multi_mode_overhead = 1  # 1 minute overhead per additional mode
        self.setup_overhead = 0.5     # Setup overhead per mode
        self.cleanup_overhead = 0.3   # Cleanup overhead per mode
    
    def calculate_estimated_time(self, video_count, selected_modes):
        """Calculate estimated processing time for multiple modes"""
        if not selected_modes or video_count == 0:
            return "0 minutes"
        
        try:
            total_minutes = self._calculate_base_time(video_count, selected_modes)
            total_minutes += self._calculate_overhead_time(selected_modes)
            
            return self._format_time(total_minutes)
            
        except Exception as e:
            print(f"⚠️ Error calculating time: {e}")
            return "Unable to calculate"
    
    def _calculate_base_time(self, video_count, selected_modes):
        """Calculate base processing time"""
        total_minutes = 0
        
        for mode in selected_modes:
            mode_time = self.time_per_video_per_mode.get(mode, 2)  # Default 2 minutes
            total_minutes += video_count * mode_time
        
        return total_minutes
    
    def _calculate_overhead_time(self, selected_modes):
        """Calculate overhead time for multiple modes"""
        overhead = 0
        
        # Multi-mode overhead
        if len(selected_modes) > 1:
            overhead += len(selected_modes) * self.multi_mode_overhead
        
        # Setup and cleanup overhead per mode
        overhead += len(selected_modes) * (self.setup_overhead + self.cleanup_overhead)
        
        return overhead
    
    def _format_time(self, total_minutes):
        """Format time into human-readable string"""
        if total_minutes < 1:
            return "< 1 minute"
        elif total_minutes < 60:
            minutes = int(total_minutes)
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = int(total_minutes // 60)
            minutes = int(total_minutes % 60)
            if minutes == 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{hours}h {minutes}m"
    
    def get_time_breakdown(self, video_count, selected_modes):
        """Get detailed time breakdown"""
        if not selected_modes or video_count == 0:
            return {}
        
        breakdown = {
            'video_count': video_count,
            'mode_count': len(selected_modes),
            'mode_times': {},
            'total_base_time': 0,
            'total_overhead': 0,
            'total_time': 0
        }
        
        # Calculate time per mode
        for mode in selected_modes:
            mode_time = self.time_per_video_per_mode.get(mode, 2)
            total_mode_time = video_count * mode_time
            breakdown['mode_times'][mode] = {
                'per_video': mode_time,
                'total': total_mode_time
            }
            breakdown['total_base_time'] += total_mode_time
        
        # Calculate overhead
        breakdown['total_overhead'] = self._calculate_overhead_time(selected_modes)
        
        # Calculate total
        breakdown['total_time'] = breakdown['total_base_time'] + breakdown['total_overhead']
        
        return breakdown
    
    def estimate_time_per_mode(self, mode, video_count=1):
        """Estimate time for a single mode"""
        if mode not in self.time_per_video_per_mode:
            return "Unknown"
        
        time_per_video = self.time_per_video_per_mode[mode]
        total_time = video_count * time_per_video
        
        # Add setup/cleanup overhead
        total_time += self.setup_overhead + self.cleanup_overhead
        
        return self._format_time(total_time)
    
    def compare_mode_times(self, selected_modes, video_count=1):
        """Compare processing times between modes"""
        comparisons = {}
        
        for mode in selected_modes:
            comparisons[mode] = {
                'time': self.estimate_time_per_mode(mode, video_count),
                'minutes': self.time_per_video_per_mode.get(mode, 2) * video_count,
                'complexity': self._get_mode_complexity(mode)
            }
        
        return comparisons
    
    def _get_mode_complexity(self, mode):
        """Get complexity rating for mode"""
        complexity_scores = {
            "save_only": 1,
            "quiz_only": 3,
            "vsl_only": 4,
            "svsl_only": 4,
            "connector_quiz": 5,
            "connector_vsl": 6,
            "connector_svsl": 6
        }
        return complexity_scores.get(mode, 3)
    
    def get_time_efficiency_tips(self, selected_modes):
        """Get tips for improving processing efficiency"""
        tips = []
        
        if len(selected_modes) > 3:
            tips.append("Consider processing in smaller batches for better performance")
        
        if any('connector' in mode for mode in selected_modes):
            tips.append("Connector modes take longer - ensure stable internet connection")
        
        if 'save_only' in selected_modes and len(selected_modes) > 1:
            tips.append("Save-only mode is fastest - consider separating from other modes")
        
        complex_modes = [mode for mode in selected_modes if self._get_mode_complexity(mode) >= 5]
        if len(complex_modes) > 1:
            tips.append("Multiple complex modes detected - processing may take longer")
        
        return tips
    
    def predict_completion_time(self, selected_modes, video_count, start_time=None):
        """Predict completion time based on current time"""
        import datetime
        
        estimated_minutes = self._calculate_base_time(video_count, selected_modes)
        estimated_minutes += self._calculate_overhead_time(selected_modes)
        
        if start_time is None:
            start_time = datetime.datetime.now()
        
        completion_time = start_time + datetime.timedelta(minutes=estimated_minutes)
        
        return {
            'estimated_duration': self._format_time(estimated_minutes),
            'estimated_completion': completion_time.strftime("%H:%M"),
            'estimated_completion_full': completion_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_time_warning_threshold(self):
        """Get threshold for warning about long processing times"""
        return 30  # 30 minutes
    
    def should_warn_about_time(self, video_count, selected_modes):
        """Check if user should be warned about long processing time"""
        total_minutes = self._calculate_base_time(video_count, selected_modes)
        total_minutes += self._calculate_overhead_time(selected_modes)
        
        return total_minutes > self.get_time_warning_threshold()
    
    def get_time_warning_message(self, video_count, selected_modes):
        """Get warning message for long processing times"""
        if not self.should_warn_about_time(video_count, selected_modes):
            return None
        
        estimated_time = self.calculate_estimated_time(video_count, selected_modes)
        return f"⚠️ Processing may take {estimated_time}. Consider processing in smaller batches."