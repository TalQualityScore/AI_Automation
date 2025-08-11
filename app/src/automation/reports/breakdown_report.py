# app/src/automation/reports/breakdown_report.py - REFACTORED
"""
Breakdown Report Generator - REFACTORED
Now uses modular components for better organization
"""

from .report_modules import (
    DurationCalculator,
    ReportFormatter,
    TimelineBuilder,
    FileAnalyzer,
    ReportWriter
)

def generate_breakdown_report(processed_files, output_folder, duration, use_transitions=False):
    """
    Generate an enhanced breakdown report - REFACTORED
    Now ~40 lines instead of 178 lines
    
    Args:
        processed_files: List of processed file information
        output_folder: Output folder path
        duration: Total processing duration
        use_transitions: Whether transitions were used
        
    Returns:
        Path to generated report or None on error
    """
    
    # Initialize modules
    duration_calc = DurationCalculator()
    formatter = ReportFormatter(duration_calc)
    timeline_builder = TimelineBuilder(duration_calc)
    file_analyzer = FileAnalyzer(duration_calc)
    writer = ReportWriter()
    
    # Start building report
    lines = []
    
    # Add header
    lines.extend(formatter.format_header(
        output_folder, duration, len(processed_files), use_transitions
    ))
    
    # Process each video file
    for i, file_info in enumerate(processed_files, 1):
        # Analyze the file
        analysis = file_analyzer.analyze_file(file_info, output_folder)
        
        # Build timeline
        timeline = timeline_builder.build_timeline(analysis, use_transitions)
        
        # Get component files
        component_files = timeline_builder.get_component_files(analysis)
        
        # Format the entry
        lines.extend(formatter.format_video_entry(
            i, analysis, timeline, component_files
        ))
    
    # Add footer
    lines.extend(formatter.format_footer())
    
    # Write the report
    return writer.write_report(lines, output_folder)


def format_duration(seconds):
    """Helper function for backward compatibility"""
    calc = DurationCalculator()
    return calc.format_duration(seconds)


def format_timecode(start_seconds, end_seconds):
    """Helper function for backward compatibility"""
    calc = DurationCalculator()
    return calc.format_timecode(start_seconds, end_seconds)


def integrate_with_processing(video_processor, processed_files, output_folder, duration):

    
    """Integration helper to be called after video processing"""
    
    # Check if transitions were used
    use_transitions = getattr(video_processor, 'use_transitions', False)
    
    # Generate the report
    return generate_breakdown_report(
        processed_files,
        output_folder,
        duration,
        use_transitions
    )

def get_video_duration(video_path):
    """Compatibility function - delegates to DurationCalculator"""
    calc = DurationCalculator()
    return calc.get_video_duration(video_path)