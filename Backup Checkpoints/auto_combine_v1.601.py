# --- Version 1.601: Syntax Bug Fix ---
# Goal: Fixes the 'invalid decimal literal' SyntaxError by correctly
#       quoting the filename string for the os.path.join function.

import os
import subprocess
import json

print("--- Starting Advanced Overlay Script (v1.601) ---")

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Input files
# --- THIS IS THE FIXED LINE ---
INPUT_VIDEO = os.path.join(SCRIPT_DIR, "Videos", "1.mp4")
OVERLAY_IMAGE = os.path.join(SCRIPT_DIR, "rounded_box.png")

# Output file
OUTPUT_VIDEO = os.path.join(SCRIPT_DIR, "Output", "1_with_effects_v1.601.mp4")

# Font paths (ensure these exist on your system)
FONT_PRIMARY = "C\\:/Windows/Fonts/impact.ttf"
FONT_SECONDARY = "C\\:/Windows/Fonts/arial.ttf"

# --- 1. Get Video Duration using ffprobe ---
duration = 0.0
try:
    command = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', INPUT_VIDEO
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    duration = float(result.stdout)
    print(f"Input video duration: {duration:.2f} seconds.")
except Exception as e:
    print(f"ERROR: Could not get video duration for {INPUT_VIDEO}. Exiting.")
    print(f"Reason: {e}")
    exit()

if duration == 0:
    print("ERROR: Video duration is zero. Cannot proceed.")
    exit()

# --- 2. Build the Complex FFmpeg Filter Command ---
text_line_1 = "drawtext=text='TEST':fontfile='{}':fontsize=120:fontcolor=yellow:x=(w-text_w)/2:y=(h/2)+150:borderw=3:bordercolor=black".format(FONT_PRIMARY)
text_line_2 = "drawtext=text='text':fontfile='{}':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h/2)+300:borderw=3:bordercolor=black".format(FONT_SECONDARY)

halfway_point = duration / 2
timed_text_1 = "drawtext=text='text 1':fontfile='{}':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=200:enable='between(t,0,{})'".format(FONT_SECONDARY, halfway_point)
timed_text_2 = "drawtext=text='text 2':fontfile='{}':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=200:enable='between(t,{},{})'".format(FONT_SECONDARY, halfway_point, duration)

filter_complex = (
    "[0:v][1:v]overlay=x=0:y=0[bg_with_box];"
    "[bg_with_box]{}, {}, {}, {}[final_v]".format(
        text_line_1,
        text_line_2,
        timed_text_1,
        timed_text_2
    )
)

# --- 3. Assemble and Run the Final FFmpeg Command ---
ffmpeg_command = [
    'ffmpeg',
    '-y',
    '-i', INPUT_VIDEO,
    '-i', OVERLAY_IMAGE,
    '-filter_complex', filter_complex,
    '-map', '[final_v]',
    '-map', '0:a',
    '-c:a', 'copy',
    OUTPUT_VIDEO
]

print("\nApplying advanced overlays. This will re-encode the video and may take a moment...")

try:
    subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
    print(f"✅ SUCCESS: Effects applied. Output saved to:\n{OUTPUT_VIDEO}")
except subprocess.CalledProcessError as e:
    print("\n❌ ERROR: FFmpeg failed during execution.")
    print("This is often due to incorrect font paths or filter syntax.")
    print("\n--- FFmpeg Command Sent ---")
    print(" ".join(ffmpeg_command))
    print("\n--- FFmpeg Error Output ---")
    print(e.stderr)

print("\n--- Script finished. ---")