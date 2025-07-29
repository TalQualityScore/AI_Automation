# --- Version 1.700: Visual Coordinate Picker ---
# Goal: A simple GUI to load a video, display its first frame,
#       and report the (x, y) coordinates of mouse clicks.

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import subprocess
import os

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_FRAME_FILENAME = "_temp_frame.png" # A temporary file for the screenshot

class VisualLayoutTool:
    def __init__(self, root):
        """Initializes the GUI application."""
        self.root = root
        self.root.title("Visual Layout Tool v1.700")
        
        # --- GUI Widgets ---
        # A frame to hold the main content
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=10, pady=10)

        # Button to load a video
        self.load_button = tk.Button(self.main_frame, text="Load Video", command=self.load_video)
        self.load_button.pack(pady=5)
        
        # Canvas to display the video frame
        self.canvas = tk.Canvas(self.main_frame, background="grey", width=600, height=800)
        self.canvas.pack(pady=5)
        
        # Label to show the coordinates
        self.coords_label = tk.Label(self.main_frame, text="Click on the frame to get coordinates", font=("Arial", 12))
        self.coords_label.pack(pady=5)
        
        # --- Event Binding ---
        # This tells the canvas to call the on_canvas_click method when it's clicked
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # A variable to hold the image so it doesn't get garbage-collected
        self.photo_image = None

    def load_video(self):
        """Opens a file dialog to select a video and then displays its first frame."""
        # Open file dialog, starting in the 'Videos' folder
        initial_dir = os.path.join(SCRIPT_DIR, "Videos")
        filepath = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select a Video File",
            filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*"))
        )
        
        # If the user selected a file (didn't cancel)
        if filepath:
            print(f"Loading video: {filepath}")
            self.extract_and_display_frame(filepath)

    def extract_and_display_frame(self, video_path):
        """Uses FFmpeg to extract the first frame and displays it on the canvas."""
        output_frame_path = os.path.join(SCRIPT_DIR, TEMP_FRAME_FILENAME)
        
        # FFmpeg command to grab exactly one frame from the beginning
        command = [
            'ffmpeg',
            '-y',           # Overwrite the temp file if it exists
            '-i', video_path,
            '-vframes', '1', # Get only one frame
            output_frame_path
        ]
        
        print("Extracting first frame with FFmpeg...")
        try:
            # We run FFmpeg hidden, as we don't need to see its output
            subprocess.run(command, check=True, capture_output=True)
            print("Frame extracted successfully.")
        except subprocess.CalledProcessError as e:
            print("❌ ERROR: FFmpeg failed to extract frame.")
            print(e.stderr.decode())
            self.coords_label.config(text="Error: Could not extract frame from video.")
            return
            
        # --- Display the extracted frame using Pillow and Tkinter ---
        try:
            # Open the image with Pillow
            img = Image.open(output_frame_path)
            
            # Update the canvas size to match the image
            self.canvas.config(width=img.width, height=img.height)
            
            # Convert the Pillow image to a Tkinter-compatible image
            self.photo_image = ImageTk.PhotoImage(img)
            
            # Clear the canvas and draw the new image
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
            
            self.coords_label.config(text="Video frame loaded. Click to get coordinates.")
            
        except Exception as e:
            print(f"❌ ERROR: Failed to display image. Reason: {e}")
            self.coords_label.config(text="Error: Could not display the extracted frame.")

    def on_canvas_click(self, event):
        """Handles mouse clicks on the canvas."""
        x, y = event.x, event.y
        # Update the label in the GUI
        self.coords_label.config(text=f"Coordinates: (x={x}, y={y})")
        # Print to the console for a clear log
        print(f"Click detected at: (x={x}, y={y})")


# --- Main execution block ---
if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    # Create an instance of our application
    app = VisualLayoutTool(root)
    # Start the GUI event loop
    root.mainloop()