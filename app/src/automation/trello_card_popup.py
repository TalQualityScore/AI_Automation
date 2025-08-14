# app/src/automation/trello_card_popup.py - FIXED for Windows
import tkinter as tk
from tkinter import ttk, messagebox
import re

class TrelloCardPopup:
    """Initial popup to get Trello card URL - FIXED for Windows compatibility"""
    
    def __init__(self, parent=None, theme=None):
        self.parent = parent
        self.theme = theme
        self.result = None
        self.card_id = None
        self.root = None
        
    def show_popup(self):
        """Show the Trello card input popup and return card ID - FIXED"""
        print("🎬 Creating Trello card popup...")
        
        try:
            self._create_popup()
            print(f"✅ Popup completed. Result: {self.card_id}")
            return self.card_id
        except Exception as e:
            print(f"❌ Popup failed: {e}")
            return None
    
    def _create_popup(self):
        """Create the main popup - FIXED for Windows"""
        # FIXED: Create root window if no parent
        if not self.parent:
            print("Creating new root window...")
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the main window
            parent_window = self.root
        else:
            parent_window = self.parent
        
        # Create the popup window
        print("Creating popup dialog...")
        self.popup = tk.Toplevel(parent_window)
        self.popup.title("AI Automation - Trello Card")
        self.popup.geometry("500x400")
        self.popup.resizable(False, False)
        
        # Apply theme if available
        if self.theme:
            self.popup.configure(bg=self.theme.colors['bg'])
        
        # FIXED: Windows compatibility - ensure window appears
        self.popup.attributes('-topmost', True)
        self.popup.grab_set()
        self.popup.focus_force()
        
        # Center the window
        self._center_window()
        
        # Create the UI content
        self._create_content()
        
        # FIXED: Proper event handling
        self.popup.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        print("Starting popup mainloop...")
        self.popup.wait_window()  # FIXED: Use wait_window instead of mainloop
        
        # Clean up
        if self.root:
            self.root.destroy()
    
    def _center_window(self):
        """Center the popup window"""
        self.popup.update_idletasks()
        width = 500
        height = 400
        x = (self.popup.winfo_screenwidth() // 2) - (width // 2)
        y = (self.popup.winfo_screenheight() // 2) - (height // 2)
        self.popup.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_content(self):
        """Create the popup content"""
        # Get theme colors
        if self.theme:
            bg_color = self.theme.colors['frame_bg']
            text_primary = self.theme.colors['text_primary'] 
            text_secondary = self.theme.colors['text_secondary']
            # Force entry background to be white in both modes, keep text black
            entry_bg = 'white'
            entry_fg = '#000000'  # Black text in both modes
        else:
            bg_color = 'white'
            text_primary = '#323130'
            text_secondary = '#605e5c'
            entry_bg = 'white'
            entry_fg = '#323130'
        
        # Main container
        main_frame = tk.Frame(self.popup, bg=bg_color, padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg=bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Icon and title
        title_frame = tk.Frame(header_frame, bg=bg_color)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = tk.Label(title_frame, text="🎬 AI Automation Workflow", 
                              font=('Segoe UI', 16, 'bold'), bg=bg_color, fg=text_primary)
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_frame, text="Enter your Trello card to get started", 
                                 font=('Segoe UI', 10), bg=bg_color, fg=text_secondary)
        subtitle_label.pack(anchor=tk.W)
        
        # Input section
        input_frame = tk.Frame(main_frame, bg=bg_color)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        input_label = tk.Label(input_frame, text="📋 Trello Card URL or ID:", 
                              font=('Segoe UI', 11, 'bold'), bg=bg_color, fg=text_primary)
        input_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Entry field
        self.url_entry = tk.Entry(input_frame, font=('Segoe UI', 10), 
                                 relief='solid', borderwidth=1, width=50,
                                 bg=entry_bg, fg=entry_fg, insertbackground=entry_fg)
        self.url_entry.pack(fill=tk.X, pady=(0, 8))
        self.url_entry.insert(0, "Paste your Trello card URL here...")
        self.url_entry.bind('<FocusIn>', self._on_entry_focus)
        self.url_entry.bind('<Return>', lambda e: self._on_ok())
        
        # Help section
        help_frame = tk.Frame(input_frame, bg=bg_color)
        help_frame.pack(fill=tk.X, pady=(5, 0))
        
        help_title = tk.Label(help_frame, text="💡 Examples:", 
                             font=('Segoe UI', 9, 'bold'), bg=bg_color, fg=text_secondary)
        help_title.pack(anchor=tk.W)
        
        example1 = tk.Label(help_frame, text="• Full URL: https://trello.com/c/abc123xyz/...", 
                           font=('Segoe UI', 9), bg=bg_color, fg=text_secondary)
        example1.pack(anchor=tk.W, padx=(15, 0))
        
        example2 = tk.Label(help_frame, text="• Card ID only: abc123xyz", 
                           font=('Segoe UI', 9), bg=bg_color, fg=text_secondary)
        example2.pack(anchor=tk.W, padx=(15, 0))
        
        # Button section
        button_frame = tk.Frame(main_frame, bg=bg_color)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Center the buttons
        button_container = tk.Frame(button_frame, bg=bg_color)
        button_container.pack()
        
        # Theme-aware button colors
        if self.theme and self.theme.mode == 'dark':
            cancel_bg = '#444444'
            cancel_fg = '#ffffff'
        else:
            cancel_bg = '#f3f3f3'
            cancel_fg = '#323130'
        
        # Cancel button
        cancel_btn = tk.Button(button_container, text="❌ Cancel", 
                              font=('Segoe UI', 10), bg=cancel_bg, fg=cancel_fg,
                              relief='flat', borderwidth=0, padx=20, pady=10,
                              command=self._on_cancel, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # OK button (always blue)
        ok_btn = tk.Button(button_container, text="✅ Start Processing", 
                          font=('Segoe UI', 10, 'bold'), bg='#0078d4', fg='white',
                          relief='flat', borderwidth=0, padx=20, pady=10,
                          command=self._on_ok, cursor='hand2')
        ok_btn.pack(side=tk.LEFT)
        
        # Set focus to entry and select placeholder text
        self.url_entry.focus_set()
        self.url_entry.select_range(0, tk.END)
    
    def _on_entry_focus(self, event):
        """Clear placeholder text when entry gets focus"""
        current_text = self.url_entry.get()
        if current_text == "Paste your Trello card URL here...":
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
        """Handle OK button - FIXED to prevent getting stuck"""
        print("OK button clicked")
        url_text = self.url_entry.get().strip()
        
        # Check if empty or placeholder
        if not url_text or url_text == "Paste your Trello card URL here...":
            self._show_error_and_reset("Error", "Please enter a Trello card URL or ID")
            return
        
        # Extract card ID
        card_id = self._extract_card_id(url_text)
        
        if not card_id:
            self._show_error_and_reset("Invalid Input", 
                            "Could not extract card ID from input.\n\n"
                            "Please provide either:\n"
                            "• A full Trello URL (https://trello.com/c/abc123xyz/...)\n"
                            "• Just the card ID (abc123xyz)")
            return
        
        # Success
        print(f"Card ID extracted: {card_id}")
        self.card_id = card_id
        self.popup.destroy()

    def _show_error_and_reset(self, title, message):
        """Show error message and reset input field to prevent getting stuck"""
        # Show error message
        messagebox.showerror(title, message)
        
        # CRITICAL FIX: Reset the input field and refocus
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, "Paste your Trello card URL here...")
        
        # Refocus the entry field for user to try again
        self.url_entry.focus_set()
        self.url_entry.select_range(0, tk.END)
        
        print("🔄 Input field reset after error - ready for new input")

    def _on_cancel(self):
        """Handle Cancel button"""
        print("Cancel button clicked")
        self.card_id = None
        self.popup.destroy()


# FIXED: Test function
def test_trello_popup():
    """Test the Trello card popup - FIXED"""
    print("🧪 Testing Trello Card Popup...")
    
    popup = TrelloCardPopup()
    card_id = popup.show_popup()
    
    if card_id:
        print(f"✅ Success! Card ID: {card_id}")
    else:
        print("❌ User cancelled or no card ID provided")
    
    return card_id

if __name__ == "__main__":
    test_trello_popup()