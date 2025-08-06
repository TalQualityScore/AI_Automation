# app/src/automation/video_processor.py - COMPLETE WITH ALL FUNCTIONS

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
    """SIMPLIFIED: Process videos with basic working concatenation (transitions removed for reliability)"""
    
    print(f"🎬 Starting video processing in {processing_mode} mode...")
    
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
            print(f"🎬 Will process: Client → Connector → Quiz (simple concatenation)")
            
        elif processing_mode == "quiz_only":
            if not os.path.exists(QUIZ_OUTRO_PATH):
                return f"Quiz outro directory not found: {QUIZ_OUTRO_PATH}"
            
            quiz_files = [f for f in os.listdir(QUIZ_OUTRO_PATH) if f.lower().endswith(('.mp4', '.mov'))]
            if not quiz_files:
                return f"No video files found in quiz outro directory: {QUIZ_OUTRO_PATH}"
            
            outro = os.path.join(QUIZ_OUTRO_PATH, quiz_files[0])
            print(f"✅ Found quiz outro: {outro}")
            
            video_list.append(outro)
            print(f"🎬 Will process: Client → Quiz (simple concatenation)")
            
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

    print(f"🎬 Processing {len(video_list)} videos with SIMPLE concatenation...")

    # Verify all input files exist
    for i, video_path in enumerate(video_list):
        if not os.path.exists(video_path):
            return f"Input file not found: {video_path}"
        print(f"✅ Video {i+1}: {os.path.basename(video_path)} ({os.path.getsize(video_path)} bytes)")

    # SIMPLIFIED: Use basic concatenation that works reliably
    return _process_simple_concatenation_reliable(video_list, output_path, target_width, target_height)


def _process_simple_concatenation_reliable(video_list, output_path, target_width, target_height):
    """RELIABLE: Simple concatenation that works every time"""
    
    print(f"🔄 Using RELIABLE simple concatenation for {len(video_list)} videos")
    
    concat_file = None
    try:
        # Create temporary file list
        concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        
        for video_path in video_list:
            # Use absolute paths and escape them properly
            abs_path = os.path.abspath(video_path)
            concat_file.write(f"file '{abs_path}'\n")
        
        concat_file.close()
        
        print(f"📝 Created concat file: {concat_file.name}")
        
        # Simple FFmpeg concat command that works
        command = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file.name,
            '-c', 'copy',  # Copy streams without re-encoding for speed/reliability
            output_path
        ]
        
        print(f"🎬 Running FFmpeg command...")
        print(f"Command: {' '.join(command)}")
        
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes
            startupinfo=startupinfo
        )
        
        if result.returncode == 0:
            print(f"✅ Simple concatenation completed successfully")
            print(f"✅ Output: {os.path.basename(output_path)}")
            return None
        else:
            print(f"❌ FFmpeg failed:")
            print(f"❌ Error: {result.stderr}")
            
            # Fallback: Try with re-encoding if copy failed
            return _process_with_reencoding_fallback(video_list, output_path, target_width, target_height)
        
    except subprocess.TimeoutExpired:
        print(f"❌ Simple concatenation timed out")
        return "Simple concatenation timed out after 10 minutes"
    except Exception as e:
        print(f"❌ Simple concatenation error: {e}")
        return f"Simple concatenation error: {e}"
    finally:
        # Clean up temporary file
        if concat_file and os.path.exists(concat_file.name):
            try:
                os.unlink(concat_file.name)
            except:
                pass


def _process_with_reencoding_fallback(video_list, output_path, target_width, target_height):
    """FALLBACK: Re-encode if simple copy failed"""
    
    print(f"🔄 FALLBACK: Using re-encoding for {len(video_list)} videos")
    
    command = ['ffmpeg', '-y']
    filter_complex_parts = []
    concat_inputs = ""
    target_fps, target_audio_rate = 30, 44100
    
    for j, video_path in enumerate(video_list):
        command.extend(['-i', video_path])
        
        # Normalize video stream
        filter_complex_parts.append(
            f"[{j}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
            f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,fps={target_fps}[v{j}];"
        )
        
        # Normalize audio stream
        filter_complex_parts.append(
            f"[{j}:a]aformat=sample_rates={target_audio_rate}:channel_layouts=stereo[a{j}];"
        )
        
        concat_inputs += f"[v{j}][a{j}]"

    filter_complex = "".join(filter_complex_parts) + \
                     f"{concat_inputs}concat=n={len(video_list)}:v=1:a=1[outv][outa]"
    
    command.extend([
        '-filter_complex', filter_complex,
        '-map', '[outv]', '-map', '[outa]',
        '-c:v', 'libx264', '-c:a', 'aac',
        '-preset', 'fast'  # Faster encoding
    ])
    command.append(output_path)
    
    try:
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run(command, check=True, capture_output=True, text=True, 
                      startupinfo=startupinfo, timeout=900)  # 15 minutes
        
        print(f"✅ Fallback re-encoding complete: {os.path.basename(output_path)}")
        return None
        
    except subprocess.TimeoutExpired:
        return "Re-encoding fallback timed out"
    except subprocess.CalledProcessError as e:
        print(f"❌ Re-encoding fallback failed: {e.stderr}")
        return f"Re-encoding fallback failed: {e.stderr}"
    except Exception as e:
        return f"Re-encoding fallback error: {e}"