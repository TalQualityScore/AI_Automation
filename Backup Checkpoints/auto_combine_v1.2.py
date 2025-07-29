# --- Checkpoint Version 1.2: Interactive Editor & Timecode Logger ---
# Goal: Creates an initial video, then allows the user to interactively
#       swap clips to create new variants. Logs clip order and timecodes.

import os
import glob
import subprocess
import csv
import json # To get video duration with ffprobe

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_VIDEO_FOLDER = os.path.join(SCRIPT_DIR, "Videos")
OUTPUT_BASE_FOLDER = os.path.join(SCRIPT_DIR, "Output")
RUN_ID = "Run_003"
LOG_FILENAME = "log.csv"

# --- UTILITY FUNCTIONS ---

def get_clip_durations(video_files):
    """Uses ffprobe to get the duration of each video file."""
    durations = {}
    print("Analyzing clip durations...")
    for video_path in video_files:
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            durations[video_path] = float(result.stdout)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  WARNING: Could not get duration for {os.path.basename(video_path)}. Defaulting to 0.")
            durations[video_path] = 0.0
    print("Duration analysis complete.\n")
    return durations

def format_time(seconds):
    """Converts seconds (float) to HH:MM:SS.ms string."""
    millis = int((seconds - int(seconds)) * 1000)
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}.{millis:03d}"

def combine_and_log(video_order, variant_id, run_output_folder, log_file_path, clip_durations):
    """Combines a list of videos and logs the result with timecodes."""
    output_filename = f"variant_{variant_id.split('-')[1]}.mp4"
    final_video_path = os.path.join(run_output_folder, output_filename)
    
    # Create temp filelist for FFmpeg
    temp_list_filename = os.path.join(run_output_folder, "filelist_temp.txt")
    with open(temp_list_filename, 'w') as f:
        for video_path in video_order:
            f.write(f"file '{video_path.replace(os.sep, '/')}'\n")

    # Run FFmpeg
    ffmpeg_command = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', temp_list_filename, '-c', 'copy', final_video_path]
    try:
        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print(f"✅ SUCCESS: Saved {output_filename}")
        status = "Success"
    except Exception as e:
        print(f"❌ ERROR combining video: {e}")
        status = "Failed"
    
    os.remove(temp_list_filename)

    # Append detailed log
    with open(log_file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        current_time = 0.0
        for video_path in video_order:
            duration = clip_durations.get(video_path, 0.0)
            start_time_str = format_time(current_time)
            end_time_str = format_time(current_time + duration)
            writer.writerow([variant_id, os.path.basename(video_path), start_time_str, end_time_str, status])
            current_time += duration
    return video_order # Return the order we just processed


# --- SCRIPT START ---

print("--- Starting Interactive Editor Script (v1.2) ---")

# 1. Setup paths and directories
run_output_folder = os.path.join(OUTPUT_BASE_FOLDER, RUN_ID)
os.makedirs(run_output_folder, exist_ok=True)
log_file_path = os.path.join(run_output_folder, LOG_FILENAME)

# 2. Find and sort videos
source_videos = sorted(glob.glob(os.path.join(INPUT_VIDEO_FOLDER, "*.mp4")))
if not source_videos:
    print("\nERROR: No .mp4 files found. Exiting.")
    exit()

# 3. Analyze durations and create the log file header
clip_durations = get_clip_durations(source_videos)
with open(log_file_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['variant_id', 'clip_filename', 'start_time', 'end_time', 'status'])

# 4. Generate the initial, ordered variant
print("--- Creating initial variant with numerical order ---")
initial_order = source_videos.copy()
variant_counter = 1
last_successful_order = combine_and_log(initial_order, f"{RUN_ID}-{variant_counter}", run_output_folder, log_file_path, clip_durations)

# 5. --- INTERACTIVE EDITING LOOP ---
while True:
    print("\n-------------------------------------------")
    print("Current clip order:")
    clip_map = {}
    for i, video_path in enumerate(last_successful_order):
        letter = chr(ord('A') + i)
        clip_map[letter] = video_path
        print(f"  {letter} - {os.path.basename(video_path)}")

    # Ask user if they want to edit
    choice = input("\nDo you want to create a new variant by editing this order? (y/n): ").lower()
    if choice != 'y':
        break

    # Get user input for swapping
    while True:
        replace_letter = input(f"Which clip to replace? (Enter a letter A-{chr(ord('A') + len(last_successful_order) - 1)}): ").upper()
        if replace_letter in clip_map:
            break
        print("Invalid letter. Please try again.")

    while True:
        with_letter = input(f"Replace it with which clip from the master list? (A-{chr(ord('A') + len(source_videos) - 1)}): ").upper()
        # Create a map for the full source list for this check
        source_map = {chr(ord('A') + i): path for i, path in enumerate(source_videos)}
        if with_letter in source_map:
            break
        print("Invalid letter. Please try again.")

    # Create the new order
    new_order = last_successful_order.copy()
    replace_index = ord(replace_letter) - ord('A')
    new_clip_path = source_map[with_letter]
    new_order[replace_index] = new_clip_path
    
    print("\n--- Creating new edited variant ---")
    variant_counter += 1
    last_successful_order = combine_and_log(new_order, f"{RUN_ID}-{variant_counter}", run_output_folder, log_file_path, clip_durations)

print("\n--- Script finished. ---")