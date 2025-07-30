# Add this to app/src/automation/timing_report.py

import os
import subprocess
import json
from datetime import timedelta

def get_video_duration(video_path):
    """Get video duration in seconds using ffprobe."""
    command = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', 
        '-show_entries', 'format=duration', '-of', 'json', video_path
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
    except Exception as e:
        print(f"Error getting duration for {video_path}: {e}")
        return 0

def format_timestamp(seconds):
    """Format seconds to MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def generate_timing_report(video_sequence, output_folder, processing_mode):
    """Generate timing report for the video sequence."""
    timing_file_path = os.path.join(output_folder, "Timing.txt")
    
    try:
        current_time = 0
        timing_lines = []
        timing_lines.append("=== VIDEO TIMING REPORT ===\n")
        timing_lines.append(f"Processing Mode: {processing_mode}\n")
        timing_lines.append(f"Total Videos: {len(video_sequence)}\n\n")
        
        for i, video_info in enumerate(video_sequence):
            video_path = video_info['path']
            video_name = video_info['name']
            video_type = video_info['type']  # 'client', 'connector', 'quiz'
            
            # Get duration
            duration = get_video_duration(video_path)
            
            # Calculate timing
            start_time = current_time
            end_time = current_time + duration
            
            # Format the line
            timing_line = f"{video_type.title()} Video: {video_name}\n"
            timing_line += f"  Duration: {format_timestamp(duration)} ({duration:.2f} seconds)\n"
            timing_line += f"  Timing: {format_timestamp(start_time)} - {format_timestamp(end_time)}\n\n"
            
            timing_lines.append(timing_line)
            
            # Update current time
            current_time = end_time
        
        # Add total duration
        timing_lines.append(f"=== TOTAL DURATION: {format_timestamp(current_time)} ({current_time:.2f} seconds) ===\n")
        
        # Write to file
        with open(timing_file_path, 'w', encoding='utf-8') as f:
            f.writelines(timing_lines)
        
        print(f"Timing report generated: {timing_file_path}")
        return timing_file_path
        
    except Exception as e:
        print(f"Error generating timing report: {e}")
        return None

def prepare_video_sequence_info(client_video, processing_mode):
    """Prepare video sequence information for timing report."""
    sequence = []
    
    # Add client video
    sequence.append({
        'path': client_video,
        'name': os.path.basename(client_video),
        'type': 'client'
    })
    
    # Add connector if needed
    if processing_mode == "connector_quiz":
        try:
            connectors_path = "Assets/Videos/connectors/"
            connector_file = os.listdir(connectors_path)[0]
            connector_path = os.path.join(connectors_path, connector_file)
            sequence.append({
                'path': connector_path,
                'name': connector_file,
                'type': 'connector'
            })
        except Exception as e:
            print(f"Warning: Could not find connector video: {e}")
    
    # Add quiz outro if needed
    if processing_mode in ["quiz_only", "connector_quiz"]:
        try:
            quiz_path = "Assets/Videos/quiz_outro/"
            quiz_file = os.listdir(quiz_path)[0]
            quiz_full_path = os.path.join(quiz_path, quiz_file)
            sequence.append({
                'path': quiz_full_path,
                'name': quiz_file,
                'type': 'quiz'
            })
        except Exception as e:
            print(f"Warning: Could not find quiz outro video: {e}")
    
    return sequence