# --- Version 1.600 Advanced Overlay Effects ---
# Goal Apply a complex set of visual effects to a single video clip.
# 1. Overlay a PNG with a rounded box.
# 2. Add two lines of styled text.
# 3. Add text that changes mid-way through the clip.

import os
import subprocess
import json

print(--- Starting Advanced Overlay Script (v1.600) ---)

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Input files
INPUT_VIDEO = os.path.join(SCRIPT_DIR, Videos, 1.mp4)
OVERLAY_IMAGE = os.path.join(SCRIPT_DIR, rounded_box.png) # The PNG you created

# Output file
OUTPUT_VIDEO = os.path.join(SCRIPT_DIR, Output, 1_with_effects.mp4)

# Font paths (ensure these exist on your system)
FONT_PRIMARY = CWindowsFontsimpact.ttf
FONT_SECONDARY = CWindowsFontsarial.ttf

# --- 1. Get Video Duration using ffprobe ---
duration = 0.0
try
    command = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1nokey=1', INPUT_VIDEO
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    duration = float(result.stdout)
    print(fInput video duration {duration.2f} seconds.)
except Exception as e
    print(fERROR Could not get video duration for {INPUT_VIDEO}. Exiting.)
    print(fReason {e})
    exit()

if duration == 0
    print(ERROR Video duration is zero. Cannot proceed.)
    exit()

# --- 2. Build the Complex FFmpeg Filter Command ---
# This is where all the magic happens. We chain multiple filters together.

# We define the text elements first for clarity
# Effect 2 Two lines of static text
text_line_1 = drawtext=text='TEST'fontfile='{}'fontsize=120fontcolor=yellowx=(w-text_w)2y=(h2)+150borderw=3bordercolor=black.format(FONT_PRIMARY)
text_line_2 = drawtext=text='text'fontfile='{}'fontsize=80fontcolor=whitex=(w-text_w)2y=(h2)+300borderw=3bordercolor=black.format(FONT_SECONDARY)

# Effect 3 Timed text that changes
halfway_point = duration  2
timed_text_1 = drawtext=text='text 1'fontfile='{}'fontsize=96fontcolor=whitex=(w-text_w)2y=200enable='between(t,0,{})'.format(FONT_SECONDARY, halfway_point)
timed_text_2 = drawtext=text='text 2'fontfile='{}'fontsize=96fontcolor=whitex=(w-text_w)2y=200enable='between(t,{},{})'.format(FONT_SECONDARY, halfway_point, duration)

# Now we build the filter chain string
filter_complex = (
    # Step A Take the video [0v] and the overlay image [1v] and place the image on top.
    # The output of this step is named [bg_with_box].
    [0v][1v]overlay=x=0y=0[bg_with_box];
    
    # Step B Take the [bg_with_box] stream and apply all four text filters to it.
    # Filters are separated by commas.
    [bg_with_box]{}, {}, {}, {}[final_v].format(
        text_line_1,
        text_line_2,
        timed_text_1,
        timed_text_2
    )
)

# --- 3. Assemble and Run the Final FFmpeg Command ---
ffmpeg_command = [
    'ffmpeg',
    '-y',                   # Overwrite output file if it exists
    '-i', INPUT_VIDEO,      # Input 0
    '-i', OVERLAY_IMAGE,    # Input 1
    '-filter_complex', filter_complex,
    '-map', '[final_v]',    # Use the final video stream from the filter
    '-map', '0a',          # Use the original audio from the first input
    '-ca', 'copy',         # Copy the audio stream without re-encoding (it's fast)
    OUTPUT_VIDEO
]

print(nApplying advanced overlays. This will re-encode the video and may take a moment...)

try
    subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
    print(f✅ SUCCESS Effects applied. Output saved ton{OUTPUT_VIDEO})
except subprocess.CalledProcessError as e
    print(n❌ ERROR FFmpeg failed during execution.)
    print(This is often due to incorrect font paths or filter syntax.)
    print(n--- FFmpeg Command Sent ---)
    print( .join(ffmpeg_command))
    print(n--- FFmpeg Error Output ---)
    print(e.stderr)

print(n--- Script finished. ---)