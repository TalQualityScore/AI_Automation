import os
import subprocess
import sys
import json
import signal

# --- CONFIGURATION ---
CONNECTORS_PATH = "Assets/Videos/connectors/"
QUIZ_OUTRO_PATH = "Assets/Videos/quiz_outro/"

# --- FUNCTIONS ---

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
            # Add connector first, then quiz
            if not os.path.exists(CONNECTORS_PATH) or not os.listdir(CONNECTORS_PATH):
                return f"Connector path not found or empty: {CONNECTORS_PATH}"
            connector = os.path.join(CONNECTORS_PATH, os.listdir(CONNECTORS_PATH)[0])
            
            if not os.path.exists(QUIZ_OUTRO_PATH) or not os.listdir(QUIZ_OUTRO_PATH):
                return f"Quiz outro path not found or empty: {QUIZ_OUTRO_PATH}"
            outro = os.path.join(QUIZ_OUTRO_PATH, os.listdir(QUIZ_OUTRO_PATH)[0])
            
            video_list.extend([connector, outro])
            print(f"Will process: Client -> Connector -> Quiz")
            
        elif processing_mode == "quiz_only":
            # Add only quiz outro
            if not os.path.exists(QUIZ_OUTRO_PATH) or not os.listdir(QUIZ_OUTRO_PATH):
                return f"Quiz outro path not found or empty: {QUIZ_OUTRO_PATH}"
            outro = os.path.join(QUIZ_OUTRO_PATH, os.listdir(QUIZ_OUTRO_PATH)[0])
            
            video_list.append(outro)
            print(f"Will process: Client -> Quiz")
            
        # processing_mode == "save_only" is handled in main script, not here
        
    except (FileNotFoundError, IndexError) as e:
        return f"Could not find required video files: {e}"

    # If only one video (client), just copy it
    if len(video_list) == 1:
        print("Only one video - copying directly...")
        import shutil
        shutil.copy(client_video, output_path)
        return None

    print(f"Processing {len(video_list)} videos with FFmpeg...")

    # Process multiple videos with FFmpeg
    command = ['ffmpeg', '-y']
    filter_complex_parts, concat_inputs = [], ""
    target_fps, target_audio_rate = 30, 44100

    for j, video_path in enumerate(video_list):
        if not os.path.exists(video_path): 
            return f"Input file not found: {video_path}"
        
        print(f"Adding video {j+1}: {os.path.basename(video_path)}")
        command.extend(['-i', video_path])
        filter_complex_parts.append(f"[{j}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={target_fps},setpts=PTS-STARTPTS[v{j}];")
        filter_complex_parts.append(f"[{j}:a]aformat=sample_rates={target_audio_rate}:channel_layouts=stereo,asetpts=PTS-STARTPTS[a{j}];")
        concat_inputs += f"[v{j}][a{j}]"
    
    filter_complex = "".join(filter_complex_parts) + f"{concat_inputs}concat=n={len(video_list)}:v=1:a=1[outv][outa]"
    command.extend(['-filter_complex', filter_complex, '-map', '[outv]', '-map', '[outa]', '-c:v', 'libx264', '-c:a', 'aac', '-preset', 'fast', output_path])
    
    print(f"FFmpeg command ready. Starting processing...")
    
    try:
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        # Add timeout to prevent hanging
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True, 
            startupinfo=startupinfo,
            timeout=300  # 5 minutes timeout
        )
        
        print(f"FFmpeg processing complete for {os.path.basename(output_path)}")
        return None
        
    except subprocess.TimeoutExpired:
        return f"FFmpeg processing timed out after 5 minutes - videos may be too large or corrupted"
    except subprocess.CalledProcessError as e:
        error_msg = f"FFmpeg error:\nCommand: {' '.join(command)}\nStderr: {e.stderr}\nStdout: {e.stdout}"
        print(f"FFmpeg failed: {error_msg}")
        return error_msg
    except Exception as e:
        return f"Unexpected error during video processing: {e}"