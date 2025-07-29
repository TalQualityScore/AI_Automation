# --- Version 1.610: Config-Driven Overlays ---
# Goal: Reads a `config.yml` file to dynamically build and place
#       overlays and text, giving the user full creative control.

import os
import subprocess
import json
import yaml # --- NEW in v1.610
from datetime import datetime

print("--- Starting Config-Driven Overlay Script (v1.610) ---")

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.yml")
INPUT_VIDEO = os.path.join(SCRIPT_DIR, "Videos", "1.mp4")
OUTPUT_BASE_DIR = os.path.join(SCRIPT_DIR, "Output")
FONT_DIR = "C:/Windows/Fonts/" # Base directory for fonts

# --- 1. Load Configuration from YAML file ---
try:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    print("✅ Successfully loaded config.yml")
except FileNotFoundError:
    print(f"❌ ERROR: config.yml not found at {CONFIG_FILE}. Please create it. Exiting.")
    exit()
except Exception as e:
    print(f"❌ ERROR: Could not read or parse config.yml. Reason: {e}. Exiting.")
    exit()

# --- 2. Setup Output Directory (Bug Fix) ---
RUN_ID = f"Run_v1.610_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
run_output_folder = os.path.join(OUTPUT_BASE_DIR, RUN_ID)
os.makedirs(run_output_folder, exist_ok=True)
OUTPUT_VIDEO = os.path.join(run_output_folder, "final_video.mp4")
print(f"Output will be saved in: {run_output_folder}")

# --- 3. Get Video Info (Duration and Dimensions) ---
video_info = {}
try:
    command = [
        'ffprobe', '-v', 'error', '-show_entries', 'stream=width,height',
        '-show_entries', 'format=duration', '-of', 'json', INPUT_VIDEO
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    video_info['duration'] = float(data['format']['duration'])
    video_info['width'] = data['streams'][0]['width']
    video_info['height'] = data['streams'][0]['height']
    print(f"Video Info: {video_info['width']}x{video_info['height']}, Duration: {video_info['duration']:.2f}s")
except Exception as e:
    print(f"❌ ERROR: Could not get video info. Reason: {e}. Exiting.")
    exit()

# --- 4. Dynamically Build the Filter Command from Config ---
ffmpeg_command = ['ffmpeg', '-y', '-i', INPUT_VIDEO]
filter_parts = []
last_video_stream = "[0:v]" # Start with the base video
input_stream_counter = 1 # 0 is the video, so images start at 1

# --- Process Image Overlays ---
if 'image_overlays' in config:
    for overlay_conf in config.get('image_overlays', []):
        image_path = os.path.join(SCRIPT_DIR, overlay_conf['file'])
        if not os.path.exists(image_path):
            print(f"  WARNING: Image not found at {image_path}, skipping.")
            continue
        
        ffmpeg_command.extend(['-i', image_path])
        next_video_stream = f"[v_out_{input_stream_counter}]"
        
        x_pos = {'center': '(main_w-overlay_w)/2', 'left': '0', 'right': 'main_w-overlay_w'}.get(overlay_conf.get('x'), str(overlay_conf.get('x', '0')))
        y_pos = {'center': '(main_h-overlay_h)/2', 'top': '0', 'bottom': 'main_h-overlay_h'}.get(overlay_conf.get('y'), str(overlay_conf.get('y', '0')))
        
        filter_parts.append(f"{last_video_stream}[{input_stream_counter}:v]overlay=x={x_pos}:y={y_pos}{next_video_stream}")
        
        last_video_stream = next_video_stream
        input_stream_counter += 1

# --- Process Text Overlays ---
text_filters = []
if 'text_overlays' in config:
    for text_conf in config.get('text_overlays', []):
        # Escape special characters for FFmpeg
        font_path = os.path.join(FONT_DIR, text_conf.get('font', 'arial.ttf')).replace('\\', '/').replace(':', '\\:')
        
        # Translate time keywords
        start = text_conf.get('start_time', 'start')
        end = text_conf.get('end_time', 'end')
        time_filter = f":enable='between(t,{0 if start == 'start' else start},{video_info['duration'] if end == 'end' else end})'"
        
        # Translate position keywords
        x_pos = {'center': '(w-text_w)/2', 'left': '20', 'right': 'w-text_w-20'}.get(text_conf.get('x'), str(text_conf.get('x', '0')))
        y_pos = {'center': '(h-text_h)/2', 'top': '20', 'bottom': 'h-text_h-20'}.get(text_conf.get('y'), str(text_conf.get('y', '0')))
        
        # Build drawtext filter part
        text_filter = f"drawtext=text='{text_conf.get('text', '')}':fontfile='{font_path}':fontsize={text_conf.get('size', 50)}:fontcolor={text_conf.get('color', 'white')}:x={x_pos}:y={y_pos}"
        if 'stroke_color' in text_conf:
            text_filter += f":borderw={text_conf.get('stroke_width', 2)}:bordercolor={text_conf.get('stroke_color', 'black')}"
        text_filter += time_filter
        text_filters.append(text_filter)

# Combine text filters with the last video stream
if text_filters:
    filter_parts.append(f"{last_video_stream}{','.join(text_filters)}[final_v]")
    last_video_stream = "[final_v]"
else: # If no text filters, the last stream from images is the final one
    filter_parts.append(f"{last_video_stream}copy[final_v]")

# --- 5. Assemble and Run Final Command ---
final_filter_string = ";".join(filter_parts)
ffmpeg_command.extend(['-filter_complex', final_filter_string])
ffmpeg_command.extend(['-map', '[final_v]', '-map', '0:a?', '-c:a', 'copy', OUTPUT_VIDEO]) # 0:a? ignores error if no audio

print("\nApplying effects from config.yml...")
try:
    subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
    print(f"✅ SUCCESS: Video created at\n{OUTPUT_VIDEO}")
except subprocess.CalledProcessError as e:
    print("\n❌ ERROR: FFmpeg failed.")
    print("\n--- Command Sent ---")
    print(" ".join(ffmpeg_command))
    print("\n--- FFmpeg Error Output ---")
    print(e.stderr)

print("\n--- Script finished. ---")