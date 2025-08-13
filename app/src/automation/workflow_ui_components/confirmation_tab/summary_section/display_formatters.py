# app/src/automation/workflow_ui_components/confirmation_tab/summary_section/display_formatters.py
"""
Display Formatters - Text Formatting Utilities
Handles formatting text and display elements for the summary section
"""

class DisplayFormatters:
    """Handles text formatting and display utilities"""
    
    def __init__(self, summary_section):
        self.ss = summary_section  # Reference to main SummarySection
    
    def format_video_count_text(self, count):
        """Format video count text"""
        if count == 0:
            return "• No videos selected"
        elif count == 1:
            return "• 1 client video will be processed"
        else:
            return f"• {count} client videos will be processed"
    
    def format_mode_text(self, mode_display, is_single=True):
        """Format processing mode text"""
        if is_single:
            return f"• Processing type: {mode_display}"
        else:
            return f"• Processing modes: {mode_display}"
    
    def format_endpoint_text(self, endpoint):
        """Format endpoint connection text"""
        return f"• Videos will be connected to: {endpoint}"
    
    def format_output_text(self, folder_count):
        """Format output folder text"""
        if folder_count == 0:
            return "• Output: No folders will be created"
        elif folder_count == 1:
            return "• Output: 1 folder will be created"
        else:
            return f"• Output: {folder_count} separate folders will be created"
    
    def format_time_text(self, estimated_time):
        """Format estimated time text"""
        return f"• Estimated processing time: {estimated_time}"
    
    def format_transitions_text(self, enabled):
        """Format transitions setting text"""
        status = "with smooth transitions" if enabled else "without transitions"
        return f"• Processing type: {status}"
    
    def format_mode_list(self, selected_modes):
        """Format list of selected modes"""
        if not selected_modes:
            return ""
        
        lines = []
        for i, mode in enumerate(selected_modes, 1):
            mode_display = self.ss.mode_analyzers.get_mode_display_name(mode)
            lines.append(f"  {i}. {mode_display}")
        
        return "\n".join(lines)
    
    def format_mode_count_text(self, mode_count):
        """Format mode count text"""
        if mode_count == 0:
            return "No modes selected"
        elif mode_count == 1:
            return "1 mode selected"
        else:
            return f"{mode_count} modes selected"
    
    def format_bullet_point(self, text, indent=0):
        """Format text as bullet point with optional indentation"""
        indent_str = "  " * indent
        if text.startswith("•"):
            return f"{indent_str}{text}"
        else:
            return f"{indent_str}• {text}"
    
    def format_numbered_list(self, items, start_num=1):
        """Format items as numbered list"""
        if not items:
            return ""
        
        lines = []
        for i, item in enumerate(items, start_num):
            lines.append(f"  {i}. {item}")
        
        return "\n".join(lines)
    
    def truncate_text(self, text, max_length=50):
        """Truncate text if too long"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def capitalize_first_letter(self, text):
        """Capitalize first letter of text"""
        if not text:
            return text
        return text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    def format_duration(self, seconds):
        """Format duration from seconds to readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            if remaining_seconds == 0:
                return f"{minutes}m"
            else:
                return f"{minutes}m {remaining_seconds}s"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            if remaining_minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h {remaining_minutes}m"
    
    def format_file_size(self, size_bytes):
        """Format file size to human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def format_percentage(self, value, total, decimal_places=1):
        """Format percentage"""
        if total == 0:
            return "0%"
        
        percentage = (value / total) * 100
        return f"{percentage:.{decimal_places}f}%"
    
    def add_emoji_prefix(self, text, emoji="•"):
        """Add emoji prefix to text"""
        if text.startswith(emoji):
            return text
        return f"{emoji} {text}"
    
    def format_warning_text(self, text):
        """Format text as warning"""
        return f"⚠️ {text}"
    
    def format_success_text(self, text):
        """Format text as success"""
        return f"✅ {text}"
    
    def format_info_text(self, text):
        """Format text as info"""
        return f"ℹ️ {text}"
    
    def format_error_text(self, text):
        """Format text as error"""
        return f"❌ {text}"
    
    def wrap_text(self, text, width=50):
        """Wrap text to specified width"""
        import textwrap
        return textwrap.fill(text, width=width)
    
    def clean_text(self, text):
        """Clean text by removing extra whitespace"""
        if not text:
            return text
        
        # Remove extra whitespace and newlines
        cleaned = " ".join(text.split())
        return cleaned.strip()
    
    def format_summary_header(self, text):
        """Format text as summary header"""
        return f"📋 {text}"
    
    def format_section_text(self, text, section_type="info"):
        """Format text based on section type"""
        formatters = {
            "info": self.format_info_text,
            "warning": self.format_warning_text,
            "success": self.format_success_text,
            "error": self.format_error_text,
            "header": self.format_summary_header
        }
        
        formatter = formatters.get(section_type, lambda x: x)
        return formatter(text)
    
    def get_label_style_config(self, font_size=8):
        """Get consistent label style configuration"""
        return {
            'style': 'Body.TLabel',
            'font': ('Segoe UI', font_size)
        }
    
    def validate_text_length(self, text, max_length=100):
        """Validate text length and provide suggestions"""
        if not text:
            return True, ""
        
        if len(text) <= max_length:
            return True, ""
        else:
            return False, f"Text is too long ({len(text)} chars). Maximum: {max_length} chars."