# app/src/automation/reports/report_modules/report_formatter.py
"""
Report Formatter Module
Formats report sections and content
"""

from datetime import datetime

class ReportFormatter:
    """Formats breakdown report content"""
    
    def __init__(self, duration_calculator):
        self.duration_calc = duration_calculator
        self.separator = "─" * 80
        self.header_separator = "=" * 80
    
    def format_header(self, output_folder, duration, file_count, use_transitions):
        """Format the report header"""
        lines = []
        lines.append(self.header_separator)
        lines.append("                  AI AUTOMATION SUITE - PROCESSING BREAKDOWN REPORT")
        lines.append(self.header_separator)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Processing Status: SUCCESS")
        lines.append(f"Total Duration: {duration}")
        lines.append(f"Files Processed: {file_count}")
        lines.append(f"Output Location: {output_folder}")
        
        transition_msg = ('ENABLED (0.25s fade between segments)' if use_transitions 
                         else 'DISABLED (direct cuts)')
        lines.append(f"Transitions: {transition_msg}")
        lines.append("")
        lines.append(self.header_separator)
        lines.append("                            DETAILED FILE BREAKDOWN")
        lines.append(self.header_separator)
        lines.append("")
        
        return lines
    
    def format_video_entry(self, index, analysis, timeline, component_files):
        """Format a single video entry"""
        lines = []
        
        lines.append(self.separator)
        lines.append(f"VIDEO {index}: {analysis['output_name']}.mp4")
        lines.append(f"│ Composition:     {analysis['composition']}")
        lines.append(f"│ Source File:     {analysis['source_file']}")
        
        # Show client video duration
        client_duration = analysis['durations']['client']
        lines.append(f"│ Client Duration: {self.duration_calc.format_timecode(0, client_duration)}")
        
        # Add connector info if present
        if 'connector' in component_files:
            lines.append(f"│ Connector File:  {component_files['connector']}")
            connector_duration = analysis['durations']['connector']
            lines.append(f"│ Connector Duration: {self.duration_calc.format_timecode(0, connector_duration)}")
        
        # Add endpoint info if present
        for endpoint_type, endpoint_name in [('quiz', 'Quiz'), ('svsl', 'SVSL'), ('vsl', 'VSL')]:
            if endpoint_type in component_files:
                lines.append(f"│ {endpoint_name} File:       {component_files[endpoint_type]}")
                endpoint_duration = analysis['durations'].get(endpoint_type, 0)
                lines.append(f"│ {endpoint_name} Duration:   {self.duration_calc.format_timecode(0, endpoint_duration)}")
                break
        
        # Add timeline
        lines.append(f"│")
        lines.append(f"│ ► Overall Timeline:")
        
        for entry in timeline:
            lines.append(f"│   {entry['component']} ({entry['formatted']})")
        
        # Total duration and file size
        total_duration = analysis['durations']['total']
        lines.append(f"│   Total Duration: {self.duration_calc.format_duration(total_duration)}")
        
        if analysis['size_mb'] > 0:
            lines.append(f"│   File Size: {analysis['size_mb']:.2f} MB")
        
        lines.append("")
        
        return lines
    
    def format_footer(self):
        """Format the report footer"""
        lines = []
        lines.append(self.header_separator)
        lines.append("                             END OF PROCESSING REPORT")
        lines.append(self.header_separator)
        return lines