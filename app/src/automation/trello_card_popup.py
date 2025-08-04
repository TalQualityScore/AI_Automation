# app/src/automation/trello_card_popup.py
import tkinter as tk
from tkinter import ttk, messagebox
import re

class TrelloCardPopup:
    """Initial popup to get Trello card URL"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.result = None
        self.card_id = None
        
    def show_popup(self):
        """Show the Trello card input popup and return card ID"""
        self._create_popup()
        return self.card_id
    
    def _create_popup(self):
        """Create the main popup with overlay"""
        # Create main window if no parent
        if not self.parent:
            self.parent = tk.Tk()
            self.parent.withdraw()  # Hide it
        
        # Create overlay window
        self.overlay = tk.Toplevel(self.parent)
        self.overlay.title("AI Automation - Trello Card")
        self.overlay.geometry("600x800")
        self.overlay.resizable(False, False)
        self.overlay.configure(bg='black')
        
        # Make it modal
        self.overlay.transient(self.parent)
        self.overlay.grab_set()
        
        # Center the overlay
        self._center_window(self.overlay, 600, 800)
        
        # Create semi-transparent background
        bg_frame = tk.Frame(self.overlay, bg='black')
        bg_frame.pack(fill=tk.BOTH, expand=True)
        
        # Set opacity (Windows)
        try:
            self.overlay.attributes('-alpha', 0.85)
        except:
            pass
        
        # Create the popup dialog
        self._create_dialog()
        
        # Handle window close
        self.overlay.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Wait for result
        self.overlay.wait_window()
    
    def _create_dialog(self):
        """Create the centered dialog box"""
        # Main dialog frame
        dialog_frame = tk.Frame(self.overlay, bg='white', relief='raised', borderwidth=2)
        dialog_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Apply padding
        content_frame = tk.Frame(dialog_frame, bg='white', padx=40, pady=30)
        content_frame.pack()
        
        # Header
        header_frame = tk.Frame(content_frame, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Icon and title
        icon_label = tk.Label(header_frame, text="🎬", font=('Segoe UI', 24), bg='white')
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        title_frame = tk.Frame(header_frame, bg='white')
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(title_frame, text="AI Automation Workflow", 
                font=('Segoe UI', 18, 'bold'), bg='white', fg='#323130').pack(anchor=tk.W)
        tk.Label(title_frame, text="Enter your Trello card to get started", 
                font=('Segoe UI', 11), bg='white', fg='#605e5c').pack(anchor=tk.W)
        
        # Input section
        input_frame = tk.Frame(content_frame, bg='white')
        input_frame.pack(fill=tk.X, pady=(0, 25))
        
        tk.Label(input_frame, text="📋 Trello Card URL or ID:", 
                font=('Segoe UI', 12, 'bold'), bg='white', fg='#323130').pack(anchor=tk.W, pady=(0, 10))
        
        # URL input
        self.url_entry = tk.Entry(input_frame, font=('Segoe UI', 10), width=50, relief='solid', borderwidth=1)
        self.url_entry.pack(fill=tk.X, pady=(0, 5))
        self.url_entry.insert(0, "Paste your Trello card URL here...")
        self.url_entry.bind('<FocusIn>', self._on_entry_focus)
        self.url_entry.bind('<Return>', lambda e: self._on_ok())
        
        # Help text
        help_frame = tk.Frame(input_frame, bg='white')
        help_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(help_frame, text="💡 Examples:", 
                font=('Segoe UI', 9, 'bold'), bg='white', fg='#605e5c').pack(anchor=tk.W)
        tk.Label(help_frame, text="• Full URL: https://trello.com/c/abc123xyz/...", 
                font=('Segoe UI', 9), bg='white', fg='#605e5c').pack(anchor=tk.W, padx=(15, 0))
        tk.Label(help_frame, text="• Card ID only: abc123xyz", 
                font=('Segoe UI', 9), bg='white', fg='#605e5c').pack(anchor=tk.W, padx=(15, 0))
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Center the buttons
        button_container = tk.Frame(button_frame, bg='white')
        button_container.pack()
        
        cancel_btn = tk.Button(button_container, text="❌ Cancel", 
                              font=('Segoe UI', 11), bg='#f3f3f3', fg='#323130',
                              relief='flat', borderwidth=0, padx=25, pady=12,
                              command=self._on_cancel, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        ok_btn = tk.Button(button_container, text="✅ Start Processing", 
                          font=('Segoe UI', 11, 'bold'), bg='#0078d4', fg='white',
                          relief='flat', borderwidth=0, padx=25, pady=12,
                          command=self._on_ok, cursor='hand2')
        ok_btn.pack(side=tk.LEFT)
        
        # Set focus to entry
        self.url_entry.focus_set()
        self.url_entry.select_range(0, tk.END)
    
    def _center_window(self, window, width, height):
        """Center window on screen"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _on_entry_focus(self, event):
        """Clear placeholder text when entry gets focus"""
        if self.url_entry.get() == "Paste your Trello card URL here...":
            self.url_entry.delete(0, tk.END)
    
    def _extract_card_id(self, input_text):
        """Extract Trello card ID from URL or return as-is if already an ID"""
        input_text = input_text.strip()
        
        # If it's already a card ID (letters/numbers, typically 24 chars)
        if re.match(r'^[a-zA-Z0-9]{20,30}$', input_text):
            return input_text
        
        # Extract from full Trello URL
        # Pattern: https://trello.com/c/CARD_ID/...
        url_pattern = r'https?://trello\.com/c/([a-zA-Z0-9]+)'
        match = re.search(url_pattern, input_text)
        if match:
            return match.group(1)
        
        # If no pattern matches, return None
        return None
    
    def _on_ok(self):
        """Handle OK button"""
        url_text = self.url_entry.get().strip()
        
        # Check if empty or placeholder
        if not url_text or url_text == "Paste your Trello card URL here...":
            messagebox.showerror("Error", "Please enter a Trello card URL or ID")
            return
        
        # Extract card ID
        card_id = self._extract_card_id(url_text)
        
        if not card_id:
            messagebox.showerror("Invalid Input", 
                               "Could not extract card ID from input.\n\n"
                               "Please provide either:\n"
                               "• A full Trello URL (https://trello.com/c/abc123xyz/...)\n"
                               "• Just the card ID (abc123xyz)")
            return
        
        # Success
        self.card_id = card_id
        self.overlay.destroy()
    
    def _on_cancel(self):
        """Handle Cancel button"""
        self.card_id = None
        self.overlay.destroy()

# Test function
def test_trello_popup():
    """Test the Trello card popup"""
    popup = TrelloCardPopup()
    card_id = popup.show_popup()
    
    if card_id:
        print(f"✅ Card ID extracted: {card_id}")
    else:
        print("❌ User cancelled or no card ID provided")
    
    return card_id

if __name__ == "__main__":
    test_trello_popup()