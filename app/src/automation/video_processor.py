# app/src/automation/video_processor.py - REVERTED TO WORKING VERSION

import os
import subprocess
import sys
import json
import tempfile
import shutil

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CONNECTORS_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos", "connectors")
QUIZ_OUTRO_PATH = os.path.join(SCRIPT_DIR, "Assets", "Videos", "quiz_outro")

def get_video_dimensions(video_path):
    """Gets the width and height of a video using ffprobe."""
    print(f"🔍 Getting dimensions for: {os.path.basename(video_path)}")
    
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', 
               '-show_entries', 'stream=width,height', '-of', 'json', video_path]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        
        if 'streams' in data and len(data['streams']) > 0:
            width = data['streams'][0]['width']
            height = data['streams'][0]['height']
            print(f"✅ Video dimensions: {width}x{height}")
            return width, height, None
        
        return None, None, "Video stream not found."
        
    except subprocess.TimeoutExpired:
        return None, None, "FFprobe timeout - video file may be corrupted"
    except subprocess.CalledProcessError as e:
        return None, None, f"FFprobe failed: {e.stderr if hasattr(e, 'stderr') else str(e)}"
    except json.JSONDecodeError as e:
        return None, None, f"Failed to parse FFprobe output: {e}"
    except Exception as e:
        return None, None, f"Error getting video dimensions: {e}"

def process_video_sequence(client_video, output_path, target_width, target_height, processing_mode="connector_quiz"):
    """REVERTED: Back to the WORKING version that was tested and reliable"""
    
    print(f"🎬 Starting RELIABLE video processing in {processing_mode} mode...")
    
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
            print(f"🎬 Will process: Client → Connector → Quiz")
            
        elif processing_mode == "quiz_only":
            if not os.path.exists(QUIZ_OUTRO_PATH):
                return f"Quiz outro directory not found: {QUIZ_OUTRO_PATH}"
            
            quiz_files = [f for f in os.listdir(QUIZ_OUTRO_PATH) if f.lower().endswith(('.mp4', '.mov'))]
            if not quiz_files:
                return f"No video files found in quiz outro directory: {QUIZ_OUTRO_PATH}"
            
            outro = os.path.join(QUIZ_OUTRO_PATH, quiz_files[0])
            print(f"✅ Found quiz outro: {outro}")
            
            video_list.append(outro)
            print(f"🎬 Will process: Client → Quiz")
            
    except Exception as e:
        return f"Error setting up video files: {e}"

    # If only one video (client), just copy it
    if len(video_list) == 1:
        print("📄 Only one video - copying directly...")
        try:
            shutil.copy(client_video, output_path)
            return None
        except Exception as copy_error:
            return f"Error copying file: {copy_error}"

    print(f"🎬 Processing {len(video_list)} videos with WORKING method...")

    # Verify all input files exist
    for i, video_path in enumerate(video_list):
        if not os.path.exists(video_path):
            return f"Input file not found: {video_path}"
        print(f"✅ Video {i+1}: {os.path.basename(video_path)} ({os.path.getsize(video_path)} bytes)")

    # REVERTED: Use the method that was ACTUALLY WORKING before
    return _process_with_working_method(video_list, output_path, target_width, target_height)


def _process_with_working_method(video_list, output_path, target_width, target_height):
    """REVERTED: The method that was working before the refactor"""
    
    print(f"🔄 Using TESTED working method for {len(video_list)} videos")
    
    try:
        # Build FFmpeg command using the WORKING approach
        command = ['ffmpeg', '-y']
        filter_complex_parts = []
        concat_inputs = ""
        
        # Define a universal standard for all clips (this was working)
        target_fps = 30
        target_audio_rate = 44100
        
        for j, video_path in enumerate(video_list):
            command.extend(['-i', video_path])
            # Standardize each video and audio stream (the WORKING way)
            filter_complex_parts.append(
                f"[{j}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
                f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,"
                f"setsar=1,fps={target_fps},setpts=PTS-STARTPTS[v{j}];"
            )
            filter_complex_parts.append(
                f"[{j}:a]aformat=sample_rates={target_audio_rate}:channel_layouts=stereo,"
                f"asetpts=PTS-STARTPTS[a{j}];"
            )
            concat_inputs += f"[v{j}][a{j}]"

        filter_complex = "".join(filter_complex_parts) + \
                         f"{concat_inputs}concat=n={len(video_list)}:v=1:a=1[outv][outa]"
        
        command.extend([
            '-filter_complex', filter_complex,
            '-map', '[outv]', '-map', '[outa]',
            '-c:v', 'libx264', '-c:a', 'aac',
            '-preset', 'medium'  # Good balance of speed and quality
        ])
        command.append(output_path)
        
        print(f"🎬 Running WORKING FFmpeg command...")
        
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes
            startupinfo=startupinfo
        )
        
        if result.returncode == 0:
            print(f"✅ WORKING method completed successfully")
            print(f"✅ Output: {os.path.basename(output_path)}")
            return None
        else:
            print(f"❌ FFmpeg failed:")
            print(f"❌ Error: {result.stderr}")
            return f"FFmpeg processing failed: {result.stderr}"
        
    except subprocess.TimeoutExpired:
        print(f"❌ Processing timed out")
        return "Processing timed out after 30 minutes"
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return f"Processing error: {e}"