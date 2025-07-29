# --- Checkpoint Version 1.0: Basic Combine Script ---
# Goal: Combines all MP4s from an input folder into one video.

import os
import glob
import subprocess
import csv
from datetime import datetime

# --- CONFIGURATION ---
# You can change these paths if you move your folders later.
INPUT_VIDEO_FOLDER = r"C:\Users\talZ\Desktop\Videos"
OUTPUT_BASE_FOLDER = r"C:\Users\talZ\Desktop\Output"
RUN_ID = "Run_001"
OUTPUT_VARIANT_FILENAME = "variant_01.mp4"
LOG_FILENAME = "log.csv"

# --- SCRIPT START ---

print("--- Starting Auto-Combine Script (v1.0) ---")

# 1. Define the full path for this run's output
run_output_folder = os.path.join(OUTPUT_BASE_FOLDER, RUN_ID)
final_video_path = os.path.join(run_output_folder, OUTPUT_VARIANT_FILENAME)
log_file_path = os.path.join(run_output_folder, LOG_FILENAME)

# 2. Find all .mp4 files in the input folder
print(f"Searching for .mp4 files in: {INPUT_VIDEO_FOLDER}")
# Using glob to find all files ending with .mp4
source_videos = glob.glob(os.path.join(INPUT_VIDEO_FOLDER, "*.mp4"))

# 3. Check if we found any videos
if not source_videos:
    print("\nERROR: No .mp4 files found in the input folder. Exiting.")
    exit()

# 4. Sort the videos numerically based on their filenames (e.g., 1.mp4, 2.mp4, 10.mp4)
# This is a "natural sort" which is smarter than a simple text sort.
def get_filenumber(filepath):
    basename = os.path.basename(filepath) # e.g., "10.mp4"
    filename_no_ext = os.path.splitext(basename)[0] # e.g., "10"
    return int(filename_no_ext)

source_videos.sort(key=get_filenumber)

print(f"\nFound {len(source_videos)} video files to combine. Order is:")
for video_path in source_videos:
    print(f"  -> {os.path.basename(video_path)}")

# 5. Create the output directory if it doesn't exist
print(f"\nCreating output directory: {run_output_folder}")
os.makedirs(run_output_folder, exist_ok=True)

# 6. Create a temporary file list for FFmpeg
# This is the safest and most efficient way to combine many files.
temp_list_filename = os.path.join(run_output_folder, "filelist.txt")
with open(temp_list_filename, 'w') as f:
    for video_path in source_videos:
        # FFmpeg needs a specific format: file '/path/to/video.mp4'
        f.write(f"file '{video_path.replace(os.sep, '/')}'\n")

print("Generated temporary file list for FFmpeg.")

# 7. Build and run the FFmpeg command to combine the videos
# -f concat: Use the concat demuxer
# -safe 0: Required for using absolute paths in the file list
# -c copy: VERY IMPORTANT! This copies the video stream without re-encoding. It's extremely fast.
ffmpeg_command = [
    'ffmpeg',
    '-f', 'concat',
    '-safe', '0',
    '-i', temp_list_filename,
    '-c', 'copy',
    final_video_path
]

print("\nRunning FFmpeg to combine videos... This should be fast.")
try:
    # We use -y to automatically overwrite the output file if it already exists
    # This is helpful for re-running the script during tests.
    subprocess.run(['ffmpeg', '-y'] + ffmpeg_command[1:], check=True, capture_output=True, text=True)
    print("✅ SUCCESS: Video combination complete!")
    export_status = "Success"
except FileNotFoundError:
    print("\n❌ ERROR: FFmpeg command not found.")
    print("Please ensure FFmpeg is installed and accessible in your system's PATH.")
    export_status = "Failed - FFmpeg not found"
except subprocess.CalledProcessError as e:
    print("\n❌ ERROR: FFmpeg failed during execution.")
    print("FFmpeg error output:")
    print(e.stderr)
    export_status = f"Failed - FFmpeg error"

# 8. Clean up the temporary file list
os.remove(temp_list_filename)
print("Cleaned up temporary file.")

# 9. Create the log.csv file
if export_status == "Success":
    print(f"Creating log file at: {log_file_path}")
    header = ['variant_id', 'clip_filenames_used', 'output_filename', 'status']
    
    # Get just the filenames, not the full paths
    clip_basenames = [os.path.basename(p) for p in source_videos]

    data = [
        RUN_ID + "-1", # e.g., "Run_001-1"
        ",".join(clip_basenames), # "1.mp4,2.mp4,..."
        OUTPUT_VARIANT_FILENAME,
        export_status
    ]

    with open(log_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(data)
    print("✅ Log file created successfully.")

print("\n--- Script finished. ---")