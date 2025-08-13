# app/src/automation/workflow_ui_components/confirmation_tab/project_section/data_helpers.py
"""
Data Helpers - Data Manipulation Utilities
Handles data processing and validation for project section
"""

class DataHelpers:
    """Handles data manipulation and validation"""
    
    def __init__(self, project_section):
        self.ps = project_section
    
    def update_project_name(self, new_name):
        """Update project name and related data"""
        if new_name != self.ps.data.project_name:
            print(f"📝 Project name changed: '{self.ps.data.project_name}' → '{new_name}'")
            old_name = self.ps.data.project_name
            self.ps.data.project_name = new_name
            
            # Update output location if it exists
            if hasattr(self.ps.data, 'output_location') and self.ps.data.output_location:
                self.ps.data.output_location = self.ps.data.output_location.replace(old_name, new_name)
                
            # Refresh dependent UI sections
            if hasattr(self.ps.main_tab, 'refresh_output_location'):
                self.ps.main_tab.refresh_output_location()
                
            if hasattr(self.ps.main_tab, 'refresh_summary'):
                self.ps.main_tab.refresh_summary()
    
    def update_account(self, account_code):
        """Update account code and related data"""
        if account_code != getattr(self.ps.data, 'account', None):
            print(f"🔄 Account changed to: {account_code}")
            self.ps.data.account = account_code
            
            # Refresh dependent UI sections
            if hasattr(self.ps.main_tab, 'refresh_summary'):
                self.ps.main_tab.refresh_summary()
                
            if hasattr(self.ps.main_tab, 'refresh_output_location'):
                self.ps.main_tab.refresh_output_location()
    
    def update_platform(self, platform_code):
        """Update platform code and related data"""
        if platform_code != getattr(self.ps.data, 'platform', None):
            print(f"🔄 Platform changed to: {platform_code}")
            self.ps.data.platform = platform_code
            
            # Refresh dependent UI sections
            if hasattr(self.ps.main_tab, 'refresh_summary'):
                self.ps.main_tab.refresh_summary()
                
            if hasattr(self.ps.main_tab, 'refresh_output_location'):
                self.ps.main_tab.refresh_output_location()
    
    def update_processing_modes(self, selected_modes):
        """Update selected processing modes and related data"""
        print(f"🔄 Processing modes changed to: {selected_modes}")
        
        # Update data object with first selected mode for compatibility
        if selected_modes:
            self.ps.data.processing_mode = selected_modes[0]
        
        # Store all selected modes
        self.ps.data.selected_processing_modes = selected_modes
        
        # Refresh dependent UI sections
        if hasattr(self.ps.main_tab, 'refresh_summary'):
            self.ps.main_tab.refresh_summary()
            
        if hasattr(self.ps.main_tab, 'refresh_output_location'):
            self.ps.main_tab.refresh_output_location()
    
    def extract_code_from_selection(self, selection, separator=' - '):
        """Extract code from 'CODE - Description' format"""
        if selection and separator in selection:
            code = selection.split(separator)[0]
            print(f"DEBUG: Extracted code '{code}' from selection '{selection}'")
            return code
        return selection
    
    def validate_project_name(self, name):
        """Validate project name"""
        if not name or not name.strip():
            return False, "Project name cannot be empty"
        
        if len(name.strip()) < 3:
            return False, "Project name must be at least 3 characters"
        
        # Check for invalid characters (basic validation)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                return False, f"Project name cannot contain '{char}'"
        
        return True, ""
    
    def clean_project_name(self, name):
        """Clean project name by removing unnecessary prefixes/suffixes"""
        if not name:
            return name
        
        # Remove common prefixes
        prefixes_to_remove = ['GH ', 'Output/', 'Project: ']
        cleaned = name
        
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def get_data_summary(self):
        """Get summary of current data state"""
        return {
            'project_name': getattr(self.ps.data, 'project_name', 'Unknown'),
            'account': getattr(self.ps.data, 'account', 'Unknown'),
            'platform': getattr(self.ps.data, 'platform', 'Unknown'),
            'processing_mode': getattr(self.ps.data, 'processing_mode', 'Unknown'),
            'selected_processing_modes': getattr(self.ps.data, 'selected_processing_modes', []),
            'video_count': len(getattr(self.ps.data, 'client_videos', [])),
            'has_issues': bool(getattr(self.ps.data, 'issues', []))
        }
    
    def backup_data(self):
        """Create backup of current data state"""
        return {
            'project_name': getattr(self.ps.data, 'project_name', ''),
            'account': getattr(self.ps.data, 'account', ''),
            'platform': getattr(self.ps.data, 'platform', ''),
            'processing_mode': getattr(self.ps.data, 'processing_mode', ''),
            'selected_processing_modes': getattr(self.ps.data, 'selected_processing_modes', []),
            'output_location': getattr(self.ps.data, 'output_location', '')
        }
    
    def restore_data(self, backup):
        """Restore data from backup"""
        if not backup:
            return
        
        for key, value in backup.items():
            if hasattr(self.ps.data, key):
                setattr(self.ps.data, key, value)
                print(f"📄 Restored {key}: {value}")
    
    def sync_ui_with_data(self):
        """Synchronize UI controls with current data"""
        # Update project name
        if hasattr(self.ps.main_tab, 'project_name_var'):
            self.ps.main_tab.project_name_var.set(getattr(self.ps.data, 'project_name', ''))
        
        # Update account selection
        if hasattr(self.ps.main_tab, 'account_var'):
            account_selection = self.ps.dropdown_handlers.get_default_account_selection()
            self.ps.main_tab.account_var.set(account_selection)
        
        # Update platform selection
        if hasattr(self.ps.main_tab, 'platform_var'):
            platform_selection = self.ps.dropdown_handlers.get_default_platform_selection()
            self.ps.main_tab.platform_var.set(platform_selection)
        
        # Update processing modes
        selected_modes = getattr(self.ps.data, 'selected_processing_modes', [])
        if not selected_modes:
            selected_modes = [getattr(self.ps.data, 'processing_mode', 'save_only')]
        
        self.ps.mode_selector.set_selected_processing_modes(selected_modes)
        
        print("✅ UI synchronized with data")