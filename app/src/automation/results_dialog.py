# app/src/automation/results_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import platform
import webbrowser
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ProcessingResult:
    """Results from processing operation"""
    success: bool
    duration: str
    processed_files: List[Dict]  # {version, source_file, output_name, description, duration}
    output_folder: str
    error_message: str = ""
    error_solution: str = ""
    video_connections: List[Dict] = None  # {source, connector, quiz, final_duration}

@dataclass
class NotificationSettings:
    """Notification configuration"""
    email_enabled: bool = False
    email_address: str = ""
    slack_enabled: bool = False
    slack_webhook: str = ""

class ResultsDialog:
    """Results dialog showing success or error with actionable buttons"""
    
    def __init__(self, parent=None):
        self.root = None
        self.parent = parent
        
    def show_success(self, result: ProcessingResult, notifications: NotificationSettings = None):
        """Show success dialog with results and actions"""
        self._create_dialog("success")
        self._show_success_content(result)
        if notifications:
            self._send_notifications(result, notifications)
        
    def show_error(self, error_message: str, error_solution: str = "", bring_to_front: bool = True):
        """Show error dialog with solution and retry options"""
        self._create_dialog("error", bring_to_front)
        self._show_error_content(error_message, error_solution)
        
    def _create_dialog(self, dialog_type: str, bring_to_front: bool = False):
        """Create base dialog window"""
        self.root = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        
        if dialog_type == "success":
            self.root.title("Processing Complete")
            self.root.geometry("600x750")
        else:  # error
            self.root.title("Processing Error")
            self.root.geometry("550x500")
            
        self.root.resizable(False, False)
        
        # Apply white theme
        self._apply_white_theme()
        
        # Center window
        self._center_window()
        
        # Make modal
        self.root.transient(self.parent)
        self.root.grab_set()
        
        # Bring to front if requested (for errors)
        if bring_to_front:
            self.root.lift()
            self.root.focus_force()
            self.root.attributes('-topmost', True)
            self.root.after(500, lambda: self.root.attributes('-topmost', False))
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.wait_window()
        
    def _apply_white_theme(self):
        """Apply pure white theme"""
        self.colors = {
            'bg': '#ffffff',
            'success': '#107c10',
            'error': '#d13438',
            'accent': '#0078d4',
            'text_primary': '#323130',
            'text_secondary': '#605e5c',
            'border': '#e1dfdd'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        style = ttk.Style()
        style.configure('White.TFrame', background=self.colors['bg'])
        style.configure('Header.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 18, 'bold'))
        style.configure('Subheader.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 11))
        style.configure('Body.TLabel', background=self.colors['bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        style.configure('Accent.TButton', font=('Segoe UI', 11, 'bold'),
                       padding=(25, 12))
        style.configure('Secondary.TButton', font=('Segoe UI', 11),
                       padding=(25, 12))
    
    def _center_window(self):
        """Center dialog on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _show_success_content(self, result: ProcessingResult):
        """Show success content with detailed results"""
        # Header
        self._create_header("🎉", "Success!", "Your videos have been processed successfully")
        
        # Scrollable content
        content_frame = self._create_scrollable_content()
        
        # Processing summary
        self._add_summary_section(content_frame, result)
        
        # Processed files details
        if result.processed_files:
            self._add_files_section(content_frame, result.processed_files)
        
        # Video connections (if available)
        if result.video_connections:
            self._add_connections_section(content_frame, result.video_connections)
        
        # Output location
        self._add_output_section(content_frame, result.output_folder)
        
        # Action buttons
        self._create_success_buttons(result.output_folder)
        
    def _show_error_content(self, error_message: str, error_solution: str):
        """Show error content with solution"""
        # Header
        self._create_header("❌", "Processing Error", "An error occurred during processing")
        
        # Error details container
        error_container = ttk.Frame(self.root, style='White.TFrame')
        error_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Error message
        ttk.Label(error_container, text="Error Details:", style='Body.TLabel',
                 font=('Segoe UI', 12, 'bold'),
                 foreground=self.colors['error']).pack(anchor=tk.W, pady=(0, 10))
        
        # Error text box
        error_frame = ttk.Frame(error_container, style='White.TFrame')
        error_frame.pack(fill=tk.X, pady=(0, 20))
        
        error_text = tk.Text(error_frame, height=6, wrap=tk.WORD, 
                            font=('Consolas', 9), bg='#fef9f9', 
                            borderwidth=1, relief='solid',
                            selectbackground='#e3f2fd')
        scrollbar_error = ttk.Scrollbar(error_frame, orient="vertical", command=error_text.yview)
        error_text.configure(yscrollcommand=scrollbar_error.set)
        
        error_text.pack(side="left", fill="both", expand=True)
        scrollbar_error.pack(side="right", fill="y")
        
        error_text.insert('1.0', error_message)
        error_text.configure(state='disabled')
        
        # Solution section
        if error_solution:
            ttk.Label(error_container, text="💡 Suggested Solution:", style='Body.TLabel',
                     font=('Segoe UI', 12, 'bold'),
                     foreground=self.colors['accent']).pack(anchor=tk.W, pady=(0, 10))
            
            solution_frame = ttk.Frame(error_container, style='White.TFrame')
            solution_frame.pack(fill=tk.X, pady=(0, 20))
            
            solution_text = tk.Text(solution_frame, height=4, wrap=tk.WORD,
                                   font=('Segoe UI', 9), bg='#f0f8ff',
                                   borderwidth=1, relief='solid',
                                   selectbackground='#e3f2fd')
            scrollbar_solution = ttk.Scrollbar(solution_frame, orient="vertical", command=solution_text.yview)
            solution_text.configure(yscrollcommand=scrollbar_solution.set)
            
            solution_text.pack(side="left", fill="both", expand=True)
            scrollbar_solution.pack(side="right", fill="y")
            
            solution_text.insert('1.0', error_solution)
            solution_text.configure(state='disabled')
        
        # Error action buttons
        self._create_error_buttons()
    
    def _create_header(self, icon: str, title: str, subtitle: str):
        """Create header section"""
        header_frame = ttk.Frame(self.root, style='White.TFrame')
        header_frame.pack(fill=tk.X, padx=40, pady=(30, 20))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack(fill=tk.X)
        
        # Icon
        icon_label = ttk.Label(title_container, text=icon, font=('Segoe UI', 28),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Title and subtitle
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(text_frame, text=title, style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text=subtitle, style='Subheader.TLabel').pack(anchor=tk.W)
    
    def _create_scrollable_content(self):
        """Create scrollable content area"""
        content_container = ttk.Frame(self.root, style='White.TFrame')
        content_container.pack(fill=tk.BOTH, expand=True, padx=40)
        
        canvas = tk.Canvas(content_container, bg=self.colors['bg'], 
                          highlightthickness=0, height=450)
        scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='White.TFrame')
        
        scrollable_frame.bind("<Configure>", 
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        return scrollable_frame
    
    def _add_summary_section(self, parent, result: ProcessingResult):
        """Add processing summary section"""
        summary_frame = ttk.Frame(parent, style='White.TFrame')
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(summary_frame, text=f"✅ Processing completed in {result.duration}",
                 style='Body.TLabel', font=('Segoe UI', 12, 'bold'),
                 foreground=self.colors['success']).pack(anchor=tk.W)
        
        if result.processed_files:
            count = len(result.processed_files)
            ttk.Label(summary_frame, text=f"📊 {count} video{'s' if count != 1 else ''} processed successfully",
                     style='Body.TLabel', font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(5, 0))
    
    def _add_files_section(self, parent, processed_files: List[Dict]):
        """Add processed files section"""
        files_frame = ttk.Frame(parent, style='White.TFrame')
        files_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(files_frame, text="📁 Processed Files:", style='Body.TLabel',
                 font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        for i, file_info in enumerate(processed_files, 1):
            file_container = ttk.Frame(files_frame, style='White.TFrame')
            file_container.pack(fill=tk.X, pady=5, padx=20)
            
            # File number and name
            ttk.Label(file_container, text=f"{i}. {file_info['output_name']}.mp4",
                     style='Body.TLabel', font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
            
            # Details
            details_frame = ttk.Frame(file_container, style='White.TFrame')
            details_frame.pack(fill=tk.X, padx=20, pady=(2, 0))
            
            ttk.Label(details_frame, text=f"Source: {file_info['source_file']}",
                     style='Body.TLabel', font=('Segoe UI', 9)).pack(anchor=tk.W)
            ttk.Label(details_frame, text=f"Description: {file_info['description']}",
                     style='Body.TLabel', font=('Segoe UI', 9)).pack(anchor=tk.W)
            
            if 'duration' in file_info:
                ttk.Label(details_frame, text=f"Duration: {file_info['duration']}",
                         style='Body.TLabel', font=('Segoe UI', 9),
                         foreground=self.colors['text_secondary']).pack(anchor=tk.W)
    
    def _add_connections_section(self, parent, connections: List[Dict]):
        """Add video connections section"""
        conn_frame = ttk.Frame(parent, style='White.TFrame')
        conn_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(conn_frame, text="🔗 Video Assembly Details:", style='Body.TLabel',
                 font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        for i, conn in enumerate(connections, 1):
            conn_container = ttk.Frame(conn_frame, style='White.TFrame')
            conn_container.pack(fill=tk.X, pady=5, padx=20)
            
            # Connection flow
            flow_text = f"{i}. {conn['source']}"
            if conn.get('connector'):
                flow_text += f" → {conn['connector']}"
            if conn.get('quiz'):
                flow_text += f" → {conn['quiz']}"
            
            ttk.Label(conn_container, text=flow_text, style='Body.TLabel',
                     font=('Segoe UI', 10)).pack(anchor=tk.W)
            
            if conn.get('final_duration'):
                ttk.Label(conn_container, text=f"Final Duration: {conn['final_duration']}",
                         style='Body.TLabel', font=('Segoe UI', 9),
                         foreground=self.colors['text_secondary']).pack(anchor=tk.W, padx=20)
    
    def _add_output_section(self, parent, output_folder: str):
        """Add output location section"""
        output_frame = ttk.Frame(parent, style='White.TFrame')
        output_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(output_frame, text="📂 Output Location:", style='Body.TLabel',
                 font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)
        
        # Clickable path
        path_frame = ttk.Frame(output_frame, style='White.TFrame')
        path_frame.pack(fill=tk.X, padx=20, pady=(5, 0))
        
        path_label = ttk.Label(path_frame, text=output_folder, style='Body.TLabel',
                              font=('Segoe UI', 9), foreground=self.colors['accent'],
                              cursor="hand2")
        path_label.pack(anchor=tk.W)
        path_label.bind("<Button-1>", lambda e: self._open_folder(output_folder))
        
        # Instruction
        ttk.Label(path_frame, text="(Click path above to open folder)",
                 style='Body.TLabel', font=('Segoe UI', 8, 'italic'),
                 foreground=self.colors['text_secondary']).pack(anchor=tk.W)
    
    def _create_success_buttons(self, output_folder: str):
        """Create success action buttons"""
        button_frame = ttk.Frame(self.root, style='White.TFrame')
        button_frame.pack(fill=tk.X, padx=40, pady=30)
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        # Open folder button (primary action)
        ttk.Button(button_container, text="📂 Open Output Folder", 
                  style='Accent.TButton',
                  command=lambda: self._open_folder(output_folder)).pack(side=tk.LEFT, padx=(0, 15))
        
        # Done button
        ttk.Button(button_container, text="✅ Done", style='Secondary.TButton',
                  command=self._on_close).pack(side=tk.LEFT)
    
    def _create_error_buttons(self):
        """Create error action buttons"""
        button_frame = ttk.Frame(self.root, style='White.TFrame')
        button_frame.pack(fill=tk.X, padx=40, pady=30)
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        # Copy error button
        ttk.Button(button_container, text="📋 Copy Error Details", 
                  style='Secondary.TButton',
                  command=self._copy_error_details).pack(side=tk.LEFT, padx=(0, 15))
        
        # Close button
        ttk.Button(button_container, text="❌ Close", style='Secondary.TButton',
                  command=self._on_close).pack(side=tk.LEFT)
    
    def _open_folder(self, folder_path: str):
        """Open output folder in file explorer"""
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")
    
    def _copy_error_details(self):
        """Copy error details to clipboard"""
        try:
            # Find the error text widget and copy its contents
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Text):
                            error_text = child.get("1.0", tk.END)
                            self.root.clipboard_clear()
                            self.root.clipboard_append(error_text)
                            self.root.update()
                            messagebox.showinfo("Copied", "Error details copied to clipboard!")
                            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy to clipboard:\n{e}")
    
    def _send_notifications(self, result: ProcessingResult, notifications: NotificationSettings):
        """Send completion notifications"""
        if notifications.email_enabled and notifications.email_address:
            self._send_email_notification(result, notifications.email_address)
        
        if notifications.slack_enabled and notifications.slack_webhook:
            self._send_slack_notification(result, notifications.slack_webhook)
    
    def _send_email_notification(self, result: ProcessingResult, email_address: str):
        """Send email notification (placeholder implementation)"""
        try:
            # TODO: Implement actual email sending
            # This would require SMTP configuration
            print(f"Email notification would be sent to: {email_address}")
            print(f"Subject: AI Automation Complete - {len(result.processed_files)} videos processed")
            print(f"Duration: {result.duration}")
        except Exception as e:
            print(f"Failed to send email notification: {e}")
    
    def _send_slack_notification(self, result: ProcessingResult, webhook_url: str):
        """Send Slack notification"""
        try:
            message = {
                "text": f"🎬 AI Automation Complete!",
                "attachments": [
                    {
                        "color": "good",
                        "fields": [
                            {"title": "Videos Processed", "value": str(len(result.processed_files)), "short": True},
                            {"title": "Duration", "value": result.duration, "short": True},
                            {"title": "Output Location", "value": result.output_folder, "short": False}
                        ]
                    }
                ]
            }
            
            # TODO: Implement actual Slack webhook call
            # requests.post(webhook_url, json=message)
            print(f"Slack notification would be sent to: {webhook_url}")
            print(f"Message: {message}")
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
    
    def _on_close(self):
        """Handle close button"""
        self.root.destroy()

# Test functions
def test_success_dialog():
    """Test success dialog"""
    test_result = ProcessingResult(
        success=True,
        duration="2 minutes 34 seconds",
        processed_files=[
            {
                'version': 'v01',
                'source_file': 'video1.mp4',
                'output_name': 'GH-grocerystoreoilsvtd12036ZZquiz_x-v01-m01-f00-c00',
                'description': 'New Ad from video1.mp4 + connector + quiz',
                'duration': '1:45'
            },
            {
                'version': 'v02',
                'source_file': 'video2.mp4',
                'output_name': 'GH-grocerystoreoilsvtd12036ZZquiz_y-v02-m01-f00-c00',
                'description': 'New Ad from video2.mp4 + connector + quiz',
                'duration': '2:12'
            }
        ],
        output_folder=r"C:\Users\talZ\Desktop\GH Grocery Store Oils VTD 12036 Quiz",
        video_connections=[
            {
                'source': 'video1.mp4',
                'connector': 'blake_connector.mp4',
                'quiz': 'quiz_outro.mp4',
                'final_duration': '1:45'
            }
        ]
    )
    
    notifications = NotificationSettings(
        email_enabled=True,
        email_address="user@example.com",
        slack_enabled=True,
        slack_webhook="https://hooks.slack.com/..."
    )
    
    dialog = ResultsDialog()
    dialog.show_success(test_result, notifications)

def test_error_dialog():
    """Test error dialog"""
    error_msg = """Failed to download videos: Google Drive API error: <HttpError 404 when requesting https://www.googleapis.com/drive/v3/files?q='1utt4vV6JK73c9NVAI8f5T04Ffz0Uhas1dd'+in+parents+and+mimeType+contains+'video%2F'&fields=files%28id%2C+name%2C+size%29&alt=json returned "File not found: .". Details: "[{'message': 'File not found: .', 'domain': 'global', 'reason': 'notFound', 'location': 'fileId', 'locationType': 'parameter'}]">"""
    
    solution = """1. Check if the Google Drive folder link is correct and accessible
2. Verify the folder is shared with your service account email
3. Ensure the folder contains video files (.mp4 or .mov)
4. Try opening the Google Drive link in your browser to confirm access"""
    
    dialog = ResultsDialog()
    dialog.show_error(error_msg, solution, bring_to_front=True)

if __name__ == "__main__":
    # Test both dialogs
    print("Testing Success Dialog...")
    test_success_dialog()
    
    print("Testing Error Dialog...")
    test_error_dialog()