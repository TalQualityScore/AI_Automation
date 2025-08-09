# app/src/automation/reports/breakdown_report.py
# COMPLETE FILE - Shows all video components with accurate durations

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

def get_video_duration(video_path):
    """Get actual duration of a video file using ffprobe"""
    try:
        # Use ffprobe to get the actual duration
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json', video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if 'format' in data and 'duration' in data['format']:
                duration = float(data['format']['duration'])
                print(f"📹 Got duration for {os.path.basename(video_path)}: {duration:.2f} seconds")
                return duration
        
        # Fallback: try stream duration
        cmd_stream = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=duration',
            '-of', 'json', video_path
        ]
        
        result_stream = subprocess.run(cmd_stream, capture_output=True, text=True, timeout=10)
        
        if result_stream.returncode == 0:
            data_stream = json.loads(result_stream.stdout)
            if 'streams' in data_stream and len(data_stream['streams']) > 0:
                if 'duration' in data_stream['streams'][0]:
                    duration = float(data_stream['streams'][0]['duration'])
                    print(f"📹 Got stream duration for {os.path.basename(video_path)}: {duration:.2f} seconds")
                    return duration
        
        print(f"⚠️ Could not get duration for {os.path.basename(video_path)}")
        return 0
        
    except subprocess.TimeoutExpired:
        print(f"⚠️ Timeout getting duration for {os.path.basename(video_path)}")
        return 0
    except Exception as e:
        print(f"⚠️ Error getting duration for {os.path.basename(video_path)}: {e}")
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
    """Generate an enhanced breakdown report with all component durations"""
    
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
    lines.append(f"Transitions: {'ENABLED (0.25s fade between segments)' if use_transitions else 'DISABLED (direct cuts)'}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("                            DETAILED FILE BREAKDOWN")
    lines.append("=" * 80)
    lines.append("")
    
    # Cache for video durations to avoid repeated ffprobe calls
    duration_cache = {}
    
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
        
        # Get video paths from file_info
        client_video_path = file_info.get('client_video_path', '')
        connector_path = file_info.get('connector_path', '')
        quiz_path = file_info.get('quiz_path', '')
        
        # Check for output file in _AME folder
        output_path = os.path.join(output_folder, "_AME", f"{output_name}.mp4")
        if not os.path.exists(output_path):
            # Try without _AME folder
            output_path = os.path.join(output_folder, f"{output_name}.mp4")
        
        # Get actual durations using ffprobe with caching
        client_duration = 0
        connector_duration = 0
        quiz_duration = 0
        total_duration = 0
        
        # Get client video duration
        if client_video_path and os.path.exists(client_video_path):
            if client_video_path not in duration_cache:
                duration_cache[client_video_path] = get_video_duration(client_video_path)
            client_duration = duration_cache[client_video_path]
        
        # Get connector duration if used
        if connector_path and os.path.exists(connector_path):
            if connector_path not in duration_cache:
                duration_cache[connector_path] = get_video_duration(connector_path)
            connector_duration = duration_cache[connector_path]
        
        # Get quiz duration if used
        if quiz_path and os.path.exists(quiz_path):
            if quiz_path not in duration_cache:
                duration_cache[quiz_path] = get_video_duration(quiz_path)
            quiz_duration = duration_cache[quiz_path]
        
        # Get total output duration - most accurate
        if os.path.exists(output_path):
            if output_path not in duration_cache:
                duration_cache[output_path] = get_video_duration(output_path)
            total_duration = duration_cache[output_path]
        else:
            # Calculate total if output doesn't exist yet
            total_duration = client_duration + connector_duration + quiz_duration
            if use_transitions:
                # Add transition time between segments
                num_transitions = 1 if quiz_duration > 0 else 0
                if connector_duration > 0:
                    num_transitions += 1
                total_duration += num_transitions * 0.25  # 0.25s per transition
        
        # Build the separator line
        separator = "─" * 80
        
        # Format the report entry with complete information
        lines.append(separator)
        lines.append(f"VIDEO {i}: {output_name}.mp4")
        lines.append(f"│ Composition:     {composition}")
        lines.append(f"│ Source File:     {source_file}")
        
        # Show client video duration
        lines.append(f"│ Client Duration: {format_timecode(0, client_duration)}")
        
        # Add connector info if used
        if 'connector' in composition.lower() and connector_path:
            connector_name = os.path.basename(connector_path)
            lines.append(f"│ Connector File:  {connector_name}")
            lines.append(f"│ Connector Duration: {format_timecode(0, connector_duration)}")
        
        # Add quiz info if used
        if 'quiz' in composition.lower() and quiz_path:
            quiz_name = os.path.basename(quiz_path)
            lines.append(f"│ Quiz File:       {quiz_name}")
            lines.append(f"│ Quiz Duration:   {format_timecode(0, quiz_duration)}")
        
        lines.append(f"│")
        lines.append(f"│ ► Overall Timeline:")
        
        # Build the timeline showing when each component appears
        current_time = 0
        
        # Client video timeline
        if client_duration > 0:
            client_end = current_time + client_duration
            lines.append(f"│   Client ({format_timecode(current_time, client_end)})")
            current_time = client_end
        
        # Connector timeline (if present)
        if 'connector' in composition.lower() and connector_duration > 0:
            if use_transitions:
                current_time += 0.25  # Add transition time
            connector_end = current_time + connector_duration
            lines.append(f"│   Connector ({format_timecode(current_time, connector_end)})")
            current_time = connector_end
        
        # Quiz timeline (if present)
        if 'quiz' in composition.lower() and quiz_duration > 0:
            if use_transitions:
                current_time += 0.25  # Add transition time
            quiz_end = current_time + quiz_duration
            lines.append(f"│   Quiz Outro ({format_timecode(current_time, quiz_end)})")
            current_time = quiz_end
        
        # Total duration and file size
        lines.append(f"│   Total Duration: {format_duration(total_duration)}")
        
        # Add file size if available
        if os.path.exists(output_path):
            try:
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                lines.append(f"│   File Size: {size_mb:.2f} MB")
            except:
                pass
        
        lines.append("")
    
    # Footer
    lines.append("=" * 80)
    lines.append("                             END OF PROCESSING REPORT")
    lines.append("=" * 80)
    
    # Write the report to file
    report_content = "\n".join(lines)
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"✅ Breakdown report generated: {report_path}")
        
        return report_path
    except Exception as e:
        print(f"❌ Error generating breakdown report: {e}")
        return None

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