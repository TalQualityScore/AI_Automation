# --- File: app/src/naming_generator.py ---
import re
import os
import subprocess
import sys
import time
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from unidecode import unidecode
import io

def load_api_key():
    """Loads the Gemini API key from the .env file in the project root."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path=dotenv_path)
    return os.getenv("GEMINI_API_KEY")

def parse_filename_for_folder(filename):
    """Parses only the parts needed for the main project folder name."""
    base_name = os.path.splitext(filename)[0].replace("Copy of OO_", "")
    ad_type_match = re.search(r'(VTD|STOR|ACT)', base_name)
    ad_type = ad_type_match.group(1) if ad_type_match else ""
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', base_name)
    test_name = test_name_match.group(1) if test_name_match else ""
    return {"ad_type": ad_type, "test_name": test_name}

def generate_project_folder_name(project_name, first_client_video, ad_type_selection):
    """Generates the main output folder name."""
    parts = parse_filename_for_folder(os.path.basename(first_client_video))
    ad_type_cased = ad_type_selection.upper() if ad_type_selection.lower() != 'quiz' else 'Quiz'
    return f"GH {project_name} {parts['ad_type']} {parts['test_name']} {ad_type_cased}"

def generate_output_name(project_name, first_client_video, ad_type_selection, image_desc, version_num):
    """Generates the final stitched video filename."""
    base_name = os.path.splitext(os.path.basename(first_client_video))[0].replace("Copy of OO_", "")
    
    ad_type_match = re.search(r'(VTD|STOR|ACT)', base_name)
    ad_type = ad_type_match.group(1) if ad_type_match else ""
    test_name_match = re.search(r'(?:VTD|STOR|ACT)-(\d+)', base_name)
    test_name = test_name_match.group(1) if test_name_match else ""
    version_letter_match = re.search(r'\d+([A-Z])$', base_name)
    version_letter = version_letter_match.group(1) if version_letter_match else ""

    part1 = "GH"
    part2 = unidecode(project_name).lower().replace(" ", "")
    part3 = ad_type
    part4 = f"{test_name}{version_letter}"
    part5 = ad_type_selection
    part6 = image_desc.lower().replace(" ", "").replace("_", "")
    part7 = f"v{version_num:02d}"
    part8, part9, part10 = "m00", "f00", "c00"
    
    name_part = f"{part1}-{part2}{part3}{part4}ZZ{part5}"
    version_part = f"{part7}-{part8}-{part9}-{part10}"
    
    return f"{name_part}_{part6}-{version_part}"

def get_image_description(video_path, api_key):
    """
    Gets image description from Gemini API with automatic retry on rate limit errors.
    """
    temp_dir = "temp_downloads" # A temporary directory for frame extraction
    os.makedirs(temp_dir, exist_ok=True)
    temp_image_path = os.path.join(temp_dir, f"temp_frame_{os.path.basename(video_path)}.jpg")
    
    try:
        command = ['ffmpeg', '-i', video_path, '-vframes', '1', '-q:v', '2', '-y', temp_image_path]
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(command, check=True, capture_output=True, text=True, startupinfo=startupinfo)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"FFmpeg error extracting frame: {e}")
        return "ffmpegerror"

    if not api_key:
        return "noapikey"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = "Analyze the visual elements, style, and subject of this image, ignoring any text. Describe the scene in one or two combined words (e.g., 'squeezebottle', 'womanoutside', 'vintagewoman'), all lowercase, with no spaces."
    
    # FIX: Implement automatic retry with exponential backoff for API calls
    max_retries = 5
    delay = 1.0 # Initial delay in seconds
    for attempt in range(max_retries):
        try:
            with open(temp_image_path, 'rb') as f:
                image_bytes = f.read()
            img = Image.open(io.BytesIO(image_bytes))
            
            response = model.generate_content([prompt, img])
            description = response.text.strip().replace(" ", "")
            
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            
            return description

        except Exception as e:
            # Check if it's a rate limit error (often includes '429')
            if '429' in str(e):
                print(f"Rate limit hit. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
                delay *= 2 # Double the delay for the next attempt
                continue
            else:
                print(f"An unexpected API error occurred: {e}")
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
                return "apifail"
    
    print("API call failed after multiple retries.")
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)
    return "apifail"
