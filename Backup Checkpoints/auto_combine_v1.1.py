# --- Checkpoint Version 1.1: Multi-Variant Randomizer Script ---
# Goal: Creates 3 different video variants by shuffling the order of source clips.
# It now uses relative paths, so it can run from anywhere as long as the
# 'Videos' and 'Output' folders are next to it.

import os
import glob
import subprocess
import csv
import random # --- NEW in v1.1: For shuffling the video order

# --- CONFIGURATION ---
# --- NEW in v1.1: Paths are now calculated automatically! ---
# The script will find the 'Videos' and 'Output' folders that are in the same directory as the script.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_VIDEO_FOLDER = os.path.join(SCRIPT_DIR, "Videos")
OUTPUT_BASE_FOLDER = os.path.join(SCRIPT_DIR, "Output")

# --- NEW in v1.1: Define how many variants to create ---
NUMBER_OF_VARIANTS = 3
RUN_ID = "Run_002" # Let's use a new Run ID for this test
LOG_FILENAME = "log.csv"

# --- SCRIPT START ---

print("--- Starting Auto-Combine Script (v1.1) ---")

# 1. Define the full path for this run's output
run_output_folder = os.path.join(OUTPUT_BASE_FOLDER, RUN_ID)

# 2. Find all .mp4 files in the input folder
print(f"Searching for .mp4 files in: {INPUT_VIDEO_FOLDER}")
source_videos = glob.glob(os.path.join(INPUT_VIDEO_FOLDER, "*.mp4"))

# 3. Check if we found any videos
if not source_videos:
    print("\nERROR: No .mp4 files found in the 'Videos' folder. Exiting.")
    exit()

print(f"\nFound {len(source_videos)} source video files.")

# 4. Create the output directory
print(f"Creating output directory: {run_output_folder}")
os.makedirs(run_output_folder, exist_ok=True)

# 5. --- NEW in v1.1: Prepare the Log File ---
# We create the log file once and write the header.
log_file_path = os.path.join(run_output_folder, LOG_FILENAME)
header = ['variant_id', 'clip_filenames_used', 'output_filename', 'status']
with open(log_file_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)

print(f"Log file created at: {log_file_path}")

# 6. --- NEW in v1.1: Loop to create each variant ---
print(f"\n--- Starting to generate {NUMBER_OF_VARIANTS} variants ---")

for i in range(NUMBER_OF_VARIANTS):
    variant_number = i + 1
    variant_id = f"{RUN_ID}-{variant_number}"
    output_variant_filename = f"variant_{variant_number:02d}.mp4" # e.g., variant_01.mp4
    final_video_path = os.path.join(run_output_folder, output_variant_filename)
    
    print(f"\n--- Processing Variant {variant_number}/{NUMBER_OF_VARIANTS} ---")

    # --- NEW in v1.1: Shuffle the list of videos for this variant ---
    # We make a copy first to not change the original list
    shuffled_videos = source_videos.copy()
    random.shuffle(shuffled_videos)

    print("Clip order for this variant:")
    shuffled_basenames = [os.path.basename(p) for p in shuffled_videos]
    print(f"  -> {' -> '.join(shuffled_basenames)}")
    
    # Create the temporary file list for FFmpeg for this specific order
    temp_list_filename = os.path.join(run_output_folder, f"filelist_temp_{variant_number}.txt")
    with open(temp_list_filename, 'w') as f:
        for video_path in shuffled_videos:
            f.write(f"file '{video_path.replace(os.sep, '/')}'\n")

    # Build and run the FFmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-y', # Overwrite output file if it exists
        '-f', 'concat',
        '-safe', '0',
        '-i', temp_list_filename,
        '-c', 'copy',
        final_video_path
    ]

    export_status = "Success"
    try:
        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print(f"✅ SUCCESS: Saved {output_variant_filename}")
    except FileNotFoundError:
        print("\n❌ ERROR: FFmpeg command not found.")
        export_status = "Failed - FFmpeg not found"
        break # Stop the loop if ffmpeg isn't found
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR: FFmpeg failed for {output_variant_filename}.")
        print(f"FFmpeg error: {e.stderr}")
        export_status = f"Failed - FFmpeg error"

    # Clean up the temporary file for this variant
    os.remove(temp_list_filename)
    
    # --- NEW in v1.1: Append the result to the log file ---
    with open(log_file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        data_row = [
            variant_id,
            ",".join(shuffled_basenames),
            output_variant_filename,
            export_status
        ]
        writer.writerow(data_row)

print("\n--- Script finished. ---")