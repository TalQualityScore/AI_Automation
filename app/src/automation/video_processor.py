import os
import subprocess
import sys
import json

# --- CONFIGURATION ---
# Get the absolute path to the project root directory
# From app/src/automation/video_processor.py, go up 4 levels to reach project root
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CONNECTORS_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos", "connectors")
QUIZ_OUTRO_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos", "quiz_outro")

def get_video_dimensions(video_path):
    """Gets the width and height of a video using ffprobe."""
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', video_path]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        if 'streams' in data and len(data['streams']) > 0:
            return data['streams'][0]['width'], data['streams'][0]['height'], None
        return None, None, "Video stream not found."
    except subprocess.TimeoutExpired:
        return None, None, "FFprobe timeout - video file may be corrupted"
    except Exception as e:
        return None, None, f"Error getting video dimensions: {e}"

def process_video_sequence(client_video, output_path, target_width, target_height, processing_mode="connector_quiz"):
    """Processes a single video sequence based on the processing mode."""
    print(f"Starting video processing in {processing_mode} mode...")
    
    try:
        # Build video list based on processing mode
        video_list = [client_video]
        
        if processing_mode == "connector_quiz":
            # Check if connector path exists
            if not os.path.exists(CONNECTORS_PATH):
                return f"Connector directory not found: {CONNECTORS_PATH}"
            
            connector_files = [f for f in os.listdir(CONNECTORS_PATH) if f.lower().endswith(('.mp4', '.mov'))]
            if not connector_files:
                return f"No video files found in connector directory: {CONNECTORS_PATH}"
            
            connector = os.path.join(CONNECTORS_PATH, connector_files[0])
            print(f"Found connector: {connector}")
            
            # Check if quiz outro path exists
            if not os.path.exists(QUIZ_OUTRO_PATH):
                return f"Quiz outro directory not found: {QUIZ_OUTRO_PATH}"
            
            quiz_files = [f for f in os.listdir(QUIZ_OUTRO_PATH) if f.lower().endswith(('.mp4', '.mov'))]
            if not quiz_files:
                return f"No video files found in quiz outro directory: {QUIZ_OUTRO_PATH}"
            
            outro = os.path.join(QUIZ_OUTRO_PATH, quiz_files[0])
            print(f"Found quiz outro: {outro}")
            
            video_list.extend([connector, outro])
            print(f"Will process: Client -> Connector -> Quiz")
            
        elif processing_mode == "quiz_only":
            # Check if quiz outro path exists
            if not os.path.exists(QUIZ_OUTRO_PATH):
                return f"Quiz outro directory not found: {QUIZ_OUTRO_PATH}"
            
            quiz_files = [f for f in os.listdir(QUIZ_OUTRO_PATH) if f.lower().endswith(('.mp4', '.mov'))]
            if not quiz_files:
                return f"No video files found in quiz outro directory: {QUIZ_OUTRO_PATH}"
            
            outro = os.path.join(QUIZ_OUTRO_PATH, quiz_files[0])
            print(f"Found quiz outro: {outro}")
            
            video_list.append(outro)
            print(f"Will process: Client -> Quiz")
            
        # processing_mode == "save_only" is handled in main script, not here
        
    except Exception as e:
        return f"Error setting up video files: {e}"

    # If only one video (client), just copy it
    if len(video_list) == 1:
        print("Only one video - copying directly...")
        import shutil
        shutil.copy(client_video, output_path)
        return None

    print(f"Processing {len(video_list)} videos with FFmpeg...")

    # Verify all input files exist before starting FFmpeg
    for i, video_path in enumerate(video_list):
        if not os.path.exists(video_path):
            return f"Input file not found: {video_path}"
        print(f"Video {i+1}: {os.path.basename(video_path)} ({os.path.getsize(video_path)} bytes)")

    # Process multiple videos with FFmpeg
    command = ['ffmpeg', '-y']
    filter_complex_parts, concat_inputs = [], ""
    target_fps, target_audio_rate = 30, 44100

    for j, video_path in enumerate(video_list):
        print(f"Adding video {j+1}: {os.path.basename(video_path)}")
        command.extend(['-i', video_path])
        filter_complex_parts.append(f"[{j}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={target_fps},setpts=PTS-STARTPTS[v{j}];")
        filter_complex_parts.append(f"[{j}:a]aformat=sample_rates={target_audio_rate}:channel_layouts=stereo,asetpts=PTS-STARTPTS[a{j}];")
        concat_inputs += f"[v{j}][a{j}]"
    
    filter_complex = "".join(filter_complex_parts) + f"{concat_inputs}concat=n={len(video_list)}:v=1:a=1[outv][outa]"
    command.extend(['-filter_complex', filter_complex, '-map', '[outv]', '-map', '[outa]', '-c:v', 'libx264', '-c:a', 'aac', '-preset', 'fast', output_path])
    
    print(f"FFmpeg processing started...")
    
    try:
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        # Run FFmpeg with progress monitoring
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=startupinfo
        )
        
        # Monitor progress and wait for completion
        print("FFmpeg is processing... (this may take a few minutes)")
        stdout, stderr = process.communicate(timeout=600)  # 10 minutes timeout
        
        if process.returncode != 0:
            return f"FFmpeg failed with return code {process.returncode}:\nError: {stderr}"
        
        print(f"FFmpeg processing complete for {os.path.basename(output_path)}")
        return None
            
    except subprocess.TimeoutExpired:
        process.kill()
        return f"FFmpeg processing timed out after 10 minutes"
    except Exception as e:
        return f"Unexpected error during video processing: {e}"