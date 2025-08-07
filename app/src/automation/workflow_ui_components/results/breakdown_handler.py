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
        """Export breakdown to file and store path"""
        if not result.processed_files:
            return
        
        try:
            # Create breakdown file in temp directory
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
                print(f"✅ Breakdown file created: {self.breakdown_file_path}")
            else:
                print(f"❌ Breakdown file was not created")
                self.breakdown_file_path = None
                
        except Exception as e:
            print(f"❌ Could not export breakdown file: {e}")
            self.breakdown_file_path = None
    
    def _generate_breakdown_content(self, result):
        """Generate well-formatted breakdown content"""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("AI AUTOMATION SUITE - PROCESSING BREAKDOWN REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Processing Status: {'SUCCESS' if result.success else 'FAILED'}")
        lines.append(f"Total Duration: {result.duration}")
        lines.append(f"Files Processed: {len(result.processed_files)}")
        lines.append(f"Output Location: {result.output_folder}")
        lines.append("")
        
        # Detailed file breakdown
        if result.processed_files:
            lines.append("=" * 80)
            lines.append("DETAILED FILE BREAKDOWN")
            lines.append("=" * 80)
            lines.append("")
            
            for i, file_info in enumerate(result.processed_files, 1):
                video_name = file_info.get('output_name', 'Unknown')
                lines.append(f"VIDEO {i}: {video_name}.mp4")
                lines.append("─" * 60)
                
                # Composition analysis
                description = file_info.get('description', '')
                if 'connector' in description.lower() and 'quiz' in description.lower():
                    composition = "Client Video → Connector → Quiz"
                elif 'quiz' in description.lower():
                    composition = "Client Video → Quiz"
                elif 'save' in description.lower():
                    composition = "Direct copy (no processing)"
                else:
                    composition = "Unknown composition"
                
                lines.append(f"│ Composition:     {composition}")
                lines.append(f"│ Source File:     {file_info.get('source_file', 'Unknown')}")
                lines.append(f"│ Source Duration: 0:23")
                
                lines.append("")
        
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
                
            print(f"✅ Opened breakdown file: {self.breakdown_file_path}")
            
        except Exception as e:
            print(f"❌ Error opening breakdown file: {e}")
            messagebox.showerror("Error", f"Could not open breakdown file:\n{e}")