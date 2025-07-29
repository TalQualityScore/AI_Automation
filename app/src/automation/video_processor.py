import os
import subprocess
import sys
import json

# --- CONFIGURATION ---
CONNECTORS_PATH = "Assets/Videos/connectors/"
QUIZ_OUTRO_PATH = "Assets/Videos/quiz_outro/"

# --- FUNCTIONS ---

def get_video_dimensions(video_path):
    """Gets the width and height of a video using ffprobe."""
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', video_path]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        if 'streams' in data and len(data['streams']) > 0:
            return data['streams'][0]['width'], data['streams'][0]['height'], None
        return None, None, "Video stream not found."
    except Exception as e:
        return None, None, f"Error getting video dimensions: {e}"

def process_video_sequence(client_video, output_path, target_width, target_height):
    """Processes a single video sequence using a dynamic resolution."""
    try:
        connector = os.path.join(CONNECTORS_PATH, os.listdir(CONNECTORS_PATH)[0])
        outro = os.path.join(QUIZ_OUTRO_PATH, os.listdir(QUIZ_OUTRO_PATH)[0])
    except (FileNotFoundError, IndexError) as e:
        return f"Could not find connector or quiz outro files: {e}"

    video_list = [client_video, connector, outro]
    command = ['ffmpeg', '-y']
    filter_complex_parts, concat_inputs = [], ""
    target_fps, target_audio_rate = 30, 44100

    for j, video_path in enumerate(video_list):
        if not os.path.exists(video_path): return f"Input file not found: {video_path}"
        command.extend(['-i', video_path])
        filter_complex_parts.append(f"[{j}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={target_fps},setpts=PTS-STARTPTS[v{j}];")
        filter_complex_parts.append(f"[{j}:a]aformat=sample_rates={target_audio_rate}:channel_layouts=stereo,asetpts=PTS-STARTPTS[a{j}];")
        concat_inputs += f"[v{j}][a{j}]"
    
    filter_complex = "".join(filter_complex_parts) + f"{concat_inputs}concat=n={len(video_list)}:v=1:a=1[outv][outa]"
    command.extend(['-filter_complex', filter_complex, '-map', '[outv]', '-map', '[outa]', '-c:v', 'libx264', '-c:a', 'aac', '-preset', 'fast', output_path])
    
    try:
        print(f"Running FFmpeg for {os.path.basename(output_path)}...")
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(command, check=True, capture_output=True, text=True, startupinfo=startupinfo)
        print(f"FFmpeg processing complete for {os.path.basename(output_path)}.")
        return None
    except subprocess.CalledProcessError as e:
        return f"FFmpeg error:\n{e.stderr}"
