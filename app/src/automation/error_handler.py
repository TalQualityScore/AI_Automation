# Add this to app/src/automation/error_handler.py

import tkinter as tk
from tkinter import messagebox, scrolledtext
import traceback
import sys

class ErrorHandler:
    def __init__(self):
        self.last_error = None
        
    def handle_error(self, error, context=""):
        """Handle errors with pop-up notification."""
        self.last_error = {
            'error': str(error),
            'traceback': traceback.format_exc(),
            'context': context
        }
        
        # Create error pop-up
        self.show_error_popup()
        
    def show_error_popup(self):
        """Show error pop-up with options."""
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        # Custom dialog
        dialog = tk.Toplevel(root)
        dialog.title("Process Stopped")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(root)
        dialog.grab_set()
        
        # Error message
        tk.Label(dialog, text="❌ Process has stopped due to an error", 
                font=("Arial", 12, "bold"), fg="red").pack(pady=20)
        
        # Buttons frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        # OK button
        tk.Button(button_frame, text="OK", width=10, 
                 command=lambda: self.close_dialog(dialog, root)).pack(side=tk.LEFT, padx=10)
        
        # View Error button
        tk.Button(button_frame, text="View Error", width=10,
                 command=lambda: self.show_error_details()).pack(side=tk.LEFT, padx=10)
        
        # X button (close)
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_dialog(dialog, root))
        
        # Wait for dialog to close
        dialog.wait_window()
        
    def show_error_details(self):
        """Show detailed error information in a new window."""
        error_window = tk.Toplevel()
        error_window.title("Error Details")
        error_window.geometry("800x600")
        
        # Scrolled text widget for error details
        text_widget = scrolledtext.ScrolledText(error_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert error details
        error_text = f"Context: {self.last_error['context']}\n\n"
        error_text += f"Error: {self.last_error['error']}\n\n"
        error_text += f"Traceback:\n{self.last_error['traceback']}"
        
        text_widget.insert(tk.END, error_text)
        text_widget.configure(state=tk.DISABLED)  # Read-only
        
        # Copy button
        tk.Button(error_window, text="Copy to Clipboard", 
                 command=lambda: self.copy_to_clipboard(error_text)).pack(pady=10)
        
    def copy_to_clipboard(self, text):
        """Copy error text to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(text)
            messagebox.showinfo("Copied", "Error details copied to clipboard!")
        except ImportError:
            # Fallback if pyperclip not available
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            messagebox.showinfo("Copied", "Error details copied to clipboard!")
            root.destroy()
        
    def close_dialog(self, dialog, root):
        """Close dialog and exit."""
        dialog.destroy()
        root.destroy()
        sys.exit(1)  # Exit the program

# Global error handler instance
error_handler = ErrorHandler()