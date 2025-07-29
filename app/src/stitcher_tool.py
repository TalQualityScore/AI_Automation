# --- File: app/src/stitcher_tool.py ---
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import sys
import threading
import shutil
from . import naming_generator

class StitcherTool:
    def __init__(self, root, back_callback):
        self.root = root
        self.back_callback = back_callback
        self.frame = ttk.Frame(root, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.frame.columnconfigure(0, weight=1)

        # Initialize state variables
        self.sequences = []
        self.tag_colors = ["#2E86C1", "#AF7AC5", "#E67E22", "#52BE80", "#F39C12"]
        self.last_color_index = 0
        self.api_key = naming_generator.load_api_key()
        self.project_name_var = tk.StringVar()
        self.ad_type_var = tk.StringVar(value="quiz")
        
        self.setup_ui()
        self.reset_tool()

    def setup_ui(self):
        selection_frame = ttk.Frame(self.frame)
        selection_frame.grid(row=0, column=0, sticky="ew")
        selection_frame.columnconfigure(0, weight=1)
        selection_frame.columnconfigure(1, weight=1)

        client_frame = ttk.LabelFrame(selection_frame, text="Step 1: Add Client Files", style="Step.TLabelframe", padding="10")
        client_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        client_frame.columnconfigure(0, weight=1)
        ttk.Button(client_frame, text="Browse Files...", command=self.browse_client_videos, width=20).pack()

        template_frame = ttk.LabelFrame(selection_frame, text="Step 2: Add Template Videos", style="Step.TLabelframe", padding="10")
        template_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        template_frame.columnconfigure(0, weight=1)
        ttk.Button(template_frame, text="Browse Files to Add...", command=self.browse_template_videos, width=20).pack()

        self.sequences_frame = ttk.LabelFrame(self.frame, text="Step 3: Review and Edit Sequences", style="Step.TLabelframe", padding="10")
        self.sequences_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        self.sequences_frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)

        config_frame = ttk.Frame(self.frame)
        config_frame.grid(row=3, column=0, sticky="ew")
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1)

        project_name_frame = ttk.LabelFrame(config_frame, text="Step 4: Enter Project Name", style="Step.TLabelframe", padding="10")
        project_name_frame.grid(row=0, column=0, sticky="ew", padx=(0,5))
        ttk.Entry(project_name_frame, textvariable=self.project_name_var, width=40).pack(fill=tk.X)

        ad_type_frame = ttk.LabelFrame(config_frame, text="Step 5: Select Ad Type", style="Step.TLabelframe", padding="10")
        ad_type_frame.grid(row=0, column=1, sticky="ew", padx=(5,0))
        ttk.Radiobutton(ad_type_frame, text="VSL", variable=self.ad_type_var, value="VSL").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(ad_type_frame, text="SVSL", variable=self.ad_type_var, value="SVSL").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(ad_type_frame, text="Quiz", variable=self.ad_type_var, value="quiz").pack(side=tk.LEFT, padx=10)

        action_frame = ttk.LabelFrame(self.frame, text="Step 6: Actions", style="Step.TLabelframe", padding="10")
        action_frame.grid(row=4, column=0, sticky="ew", pady=10)
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        
        self.export_button = ttk.Button(action_frame, text="Export All Videos", command=self.export_videos)
        self.export_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.reset_button = ttk.Button(action_frame, text="New / Reset", command=self.reset_tool, style="Reset.TButton")
        self.reset_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        style = ttk.Style()
        style.configure("Reset.TButton", foreground="red")
        
    def reset_tool(self):
        self.sequences = []
        self.last_color_index = 0
        self.project_name_var.set("")
        self.ad_type_var.set("quiz")
        self.update_sequences_display()
        if hasattr(self, 'export_button'):
            self.export_button.config(state=tk.NORMAL, text="Export All Videos")
        print("Stitcher tool has been reset.")

    def browse_client_videos(self):
        file_paths = filedialog.askopenfilenames(title="Select Client Video Files", filetypes=[("Video Files", "*.mp4 *.mov")])
        if not file_paths: return
        new_sequences = [{'client': path, 'templates': []} for path in file_paths]
        self.sequences.extend(new_sequences)
        self.update_sequences_display()

    def browse_template_videos(self):
        if not self.sequences:
            messagebox.showerror("Error", "Please select client videos first.")
            return
        file_paths = filedialog.askopenfilenames(title="Select Template Videos to Add", filetypes=[("Video Files", "*.mp4 *.mov")])
        if not file_paths: return
        for path in file_paths:
            color = self.tag_colors[self.last_color_index % len(self.tag_colors)]
            self.last_color_index += 1
            for seq in self.sequences:
                seq['templates'].append({'path': path, 'color': color})
        self.update_sequences_display()

    def update_sequences_display(self):
        for widget in self.sequences_frame.winfo_children(): widget.destroy()
        if not self.sequences:
            ttk.Label(self.sequences_frame, text="Select client videos to see the stitching plan.", style="Placeholder.TLabel").pack(pady=20)
            return
        
        canvas = tk.Canvas(self.sequences_frame, bg="#1c1c1c", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.sequences_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for seq in self.sequences:
            row_frame = ttk.Frame(scrollable_frame, padding=(0, 5))
            row_frame.pack(fill=tk.X, pady=2)
            client_name = os.path.splitext(os.path.basename(seq['client']))[0]
            self.create_video_tag(row_frame, client_name, "#85929E", seq, is_template=False)
            ttk.Label(row_frame, text="→", style="Arrow.TLabel").pack(side=tk.LEFT, padx=5)
            for template in seq['templates']:
                template_name = os.path.splitext(os.path.basename(template['path']))[0]
                self.create_video_tag(row_frame, template_name, template['color'], seq, is_template=True, template_obj=template)

    def create_video_tag(self, parent, name, color, sequence, is_template, template_obj=None):
        tag_frame = tk.Frame(parent, bg=color, relief="raised", borderwidth=1)
        tag_frame.pack(side=tk.LEFT, padx=3, pady=3)
        if is_template:
            left_btn = tk.Label(tag_frame, text="◀", bg=color, fg="white", cursor="hand2"); left_btn.pack(side=tk.LEFT, padx=(3,0))
            left_btn.bind("<Button-1>", lambda e, s=sequence, t=template_obj: self.reorder_template(s, t, -1))
        ttk.Label(tag_frame, text=name, background=color, foreground="white", padding=(5, 3)).pack(side=tk.LEFT)
        if is_template:
            remove_btn = tk.Label(tag_frame, text="X", bg=color, fg="white", cursor="hand2", font=("Arial", 8, "bold")); remove_btn.pack(side=tk.LEFT, padx=(0, 5))
            remove_btn.bind("<Button-1>", lambda e, s=sequence, t=template_obj: self.remove_template_from_sequence(s, t))
            right_btn = tk.Label(tag_frame, text="▶", bg=color, fg="white", cursor="hand2"); right_btn.pack(side=tk.LEFT, padx=(0,3))
            right_btn.bind("<Button-1>", lambda e, s=sequence, t=template_obj: self.reorder_template(s, t, 1))

    def remove_template_from_sequence(self, sequence, template_to_remove):
        sequence['templates'].remove(template_to_remove)
        self.update_sequences_display()
        
    def reorder_template(self, sequence, template_obj, direction):
        try:
            old_index = sequence['templates'].index(template_obj)
        except ValueError: return
        new_index = old_index + direction
        if 0 <= new_index < len(sequence['templates']):
            sequence['templates'].pop(old_index)
            sequence['templates'].insert(new_index, template_obj)
        self.update_sequences_display()

    def export_videos(self):
        if not self.sequences:
            messagebox.showerror("Error", "Please select client videos first.")
            return
        project_name = self.project_name_var.get()
        if not project_name:
            messagebox.showerror("Error", "Please enter a Project Name.")
            return
        output_parent_folder = filedialog.askdirectory(title="Select Parent Folder for Export")
        if not output_parent_folder: return

        self.export_button.config(state=tk.DISABLED, text="Exporting...")
        self.reset_button.config(state=tk.DISABLED)
        progress_bar = ttk.Progressbar(self.frame, orient='horizontal', mode='determinate', length=300)
        progress_bar.grid(row=5, column=0, sticky="ew", pady=10)
        
        export_thread = threading.Thread(target=self.run_export_process, args=(output_parent_folder, project_name, progress_bar))
        export_thread.start()

    # --- MODIFIED: Switched to a fully standardized, robust concat filter method ---
    def run_export_process(self, output_parent_folder, project_name, progress_bar):
        temp_dir = ""
        try:
            folder_name = naming_generator.generate_project_folder_name(project_name, self.sequences[0]['client'], self.ad_type_var.get())
            project_folder = os.path.join(output_parent_folder, folder_name)
            
            subfolders = { "audio": "_Audio", "copy": "_Copy", "footage": "_Footage", "thumbs": "_Thumbnails", "ame": "_AME" }
            audio_sub = ["Music", "SFX", "Source", "VO"]
            footage_sub = ["Images", "PSD", "Vector", "Video"]
            video_sub = ["Client", "Quality Score", "Rendered", "Stock"]

            for key, folder in subfolders.items(): os.makedirs(os.path.join(project_folder, folder), exist_ok=True)
            for sub in audio_sub: os.makedirs(os.path.join(project_folder, subfolders["audio"], sub), exist_ok=True)
            for sub in footage_sub: os.makedirs(os.path.join(project_folder, subfolders["footage"], sub), exist_ok=True)
            for sub in video_sub: os.makedirs(os.path.join(project_folder, subfolders["footage"], "Video", sub), exist_ok=True)
            
            output_folder = os.path.join(project_folder, subfolders["ame"])
            client_copy_folder = os.path.join(project_folder, subfolders["footage"], "Video", "Client")
            temp_dir = os.path.join(project_folder, "_temp_stitcher")
            os.makedirs(temp_dir, exist_ok=True)
            
            progress_bar['maximum'] = len(self.sequences)

            for i, seq in enumerate(self.sequences):
                client_path = seq['client']
                shutil.copy(client_path, client_copy_folder)
                
                image_desc = naming_generator.get_image_description(client_path, temp_dir, self.api_key)
                output_name = naming_generator.generate_output_name(project_name, client_path, self.ad_type_var.get(), image_desc, i + 1)
                output_path = os.path.join(output_folder, f"{output_name}.mp4")

                video_list = [client_path] + [t['path'] for t in seq['templates']]
                
                command = ['ffmpeg', '-y']
                filter_complex_parts = []
                concat_inputs = ""
                
                # Define a universal standard for all clips
                target_width, target_height = 1080, 1920
                target_fps = 30
                target_audio_rate = 44100
                
                for j, video_path in enumerate(video_list):
                    command.extend(['-i', video_path])
                    # Standardize each video and audio stream
                    filter_complex_parts.append(
                        f"[{j}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
                        f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,"
                        f"setsar=1,fps={target_fps},setpts=PTS-STARTPTS[v{j}];"
                    )
                    filter_complex_parts.append(
                        f"[{j}:a]aformat=sample_rates={target_audio_rate}:channel_layouts=stereo,"
                        f"asetpts=PTS-STARTPTS[a{j}];"
                    )
                    concat_inputs += f"[v{j}][a{j}]"

                filter_complex = "".join(filter_complex_parts) + \
                                 f"{concat_inputs}concat=n={len(video_list)}:v=1:a=1[outv][outa]"
                
                command.extend([
                    '-filter_complex', filter_complex,
                    '-map', '[outv]', '-map', '[outa]',
                    '-c:v', 'libx264', '-c:a', 'aac'
                ])
                command.append(output_path)
                
                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                subprocess.run(command, check=True, capture_output=True, text=True, startupinfo=startupinfo)
                progress_bar['value'] = i + 1
                self.root.update_idletasks()

            messagebox.showinfo("Success", f"Export complete! Project folder created at:\n{project_folder}")
            self.reset_tool()

        except FileNotFoundError:
            messagebox.showerror("FFmpeg Error", "FFmpeg not found. Please ensure FFmpeg is installed in your system's PATH.")
        except subprocess.CalledProcessError as e:
            error_details = f"FFmpeg command failed.\n\nError:\n{e.stderr}"
            print(error_details)
            messagebox.showerror("FFmpeg Error", error_details)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
        finally:
            self.export_button.config(state=tk.NORMAL, text="Export All Videos")
            self.reset_button.config(state=tk.NORMAL)
            progress_bar.destroy()
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)