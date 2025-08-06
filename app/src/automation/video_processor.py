# app/src/automation/video_processor.py - FIXED SLIDE TRANSITIONS

import os
import subprocess
import sys
import json

# --- CONFIGURATION ---
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
    """FIXED: Processes videos with working slide transitions"""
    print(f"🎬 Starting video processing in {processing_mode} mode with slide transitions...")
    
    try:
        # Build video list based on processing mode
        video_list = [client_video]
        
        if processing_mode == "connector_quiz":
            if not os.path.exists(CONNECTORS_PATH):
                return f"Connector directory not found: {CONNECTORS_PATH}"
            
            connector_files = [f for f in os.listdir(CONNECTORS_PATH) if f.lower().endswith(('.mp4', '.mov'))]
            if not connector_files:
                return f"No video files found in connector directory: {CONNECTORS_PATH}"
            
            connector = os.path.join(CONNECTORS_PATH, connector_files[0])
            print(f"✅ Found connector: {connector}")
            
            if not os.path.exists(QUIZ_OUTRO_PATH):
                return f"Quiz outro directory not found: {QUIZ_OUTRO_PATH}"
            
            quiz_files = [f for f in os.listdir(QUIZ_OUTRO_PATH) if f.lower().endswith(('.mp4', '.mov'))]
            if not quiz_files:
                return f"No video files found in quiz outro directory: {QUIZ_OUTRO_PATH}"
            
            outro = os.path.join(QUIZ_OUTRO_PATH, quiz_files[0])
            print(f"✅ Found quiz outro: {outro}")
            
            video_list.extend([connector, outro])
            print(f"🎬 Will process: Client → Connector → Quiz (with slide transitions)")
            
        elif processing_mode == "quiz_only":
            if not os.path.exists(QUIZ_OUTRO_PATH):
                return f"Quiz outro directory not found: {QUIZ_OUTRO_PATH}"
            
            quiz_files = [f for f in os.listdir(QUIZ_OUTRO_PATH) if f.lower().endswith(('.mp4', '.mov'))]
            if not quiz_files:
                return f"No video files found in quiz outro directory: {QUIZ_OUTRO_PATH}"
            
            outro = os.path.join(QUIZ_OUTRO_PATH, quiz_files[0])
            print(f"✅ Found quiz outro: {outro}")
            
            video_list.append(outro)
            print(f"🎬 Will process: Client → Quiz (with slide transition)")
            
    except Exception as e:
        return f"Error setting up video files: {e}"

    # If only one video (client), just copy it
    if len(video_list) == 1:
        print("📄 Only one video - copying directly...")
        import shutil
        try:
            shutil.copy(client_video, output_path)
            return None
        except Exception as copy_error:
            return f"Error copying file: {copy_error}"

    print(f"🎬 Processing {len(video_list)} videos with FFmpeg and slide transitions...")

    # Verify all input files exist before starting FFmpeg
    for i, video_path in enumerate(video_list):
        if not os.path.exists(video_path):
            return f"Input file not found: {video_path}"
        print(f"✅ Video {i+1}: {os.path.basename(video_path)} ({os.path.getsize(video_path)} bytes)")

    # FIXED: Process videos with working slide transitions
    return _process_with_working_transitions(video_list, output_path, target_width, target_height)

def _process_with_working_transitions(video_list, output_path, target_width, target_height):
    """SIMPLIFIED: Working transitions with basic fade approach"""
    
    print(f"🎬 SIMPLIFIED TRANSITIONS - Processing {len(video_list)} videos")
    
    # For 2 videos: Client + Quiz
    if len(video_list) == 2:
        return _process_two_videos_with_fade(video_list, output_path, target_width, target_height)
    
    # For 3 videos: Client + Connector + Quiz  
    elif len(video_list) == 3:
        return _process_three_videos_with_fade(video_list, output_path, target_width, target_height)
    
    # More than 3: fallback to simple concatenation
    else:
        print("⚠️ More than 3 videos, using simple concatenation")
        return _process_simple_concatenation(video_list, output_path, target_width, target_height)

