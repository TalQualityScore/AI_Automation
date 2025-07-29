# --- Checkpoint Version 1.4: Smart Format Selector ---
# Goal: Auto-detects video resolutions. If multiple formats are found,
#       it asks the user to choose a master format for the project.
#       This makes the script flexible for any type of ad campaign.
# NOTE: We do not need external programs like Premiere. FFmpeg is our engine.

import os
import glob
import subprocess
import csv
import json
from collections import Counter

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_VIDEO_FOLDER = os.path.join(SCRIPT_DIR, "Videos")
OUTPUT_BASE_FOLDER = os.path.join(SCRIPT_DIR, "Output")
RUN_ID = "Run_005"
LOG_FILENAME = "log.csv"
DEFAULT_FRAMERATE = "30" # A sensible default if not specified elsewhere.

# --- UTILITY FUNCTIONS ---

def get_video_details(video_files):
    """Uses ffprobe to get resolution and duration for each video file."""
    details = {}
    print("--- Analyzing all source video files... ---")
    for video_path in video_files:
        basename = os.path.basename(video_path)
        command = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height', '-show_entries', 'format=duration',
            '-of', 'json', video_path
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            width = data['streams'][0]['width']
            height = data['streams'][0]['height']
            duration = float(data['format']['duration'])
            details[video_path] = {
                'resolution': f"{width}x{height}",
                'duration': duration
            }
            print(f"  - Analyzed {basename} ({width}x{height})")
        except Exception as e:
            print(f"  WARNING: Could not analyze {basename}. Skipping. Error: {e}")
    print("--- Analysis complete. ---\n")
    return details

def format_time(seconds):
    # Unchanged
    millis = int((seconds - int(seconds)) * 1000)
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}.{millis:03d}"

