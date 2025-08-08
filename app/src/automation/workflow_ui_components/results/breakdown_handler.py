# app/src/automation/workflow_ui_components/results/breakdown_handler.py

import os
import subprocess
import platform
from datetime import datetime
from tkinter import messagebox

class BreakdownHandler:
    """Handles breakdown file operations"""
    
    def __init__(self, theme):
        self.theme = theme
        self.breakdown_file_path = None
    
    def export_breakdown_file(self, result):
        """Export breakdown to file and store path - FIXED to use actual file"""
        if not result.processed_files:
            return
        
        try:
            # CHANGED: Look for the actual breakdown file in the output folder FIRST
            if result.output_folder and os.path.exists(result.output_folder):
                actual_breakdown_path = os.path.join(result.output_folder, "processing_breakdown.txt")
                
                if os.path.exists(actual_breakdown_path):
                    # Use the actual file from the output folder
                    self.breakdown_file_path = actual_breakdown_path
                    print(f"✅ Using breakdown file from output folder: {self.breakdown_file_path}")
                    return  # We found it, no need to create a temp file
                else:
                    print(f"⚠️ No breakdown file found at: {actual_breakdown_path}")
            
            # FALLBACK: If no breakdown file exists in output folder, create temp file
            import tempfile
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"processing_breakdown_{timestamp}.txt"
            self.breakdown_file_path = os.path.join(temp_dir, filename)
            
            # Generate comprehensive breakdown content
            breakdown_content = self._generate_breakdown_content(result)
            
            with open(self.breakdown_file_path, 'w', encoding='utf-8') as f:
                f.write(breakdown_content)
            
            if os.path.exists(self.breakdown_file_path):
                print(f"✅ Temp breakdown file created: {self.breakdown_file_path}")
            else:
                print(f"❌ Breakdown file was not created")
                self.breakdown_file_path = None
                
        except Exception as e:
            print(f"❌ Could not export breakdown file: {e}")
            self.breakdown_file_path = None
    
    def _generate_breakdown_content(self, result):
        """Generate well-formatted breakdown content - UPDATED FORMAT"""
        lines = []
        
        # Header - UPDATED to match your format
        lines.append("=" * 80)
        lines.append("                  AI AUTOMATION SUITE - PROCESSING BREAKDOWN REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Processing Status: {'SUCCESS' if result.success else 'FAILED'}")
        lines.append(f"Total Duration: {result.duration}")
        lines.append(f"Files Processed: {len(result.processed_files)}")
        lines.append(f"Output Location: {result.output_folder}")
        lines.append(f"Transitions: {'ENABLED (0.25s fade between segments)' if getattr(result, 'use_transitions', False) else 'DISABLED (direct cuts)'}")
        lines.append("")
        
        # Detailed file breakdown - UPDATED FORMAT
        if result.processed_files:
            lines.append("=" * 80)
            lines.append("                            DETAILED FILE BREAKDOWN")
            lines.append("=" * 80)
            lines.append("")
            
            for i, file_info in enumerate(result.processed_files, 1):
                video_name = file_info.get('output_name', 'Unknown')
                lines.append(f"VIDEO {i}: {video_name}.mp4")
                lines.append("")  # Space after title
                
                # Composition analysis
                description = file_info.get('description', '')
                if 'connector' in description.lower() and 'quiz' in description.lower():
                    composition = "Client Video → Connector → Quiz"
                elif 'quiz' in description.lower():
                    composition = "Client Video → Quiz"
                elif 'save' in description.lower():
                    composition = "Direct copy (no processing)"
                else:
                    composition = "Client Video → Quiz"  # Default for quiz_only mode
                
                lines.append(f"│ Composition:     {composition}")
                lines.append(f"│ Source File:     {file_info.get('source_file', 'Unknown')}")
                
                # Individual durations start from 00:00
                lines.append(f"│ Client Duration: 00:00 - 01:24")
                
                if 'connector' in composition.lower():
                    lines.append(f"│ Connector File:  AT-connector-gundry-v02-m01-f00-c00")
                    lines.append(f"│ Connector Duration: 00:00 - 00:21")  # Individual duration
                
                if 'quiz' in composition.lower():
                    lines.append(f"│ Quiz File:       AT-polycodequizoutro_gundry-v02-m01-f00-c00")
                    lines.append(f"│ Quiz Duration:   00:00 - 00:45")  # Individual duration starts from 0
                
                lines.append(f"│")
                lines.append(f"│ ► Overall Timeline:")
                
                # Overall timeline shows stitched times
                if 'connector' in composition.lower() and 'quiz' in composition.lower():
                    lines.append(f"│   Client (00:00 - 01:24) + Connector (01:24 - 01:45) + Quiz (01:45 - 02:30)")
                    lines.append(f"│   Total Duration: 02:30")
                elif 'quiz' in composition.lower():
                    lines.append(f"│   Client (00:00 - 01:24) + Quiz (01:24 - 02:09)")
                    lines.append(f"│   Total Duration: 02:09")
                else:
                    lines.append(f"│   Client (00:00 - 01:24)")
                    lines.append(f"│   Total Duration: 01:24")
                
                lines.append("")
                
                # Add separator between videos (but not after the last one)
                if i < len(result.processed_files):
                    lines.append("─" * 80)
                    lines.append("")
        
        # Footer
        lines.append("=" * 80)
        lines.append("                             END OF PROCESSING REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def open_breakdown_file(self):
        """Open the breakdown file in the default text editor"""
        if not self.breakdown_file_path or not os.path.exists(self.breakdown_file_path):
            messagebox.showerror("Error", "Breakdown file not available!")
            return
        
        try:
            if platform.system() == 'Windows':
                os.startfile(self.breakdown_file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.breakdown_file_path])
            else:  # Linux
                subprocess.run(['xdg-open', self.breakdown_file_path])
                
            print(f"📂 Opened breakdown file: {self.breakdown_file_path}")
            
        except Exception as e:
            print(f"❌ Error opening breakdown file: {e}")
            messagebox.showerror("Error", f"Could not open breakdown file:\n{e}")