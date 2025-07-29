# --- Version 1.501: FFmpeg Pad Filter Bug Fix ---
# Adheres to the X.YZB versioning system.
# Goal: Fixes the 'pad' filter "Invalid chars" error by splitting the
#       resolution string into separate width and height variables.

import os
import glob
import subprocess
import csv
import json
from collections import Counter
from datetime import datetime

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_VIDEO_FOLDER = os.path.join(SCRIPT_DIR, "Videos")
OUTPUT_BASE_FOLDER = os.path.join(SCRIPT_DIR, "Output")
RUN_ID = "Run_v1.501" # Using version in Run ID for clarity
LOG_FILENAME = "log.csv"
DEFAULT_FRAMERATE = "30"

# --- UTILITY FUNCTIONS (Unchanged) ---
def get_video_details(video_files):
    details = {}
    print("--- Analyzing all source video files... ---")
    for video_path in video_files:
        basename = os.path.basename(video_path)
        command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-show_entries', 'format=duration', '-of', 'json', video_path]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            details[video_path] = {'resolution': f"{data['streams'][0]['width']}x{data['streams'][0]['height']}", 'duration': float(data['format']['duration'])}
            print(f"  - Analyzed {basename} ({details[video_path]['resolution']})")
        except Exception as e:
            print(f"  WARNING: Could not analyze {basename}. Skipping. Error: {e}")
    print("--- Analysis complete. ---\n")
    return details

def format_time(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}.{sec:02d}.{millis:03d}"

# --- UPDATED in v1.501: The combine function with the DEFINITIVE FIX ---
def combine_and_log(video_order, variant_id, run_output_folder, log_file_path, clip_details, target_resolution):
    output_filename = f"variant_{variant_id.split('-')[1]}.mp4"
    final_video_path = os.path.join(run_output_folder, output_filename)
    
    # --- FIX in v1.501: Split resolution string for the pad filter ---
    try:
        target_width, target_height = target_resolution.split('x')
    except ValueError:
        print(f"FATAL ERROR: Invalid target_resolution format '{target_resolution}'. Must be 'WIDTHxHEIGHT'.")
        return None # Stop this function

    ffmpeg_command = ['ffmpeg', '-y']
    for video_path in video_order:
        ffmpeg_command.extend(['-i', video_path])

    filter_complex_parts = []
    video_outputs_for_concat = []
    audio_outputs_for_concat = []

    for i in range(len(video_order)):
        video_out_stream = f"[v{i}]"
        # The pad filter now uses the separated width and height variables. This is the fix.
        filter_complex_parts.append(
            f"[{i}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={DEFAULT_FRAMERATE}{video_out_stream}"
        )
        video_outputs_for_concat.append(video_out_stream)
        audio_outputs_for_concat.append(f"[{i}:a]")

    filter_complex_parts.append(f"{''.join(video_outputs_for_concat)}concat=n={len(video_order)}:v=1:a=0[outv]")
    filter_complex_parts.append(f"{''.join(audio_outputs_for_concat)}concat=n={len(video_order)}:v=0:a=1[outa]")
    
    final_filter_string = ";".join(filter_complex_parts)
    
    ffmpeg_command.extend(['-filter_complex', final_filter_string])
    ffmpeg_command.extend(['-map', '[outv]', '-map', '[outa]', '-c:v', 'libx264', '-c:a', 'aac', '-movflags', '+faststart'])
    ffmpeg_command.append(final_video_path)
    
    print("\nCombining and re-encoding videos. This may take longer...")
    status = "Success"
    try:
        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print(f"✅ SUCCESS: Saved {output_filename}")
    except subprocess.CalledProcessError as e:
        status = "Failed"
        print(f"❌ ERROR combining video. FFmpeg failed.")
        error_log_path = os.path.join(run_output_folder, "error_log.txt")
        with open(error_log_path, 'a') as err_f:
            err_f.write(f"--- ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            err_f.write(f"Variant ID: {variant_id}\nFailed Command:\n{' '.join(ffmpeg_command)}\n\nFFmpeg Output:\n{e.stderr}\n--------------------------------------------------\n\n")
        print(f"📄 A detailed report has been saved to: {error_log_path}")
    
    with open(log_file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        current_time = 0.0
        for video_path in video_order:
            duration = clip_details.get(video_path, {}).get('duration', 0.0)
            writer.writerow([variant_id, os.path.basename(video_path), format_time(current_time), format_time(current_time + duration), status])
            current_time += duration
    # Return None on failure so the main loop can stop
    return video_order if status == "Success" else None

# --- SCRIPT START (The main interactive loop is unchanged) ---
print("--- Starting Script v1.501 ---")
run_output_folder = os.path.join(OUTPUT_BASE_FOLDER, RUN_ID)
os.makedirs(run_output_folder, exist_ok=True)
source_videos = sorted(glob.glob(os.path.join(INPUT_VIDEO_FOLDER, "*.mp4")))
if not source_videos:
    print("\nERROR: No .mp4 files found. Exiting.")
    exit()
video_details = get_video_details(source_videos)
if not video_details:
    print("\nERROR: Could not analyze any video files. Exiting.")
    exit()
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
log_file_path = os.path.join(run_output_folder, LOG_FILENAME)
with open(log_file_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['variant_id', 'clip_filename', 'start_time', 'end_time', 'status'])
print("--- Creating initial variant with numerical order ---")
initial_order = list(video_details.keys())
variant_counter = 1
last_successful_order = combine_and_log(initial_order, f"{RUN_ID}-1", run_output_folder, log_file_path, video_details, target_resolution)
if last_successful_order is None:
    print("Stopping script due to a fatal error during the initial video combination.")
    exit()
while True:
    print("\n-------------------------------------------")
    print("Current clip order:")
    clip_map = {chr(ord('A') + i): path for i, path in enumerate(last_successful_order)}
    for letter, path in clip_map.items():
        print(f"  {letter} - {os.path.basename(path)}")
    choice = input("\nCreate a new variant by editing this order? (y/n): ").lower()
    if choice != 'y':
        break
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
    if last_successful_order is None:
        print("Stopping interactive session due to a fatal error during video combination.")
        break
print("\n--- Script finished. ---")