# --- UPDATED in v1.4: Accepts target_resolution as a parameter ---
def combine_and_log(video_order, variant_id, run_output_folder, log_file_path, clip_details, target_resolution):
    # This function is now more flexible, receiving the target format.
    output_filename = f"variant_{variant_id.split('-')[1]}.mp4"
    final_video_path = os.path.join(run_output_folder, output_filename)
    
    ffmpeg_command = ['ffmpeg', '-y']
    for video_path in video_order:
        ffmpeg_command.extend(['-i', video_path])

    filter_complex = []
    video_streams, audio_streams = [], []
    for i in range(len(video_order)):
        video_stream_name, audio_stream_name = f"[v{i}]", f"[a{i}]"
        filter_complex.append(
            f"[{i}:v]scale={target_resolution}:force_original_aspect_ratio=decrease,pad={target_resolution}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={DEFAULT_FRAMERATE}[{video_stream_name}]"
        )
        filter_complex.append(f"[{i}:a]{audio_stream_name}")
        video_streams.append(video_stream_name)
        audio_streams.append(audio_stream_name)

    filter_complex.append(f"{''.join(video_streams)}concat=n={len(video_order)}:v=1[outv]")
    filter_complex.append(f"{''.join(audio_streams)}concat=n={len(video_order)}:v=0:a=1[outa]")

    ffmpeg_command.extend(['-filter_complex', ";".join(filter_complex)])
    ffmpeg_command.extend(['-map', '[outv]', '-map', '[outa]', '-c:v', 'libx264', '-c:a', 'aac', '-movflags', '+faststart'])
    ffmpeg_command.append(final_video_path)
    
    print("\nCombining and re-encoding videos. This may take longer...")
    try:
        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print(f"✅ SUCCESS: Saved {output_filename}")
        status = "Success"
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR combining video. FFmpeg failed.\nFFmpeg Error: {e.stderr}")
        status = "Failed"
    
    with open(log_file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        current_time = 0.0
        for video_path in video_order:
            duration = clip_details.get(video_path, {}).get('duration', 0.0)
            start_time_str = format_time(current_time)
            end_time_str = format_time(current_time + duration)
            writer.writerow([variant_id, os.path.basename(video_path), start_time_str, end_time_str, status])
            current_time += duration
    return video_order

# --- SCRIPT START ---
print("--- Starting Smart Format Selector Script (v1.4) ---")

# 1. Find videos and get their details
source_videos = sorted(glob.glob(os.path.join(INPUT_VIDEO_FOLDER, "*.mp4")))
if not source_videos:
    print("\nERROR: No .mp4 files found. Exiting.")
    exit()

video_details = get_video_details(source_videos)
if not video_details:
    print("\nERROR: Could not analyze any video files. Exiting.")
    exit()

# --- NEW in v1.4: The Smart Format Selector Logic ---
all_resolutions = [details['resolution'] for details in video_details.values()]
resolution_counts = Counter(all_resolutions)
unique_resolutions = list(resolution_counts.keys())

target_resolution = ""
if len(unique_resolutions) == 1:
    target_resolution = unique_resolutions[0]
    print(f"All videos have the same format. Auto-selecting {target_resolution} as the project format.\n")
else:
    print("Multiple video resolutions found. Please choose the master format for this project.")
    for i, res in enumerate(unique_resolutions):
        count = resolution_counts[res]
        print(f"  {i+1}. {res} (used by {count} clip{'s' if count > 1 else ''})")
    
    while True:
        try:
            choice = int(input("\nEnter the number for your choice: "))
            if 1 <= choice <= len(unique_resolutions):
                target_resolution = unique_resolutions[choice - 1]
                print(f"You chose {target_resolution}. All clips will be scaled to fit this format.\n")
                break
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# 3. Setup paths and log file
run_output_folder = os.path.join(OUTPUT_BASE_FOLDER, RUN_ID)
os.makedirs(run_output_folder, exist_ok=True)
log_file_path = os.path.join(run_output_folder, LOG_FILENAME)
with open(log_file_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['variant_id', 'clip_filename', 'start_time', 'end_time', 'status'])

# 4. Generate the initial, ordered variant using the CHOSEN format
print("--- Creating initial variant with numerical order ---")
initial_order = list(video_details.keys()) # Use the analyzed list to ensure we only use valid clips
variant_counter = 1
last_successful_order = combine_and_log(initial_order, f"{RUN_ID}-{variant_counter}", run_output_folder, log_file_path, video_details, target_resolution)

# 5. Interactive loop (unchanged, but now uses the chosen target_resolution)
while True:
    print("\n-------------------------------------------")
    print("Current clip order:")
    clip_map = {chr(ord('A') + i): path for i, path in enumerate(last_successful_order)}
    for letter, path in clip_map.items():
        print(f"  {letter} - {os.path.basename(path)}")

    choice = input("\nCreate a new variant by editing this order? (y/n): ").lower()
    if choice != 'y':
        break
    
    # ... (rest of the interactive loop is identical to v1.3)
    while True:
        replace_letter = input(f"Which clip to replace? (A-{chr(ord('A') + len(last_successful_order) - 1)}): ").upper()
        if replace_letter in clip_map: break
        else: print("Invalid letter.")
    while True:
        with_letter = input(f"Replace it with which clip from the master list? (A-{chr(ord('A') + len(initial_order) - 1)}): ").upper()
        source_map = {chr(ord('A') + i): path for i, path in enumerate(initial_order)}
        if with_letter in source_map: break
        else: print("Invalid letter.")

    new_order = last_successful_order.copy()
    replace_index = ord(replace_letter) - ord('A')
    new_clip_path = source_map[with_letter]
    new_order[replace_index] = new_clip_path
    
    print("\n--- Creating new edited variant ---")
    variant_counter += 1
    last_successful_order = combine_and_log(new_order, f"{RUN_ID}-{variant_counter}", run_output_folder, log_file_path, video_details, target_resolution)

print("\n--- Script finished. ---")