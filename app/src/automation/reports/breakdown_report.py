# app/src/automation/reports/breakdown_report.py

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

def get_video_duration(video_path):
    """Get duration of a video file using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
    except:
        return 0

def format_duration(seconds):
    """Convert seconds to MM:SS format"""
    if seconds == 0:
        return "00:00"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def format_timecode(start_seconds, end_seconds):
    """Format a time range as MM:SS - MM:SS"""
    return f"{format_duration(start_seconds)} - {format_duration(end_seconds)}"

def generate_breakdown_report(processed_files, output_folder, duration, use_transitions=False):
    """Generate an enhanced breakdown report with proper formatting"""
    
    # Ensure the report is saved in the main output folder, not a subfolder
    report_path = os.path.join(output_folder, "processing_breakdown.txt")
    
    lines = []
    
    # Header with nice formatting
    lines.append("=" * 80)
    lines.append("                  AI AUTOMATION SUITE - PROCESSING BREAKDOWN REPORT")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Processing Status: SUCCESS")
    lines.append(f"Total Duration: {duration}")
    lines.append(f"Files Processed: {len(processed_files)}")
    lines.append(f"Output Location: {output_folder}")
    if use_transitions:
        lines.append(f"Transitions: ENABLED (0.25s fade between segments)")
    lines.append("")
    lines.append("=" * 80)
    lines.append("                            DETAILED FILE BREAKDOWN")
    lines.append("=" * 80)
    lines.append("")
    
    # Process each video file
    for i, file_info in enumerate(processed_files, 1):
        # Extract file information
        output_name = file_info.get('output_name', f'processed_{i}')
        source_file = file_info.get('source_file', 'Unknown')
        description = file_info.get('description', '')
        
        # Determine composition type
        if 'connector' in description.lower() and 'quiz' in description.lower():
            composition = "Client Video → Connector → Quiz"
        elif 'quiz' in description.lower():
            composition = "Client Video → Quiz"
        else:
            composition = "Direct copy (no processing)"
        
        # Get video paths and durations
        client_video_path = file_info.get('client_video_path', '')
        connector_path = file_info.get('connector_path', '')
        quiz_path = file_info.get('quiz_path', '')
        output_path = os.path.join(output_folder, f"{output_name}.mp4")
        
        # Get actual durations
        client_duration = 0
        connector_duration = 0
        quiz_duration = 0
        total_duration = 0
        
        if client_video_path and os.path.exists(client_video_path):
            client_duration = get_video_duration(client_video_path)
        
        if connector_path and os.path.exists(connector_path):
            connector_duration = get_video_duration(connector_path)
        
        if quiz_path and os.path.exists(quiz_path):
            quiz_duration = get_video_duration(quiz_path)
        
        if os.path.exists(output_path):
            total_duration = get_video_duration(output_path)
        
        # Build the report entry
        lines.append(f"VIDEO {i}: {output_name}.mp4")
        lines.append("─" * 60)
        lines.append(f"│ Composition:     {composition}")
        lines.append(f"│ Source File:     {source_file}")
        
        # Add timing information based on composition
        current_time = 0
        
        if client_duration > 0:
            end_time = current_time + client_duration
            lines.append(f"│ Client Duration: {format_timecode(current_time, end_time)}")
            current_time = end_time
            
            # Account for transition if enabled
            if use_transitions and (connector_duration > 0 or quiz_duration > 0):
                current_time -= 0.25  # Overlap for transition
        
        if connector_duration > 0:
            # Extract connector filename
            connector_name = os.path.splitext(os.path.basename(connector_path))[0] if connector_path else "Unknown Connector"
            lines.append(f"│ Connector File:  {connector_name}")
            
            start_time = current_time
            end_time = current_time + connector_duration
            lines.append(f"│ Connector Time:  {format_timecode(start_time, end_time)}")
            current_time = end_time
            
            # Account for transition if enabled
            if use_transitions and quiz_duration > 0:
                current_time -= 0.25  # Overlap for transition
        
        if quiz_duration > 0:
            # Extract quiz filename
            quiz_name = os.path.splitext(os.path.basename(quiz_path))[0] if quiz_path else "Unknown Quiz"
            lines.append(f"│ Quiz File:       {quiz_name}")
            
            start_time = current_time
            end_time = current_time + quiz_duration
            lines.append(f"│ Quiz Duration:   {format_timecode(start_time, end_time)}")
        
        # Add overall timeline
        lines.append("│")
        lines.append("│ ▶ Overall Timeline:")
        
        timeline_parts = []
        current_pos = 0
        
        if client_duration > 0:
            timeline_parts.append(f"Client ({format_duration(0)} - {format_duration(client_duration)})")
            current_pos = client_duration
            if use_transitions and (connector_duration > 0 or quiz_duration > 0):
                current_pos -= 0.25
        
        if connector_duration > 0:
            start = current_pos
            end = current_pos + connector_duration
            timeline_parts.append(f"Connector ({format_duration(start)} - {format_duration(end)})")
            current_pos = end
            if use_transitions and quiz_duration > 0:
                current_pos -= 0.25
        
        if quiz_duration > 0:
            start = current_pos
            end = current_pos + quiz_duration
            timeline_parts.append(f"Quiz ({format_duration(start)} - {format_duration(end)})")
        
        if timeline_parts:
            lines.append(f"│   {' + '.join(timeline_parts)}")
        
        if total_duration > 0:
            lines.append(f"│   Total Duration: {format_duration(total_duration)}")
        
        lines.append("")
    
    # Footer
    lines.append("=" * 80)
    lines.append("                             END OF PROCESSING REPORT")
    lines.append("=" * 80)
    
    # Write the report to file
    report_content = "\n".join(lines)
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"✅ Breakdown report generated: {report_path}")
        return report_path
    except Exception as e:
        print(f"❌ Error generating breakdown report: {e}")
        return None

def integrate_with_processing(video_processor, processed_files, output_folder, duration):
    """Integration helper to be called after video processing"""
    
    # Enhance processed_files with actual video paths
    for file_info in processed_files:
        # These paths should be set during processing
        # The video_processor should store these paths
        pass
    
    # Check if transitions were used
    use_transitions = getattr(video_processor, 'USE_TRANSITIONS', False)
    
    # Generate the report
    return generate_breakdown_report(
        processed_files,
        output_folder,
        duration,
        use_transitions
    )