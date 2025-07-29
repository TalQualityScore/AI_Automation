# --- Checkpoint Version 1.3: Normalizing Interactive Editor ---
# Goal: Solves the mixed-resolution problem. It now re-encodes video to a
#       standard format (e.g., 1080x1920), adding black bars as needed.
#       This will be SLOWER but much more reliable.

import os
import glob
import subprocess
import csv

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_VIDEO_FOLDER = os.path.join(SCRIPT_DIR, "Videos")
OUTPUT_BASE_FOLDER = os.path.join(SCRIPT_DIR, "Output")
RUN_ID = "Run_004" # New run ID for this test
LOG_FILENAME = "log.csv"

# --- NEW in v1.3: Define our target video format ---
TARGET_RESOLUTION = "1080x1920" # Vertical HD (Width x Height)
TARGET_FRAMERATE = "30"

# --- UTILITY FUNCTIONS ---

def get_clip_durations(video_files):
    # This function is unchanged
    durations = {}
    for video_path in video_files:
        command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            durations[video_path] = float(result.stdout)
        except Exception:
            durations[video_path] = 0.0
    return durations

def format_time(seconds):
    # This function is unchanged
    millis = int((seconds - int(seconds)) * 1000)
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}.{millis:03d}"

# --- UPDATED in v1.3: The main combine and log function ---
def combine_and_log(video_order, variant_id, run_output_folder, log_file_path, clip_durations):
    """
    Combines videos by re-encoding them to a standard format. This is slower
    but handles mixed resolutions correctly.
    """
    output_filename = f"variant_{variant_id.split('-')[1]}.mp4"
    final_video_path = os.path.join(run_output_folder, output_filename)
    
    # --- This is the new, more complex FFmpeg command generation ---
    ffmpeg_command = ['ffmpeg', '-y']
    
    # 1. Add all video clips as inputs
    for video_path in video_order:
        ffmpeg_command.extend(['-i', video_path])

    # 2. Build the complex filter graph string
    filter_complex = []
    video_streams = []
    audio_streams = []

    for i in range(len(video_order)):
        # For each input, create a normalized video stream and an audio stream
        # [0:v] means video stream from the first input file
        # scale and pad filters ensure everything fits the TARGET_RESOLUTION
        video_stream_name = f"[v{i}]"
        audio_stream_name = f"[a{i}]"
        
        # Scale the video to fit within the target dimensions, keeping aspect ratio.
        # Then, pad with black bars to fill the rest of the space.
        filter_complex.append(
            f"[{i}:v]scale={TARGET_RESOLUTION}:force_original_aspect_ratio=decrease,pad={TARGET_RESOLUTION}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={TARGET_FRAMERATE}[{video_stream_name}]"
        )
        filter_complex.append(f"[{i}:a]{audio_stream_name}")
        
        video_streams.append(video_stream_name)
        audio_streams.append(audio_stream_name)

    # 3. Concatenate (join) all the normalized streams together
    filter_complex.append(f"{''.join(video_streams)}concat=n={len(video_order)}:v=1[outv]")
    filter_complex.append(f"{''.join(audio_streams)}concat=n={len(video_order)}:v=0:a=1[outa]")

    ffmpeg_command.extend(['-filter_complex', ";".join(filter_complex)])
    ffmpeg_command.extend(['-map', '[outv]', '-map', '[outa]'])
    
    # Use a high-quality, widely compatible codec
    ffmpeg_command.extend(['-c:v', 'libx264', '-c:a', 'aac', '-movflags', '+faststart'])
    
    ffmpeg_command.append(final_video_path)
    
    print("\nCombining and re-encoding videos. This may take longer...")
    try:
        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print(f"✅ SUCCESS: Saved {output_filename}")
        status = "Success"
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR combining video. FFmpeg failed.")
        print(f"FFmpeg Error Output:\n{e.stderr}")
        status = "Failed"
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        status = "Failed"
    
    # Append detailed log (this part is unchanged)
    with open(log_file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        current_time = 0.0
        for video_path in video_order:
            duration = clip_durations.get(video_path, 0.0)
            start_time_str = format_time(current_time)
            end_time_str = format_time(current_time + duration)
            writer.writerow([variant_id, os.path.basename(video_path), start_time_str, end_time_str, status])
            current_time += duration
    return video_order


# --- SCRIPT START (The main interactive loop is unchanged) ---
print("--- Starting Normalizing Interactive Editor (v1.3) ---")
# ... (The rest of the script is identical to v1.2)
run_output_folder = os.path.join(OUTPUT_BASE_FOLDER, RUN_ID)
os.makedirs(run_output_folder, exist_ok=True)
log_file_path = os.path.join(run_output_folder, LOG_FILENAME)
source_videos = sorted(glob.glob(os.path.join(INPUT_VIDEO_FOLDER, "*.mp4")))
if not source_videos:
    print("\nERROR: No .mp4 files found. Exiting.")
    exit()
clip_durations = get_clip_durations(source_videos)
with open(log_file_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['variant_id', 'clip_filename', 'start_time', 'end_time', 'status'])
print("--- Creating initial variant with numerical order ---")
initial_order = source_videos.copy()
variant_counter = 1
last_successful_order = combine_and_log(initial_order, f"{RUN_ID}-{variant_counter}", run_output_folder, log_file_path, clip_durations)
while True:
    print("\n-------------------------------------------")
    print("Current clip order:")
    clip_map = {}
    for i, video_path in enumerate(last_successful_order):
        letter = chr(ord('A') + i)
        clip_map[letter] = video_path
        print(f"  {letter} - {os.path.basename(video_path)}")
    choice = input("\nDo you want to create a new variant by editing this order? (y/n): ").lower()
    if choice != 'y':
        break
    while True:
        replace_letter = input(f"Which clip to replace? (Enter a letter A-{chr(ord('A') + len(last_successful_order) - 1)}): ").upper()
        if replace_letter in clip_map:
            break
        print("Invalid letter. Please try again.")
    while True:
        with_letter = input(f"Replace it with which clip from the master list? (A-{chr(ord('A') + len(source_videos) - 1)}): ").upper()
        source_map = {chr(ord('A') + i): path for i, path in enumerate(source_videos)}
        if with_letter in source_map:
            break
        print("Invalid letter. Please try again.")
    new_order = last_successful_order.copy()
    replace_index = ord(replace_letter) - ord('A')
    new_clip_path = source_map[with_letter]
    new_order[replace_index] = new_clip_path
    print("\n--- Creating new edited variant ---")
    variant_counter += 1
    last_successful_order = combine_and_log(new_order, f"{RUN_ID}-{variant_counter}", run_output_folder, log_file_path, clip_durations)
print("\n--- Script finished. ---")