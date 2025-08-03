# app/src/automation/confirmation_dialog.py
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import List

@dataclass
class ValidationIssue:
    """Data structure for validation issues"""
    severity: str  # "warning", "error", "info"
    message: str

@dataclass
class ConfirmationData:
    """All data needed for the confirmation popup"""
    project_name: str
    account: str
    platform: str
    processing_mode: str
    client_videos: List[str]
    templates_to_add: List[str]
    output_location: str
    estimated_time: str
    issues: List[ValidationIssue]
    file_sizes: List[tuple]  # (filename, size_mb)

class ConfirmationDialog:
    """Pure white confirmation dialog for processing preview"""
    
    def __init__(self, parent=None):
        self.result = False
        self.root = None
        self.parent = parent
        self.notification_settings = {
            'email': {'enabled': False, 'address': ''},
            'slack': {'enabled': False, 'webhook': ''}
        }
        
    def show_confirmation(self, data: ConfirmationData) -> tuple:
        """Show confirmation dialog and return (user_choice, notification_settings)"""
        self._create_dialog(data)
        return self.result, self.notification_settings
    
    def _create_dialog(self, data: ConfirmationData):
        """Create and display the confirmation dialog"""
        self.root = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.root.title("Processing Confirmation")
        self.root.geometry("520x700")
        self.root.resizable(False, False)
        
        # Apply pure white styling
        self._apply_white_theme()
        
        # Center and make modal
        self._center_window()
        self.root.transient(self.parent)
        self.root.grab_set()
        self.root.lift()
        self.root.focus_force()
        
        # Create UI
        self._create_header()
        content_frame = self._create_scrollable_content()
        self._add_project_info(content_frame, data)
        self._add_processing_details(content_frame, data)
        
        # Filter large file warnings (only files > 1GB)
        filtered_issues = self._filter_large_file_warnings(data.issues, data.file_sizes)
        if filtered_issues:
            self._add_issues_section(content_frame, filtered_issues)
        
        self._add_output_info(content_frame, data)
        self._add_notification_settings(content_frame)
        self._create_buttons()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.wait_window()
        
    def _apply_white_theme(self):
        """Apply pure white theme"""
        self.colors = {
            'bg': '#ffffff',           # Pure white
            'accent': '#0078d4',       # Microsoft blue
            'success': '#107c10',      # Success green
            'warning': '#ff8c00',      # Warning orange
            'error': '#d13438',        # Error red
            'text_primary': '#323130', # Primary text
            'text_secondary': '#605e5c', # Secondary text
            'border': '#e1dfdd'        # Light border
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
        x = (self.root.winfo_screenwidth() // 2) - (520 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"520x700+{x}+{y}")
    
    def _create_header(self):
        """Create header section"""
        header_frame = ttk.Frame(self.root, style='White.TFrame')
        header_frame.pack(fill=tk.X, padx=40, pady=(30, 20))
        
        title_container = ttk.Frame(header_frame, style='White.TFrame')
        title_container.pack(fill=tk.X)
        
        # Icon
        icon_label = ttk.Label(title_container, text="🎬", font=('Segoe UI', 28),
                              style='Body.TLabel')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Title and subtitle
        text_frame = ttk.Frame(title_container, style='White.TFrame')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(text_frame, text="Processing Confirmation", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(text_frame, text="Review the details before processing", style='Subheader.TLabel').pack(anchor=tk.W)
    
    def _create_scrollable_content(self):
        """Create scrollable content area with proper height"""
        content_container = ttk.Frame(self.root, style='White.TFrame')
        content_container.pack(fill=tk.BOTH, expand=True, padx=40)
        
        canvas = tk.Canvas(content_container, bg=self.colors['bg'], 
                          highlightthickness=0, height=400)  # Fixed height to prevent text cutoff
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
    
    def _add_project_info(self, parent, data: ConfirmationData):
        """Add project information section"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        details = [
            ("Project:", data.project_name),
            ("Account:", data.account),
            ("Platform:", data.platform),
            ("Mode Detected:", data.processing_mode.replace('_', ' ').upper())
        ]
        
        for label, value in details:
            row_frame = ttk.Frame(section_frame, style='White.TFrame')
            row_frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(row_frame, text=label, style='Body.TLabel',
                     font=('Segoe UI', 10)).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=value, style='Body.TLabel',
                     font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(10, 0))
    
    def _add_processing_details(self, parent, data: ConfirmationData):
        """Add processing details section"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(section_frame, text="Will Process:", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        if data.client_videos:
            ttk.Label(section_frame, 
                     text=f"✓ {len(data.client_videos)} client video(s) from Google Drive",
                     style='Body.TLabel', foreground=self.colors['success']).pack(anchor=tk.W, padx=20)
        
        for template in data.templates_to_add:
            ttk.Label(section_frame, text=f"✓ {template}", style='Body.TLabel',
                     foreground=self.colors['success']).pack(anchor=tk.W, padx=20)
    
    def _filter_large_file_warnings(self, issues: List[ValidationIssue], file_sizes: List[tuple]):
        """Filter issues - only show large file warnings for files > 1GB"""
        filtered_issues = []
        
        for issue in issues:
            if "large file" in issue.message.lower():
                # Check if any file is actually > 1GB (1000MB)
                for filename, size_mb in file_sizes:
                    if size_mb > 1000:
                        filtered_issues.append(ValidationIssue("warning", 
                            f"Large file detected: {filename} ({size_mb}MB)"))
                        break
            else:
                filtered_issues.append(issue)
        
        return filtered_issues
    
    def _add_issues_section(self, parent, issues: List[ValidationIssue]):
        """Add issues section"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(section_frame, text="⚠️ Issues Found:", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold'), 
                 foreground=self.colors['warning']).pack(anchor=tk.W, pady=(0, 8))
        
        for issue in issues:
            color = self.colors.get(issue.severity, self.colors['text_primary'])
            ttk.Label(section_frame, text=f"• {issue.message}", style='Body.TLabel',
                     foreground=color).pack(anchor=tk.W, padx=20)
    
    def _add_output_info(self, parent, data: ConfirmationData):
        """Add output information section"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(section_frame, text="Output Location:", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W)
        ttk.Label(section_frame, text=f"📁 {data.output_location}", style='Body.TLabel').pack(anchor=tk.W, padx=20, pady=(5, 10))
        
        ttk.Label(section_frame, text=f"Processing Time Estimate: {data.estimated_time}",
                 style='Body.TLabel', font=('Segoe UI', 9, 'italic')).pack(anchor=tk.W)
    
    def _add_notification_settings(self, parent):
        """Add notification settings section"""
        section_frame = ttk.Frame(parent, style='White.TFrame')
        section_frame.pack(fill=tk.X, pady=(0, 30))  # Extra padding at bottom
        
        ttk.Label(section_frame, text="📧 Notifications (Optional):", style='Body.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        # Email notification
        email_frame = ttk.Frame(section_frame, style='White.TFrame')
        email_frame.pack(fill=tk.X, padx=20, pady=2)
        
        self.email_var = tk.BooleanVar()
        email_check = ttk.Checkbutton(email_frame, text="Email notification", 
                                     variable=self.email_var)
        email_check.pack(side=tk.LEFT)
        
        self.email_entry = ttk.Entry(email_frame, width=25)
        self.email_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.email_entry.insert(0, "your.email@domain.com")
        
        # Slack notification  
        slack_frame = ttk.Frame(section_frame, style='White.TFrame')
        slack_frame.pack(fill=tk.X, padx=20, pady=2)
        
        self.slack_var = tk.BooleanVar()
        slack_check = ttk.Checkbutton(slack_frame, text="Slack notification",
                                     variable=self.slack_var)
        slack_check.pack(side=tk.LEFT)
        
        self.slack_entry = ttk.Entry(slack_frame, width=25)
        self.slack_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.slack_entry.insert(0, "slack-webhook-url")
    
    def _create_buttons(self):
        """Create action buttons"""
        button_frame = ttk.Frame(self.root, style='White.TFrame')
        button_frame.pack(fill=tk.X, padx=40, pady=(0, 30))  # No top padding, bottom padding
        
        button_container = ttk.Frame(button_frame, style='White.TFrame')
        button_container.pack()
        
        ttk.Button(button_container, text="❌ CANCEL", style='Secondary.TButton',
                  command=self._on_cancel).pack(side=tk.LEFT, padx=(0, 15))
        
        confirm_btn = ttk.Button(button_container, text="✅ CONFIRM & RUN", 
                                style='Accent.TButton', command=self._on_confirm)
        confirm_btn.pack(side=tk.LEFT)
        confirm_btn.focus_set()
        
        self.root.bind('<Return>', lambda e: self._on_confirm())
        self.root.bind('<Escape>', lambda e: self._on_cancel())
    
    def _on_confirm(self):
        """Handle confirm button"""
        # Store notification settings
        self.notification_settings['email']['enabled'] = self.email_var.get()
        self.notification_settings['email']['address'] = self.email_entry.get()
        self.notification_settings['slack']['enabled'] = self.slack_var.get()  
        self.notification_settings['slack']['webhook'] = self.slack_entry.get()
        
        self.result = True
        self.root.destroy()
    
    def _on_cancel(self):
        """Handle cancel button"""
        self.result = False
        self.root.destroy()

# Test function
def test_confirmation_dialog():
    """Test the confirmation dialog"""
    test_data = ConfirmationData(
        project_name="Grocery Store Oils VTD 12036",
        account="OO (Olive Oil)",
        platform="YouTube", 
        processing_mode="CONNECTOR + QUIZ",
        client_videos=["video1.mp4", "video2.mp4", "video3.mp4"],
        templates_to_add=[
            "Add Blake connector (YT/Connectors/)",
            "Add quiz outro (YT/Quiz/)",
            "Apply slide transition effects"
        ],
        output_location="GH Grocery Store Oils VTD 12036 Quiz",
        estimated_time="5-8 minutes",
        issues=[
            ValidationIssue("warning", "Large file detected (440MB)"),
            ValidationIssue("info", "Processing will use significant disk space")
        ],
        file_sizes=[("video1.mp4", 145), ("video2.mp4", 298), ("video3.mp4", 1200)]  # One file > 1GB
    )
    
    dialog = ConfirmationDialog()
    result, notifications = dialog.show_confirmation(test_data)
    print(f"User choice: {'CONFIRMED' if result else 'CANCELLED'}")
    print(f"Notifications: {notifications}")

if __name__ == "__main__":
    # Test the confirmation dialog
    test_confirmation_dialog()