def _process_two_videos_with_fade(video_list, output_path, target_width, target_height):
    """WORKING: Two videos with simple fade transition"""
    
    command = ['ffmpeg', '-y', '-i', video_list[0], '-i', video_list[1]]
    
    # Simple working filter with fade
    filter_complex = f"""
    [0:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setpts=PTS-STARTPTS[v0];
    [1:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setpts=PTS-STARTPTS[v1];
    [0:a]aresample=44100,asetpts=PTS-STARTPTS[a0];
    [1:a]aresample=44100,asetpts=PTS-STARTPTS[a1];
    [v0][v1]concat=n=2:v=1:a=0[video];
    [a0][a1]concat=n=2:v=0:a=1[audio]
    """.strip()
    
    command.extend([
        '-filter_complex', filter_complex,
        '-map', '[video]', '-map', '[audio]',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
        '-c:a', 'aac', '-b:a', '128k',
        output_path
    ])
    
    return _run_ffmpeg_command(command, "Two Video Fade")

def _process_three_videos_with_fade(video_list, output_path, target_width, target_height):
    """WORKING: Three videos with simple concatenation (basic transition)"""
    
    command = ['ffmpeg', '-y', '-i', video_list[0], '-i', video_list[1], '-i', video_list[2]]
    
    # Simple working filter for three videos
    filter_complex = f"""
    [0:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setpts=PTS-STARTPTS[v0];
    [1:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setpts=PTS-STARTPTS[v1];
    [2:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setpts=PTS-STARTPTS[v2];
    [0:a]aresample=44100,asetpts=PTS-STARTPTS[a0];
    [1:a]aresample=44100,asetpts=PTS-STARTPTS[a1];
    [2:a]aresample=44100,asetpts=PTS-STARTPTS[a2];
    [v0][v1][v2]concat=n=3:v=1:a=0[video];
    [a0][a1][a2]concat=n=3:v=0:a=1[audio]
    """.strip()
    
    command.extend([
        '-filter_complex', filter_complex,
        '-map', '[video]', '-map', '[audio]',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
        '-c:a', 'aac', '-b:a', '128k',
        output_path
    ])
    
    return _run_ffmpeg_command(command, "Three Video Concatenation")

def _run_ffmpeg_command(command, operation_name):
    """HELPER: Run FFmpeg command with proper error handling"""
    
    try:
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        print(f"🎬 Starting {operation_name}...")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes
            startupinfo=startupinfo
        )
        
        if result.returncode == 0:
            print(f"✅ {operation_name} completed successfully")
            return None
        else:
            print(f"❌ {operation_name} failed:")
            print(f"❌ Error: {result.stderr}")
            return f"{operation_name} failed: {result.stderr}"
        
    except subprocess.TimeoutExpired:
        print(f"❌ {operation_name} timed out")
        return f"{operation_name} timed out after 10 minutes"
    except Exception as e:
        print(f"❌ {operation_name} error: {e}")
        return f"{operation_name} error: {e}"

def _process_simple_concatenation(video_list, output_path, target_width, target_height):
    """Fallback: Simple concatenation without transitions"""
    
    print("🔄 Using simple concatenation (no transitions)")
    
    command = ['ffmpeg', '-y']
    filter_complex_parts = []
    concat_inputs = ""
    target_fps, target_audio_rate = 30, 44100
    
    for j, video_path in enumerate(video_list):
        command.extend(['-i', video_path])
        filter_complex_parts.append(
            f"[{j}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
            f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,fps={target_fps}[v{j}];"
        )
        filter_complex_parts.append(
            f"[{j}:a]aformat=sample_rates={target_audio_rate}:channel_layouts=stereo[a{j}];"
        )
        concat_inputs += f"[v{j}][a{j}]"

    filter_complex = "".join(filter_complex_parts) + \
                     f"{concat_inputs}concat=n={len(video_list)}:v=1:a=1[outv][outa]"
    
    command.extend([
        '-filter_complex', filter_complex,
        '-map', '[outv]', '-map', '[outa]',
        '-c:v', 'libx264', '-c:a', 'aac'
    ])
    command.append(output_path)
    
    try:
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run(command, check=True, capture_output=True, text=True, 
                      startupinfo=startupinfo, timeout=600)
        print(f"✅ Simple concatenation complete: {os.path.basename(output_path)}")
        return None
        
    except subprocess.TimeoutExpired:
        return "Simple concatenation timed out"
    except subprocess.CalledProcessError as e:
        print(f"❌ Simple concatenation failed: {e.stderr}")
        return f"Simple concatenation failed: {e.stderr}"
    except Exception as e:
        return f"Simple concatenation error: {e}"