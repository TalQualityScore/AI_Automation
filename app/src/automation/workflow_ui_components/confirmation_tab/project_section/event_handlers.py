# app/src/automation/workflow_ui_components/confirmation_tab/project_section/event_handlers.py
"""
Event Handlers - UI Event Callbacks
Handles all user interaction events for project section
"""

class EventHandlers:
    """Handles all UI event callbacks"""
    
    def __init__(self, project_section):
        self.ps = project_section
    
    def on_project_name_change(self, event=None):
        """Handle project name changes"""
        try:
            new_name = self.ps.main_tab.project_name_var.get()
            
            # Validate the new name
            is_valid, error_message = self.ps.data_helpers.validate_project_name(new_name)
            
            if is_valid:
                # Update data if name is valid
                self.ps.data_helpers.update_project_name(new_name)
            else:
                print(f"⚠️ Invalid project name: {error_message}")
                # Could show user feedback here
                
        except Exception as e:
            print(f"⚠️ Error in project name change: {e}")
    
    def safe_account_change(self):
        """Safe account change handler with error handling"""
        try:
            selected = self.ps.main_tab.account_var.get()
            if not selected:
                print("⚠️ No account selected")
                return
            
            account_code = self.ps.data_helpers.extract_code_from_selection(selected)
            if account_code:
                # Validate account code
                if self.ps.dropdown_handlers.validate_account_code(account_code):
                    self.ps.data_helpers.update_account(account_code)
                else:
                    print(f"⚠️ Invalid account code: {account_code}")
            else:
                print("⚠️ Could not extract account code from selection")
                
        except Exception as e:
            print(f"⚠️ Account change error (safely handled): {e}")
    
    def on_platform_change(self, event=None):
        """Handle platform change"""
        try:
            selected = self.ps.main_tab.platform_var.get()
            if not selected:
                print("⚠️ No platform selected")
                return
            
            platform_code = self.ps.data_helpers.extract_code_from_selection(selected)
            if platform_code:
                # Validate platform code
                if self.ps.dropdown_handlers.validate_platform_code(platform_code):
                    self.ps.data_helpers.update_platform(platform_code)
                else:
                    print(f"⚠️ Invalid platform code: {platform_code}")
            else:
                print("⚠️ Could not extract platform code from selection")
                
        except Exception as e:
            print(f"⚠️ Platform change error: {e}")
    
    def on_processing_mode_change(self, event=None):
        """Handle processing mode changes (now multi-select)"""
        try:
            selected_modes = self.ps.mode_selector.get_selected_processing_modes()
            
            # Validate selected modes
            valid_modes = []
            for mode in selected_modes:
                if self.ps.mode_selector.validate_mode(mode):
                    valid_modes.append(mode)
                else:
                    print(f"⚠️ Invalid mode '{mode}' ignored")
            
            if valid_modes:
                self.ps.data_helpers.update_processing_modes(valid_modes)
            else:
                print("⚠️ No valid processing modes selected")
                
        except Exception as e:
            print(f"⚠️ Processing mode change error: {e}")
    
    def on_field_focus_in(self, event=None):
        """Handle field gaining focus"""
        try:
            if event and event.widget:
                print(f"DEBUG: Field gained focus: {event.widget}")
                # Could add focus styling here
        except Exception as e:
            print(f"⚠️ Focus in error: {e}")
    
    def on_field_focus_out(self, event=None):
        """Handle field losing focus"""
        try:
            if event and event.widget:
                print(f"DEBUG: Field lost focus: {event.widget}")
                # Could add validation here
        except Exception as e:
            print(f"⚠️ Focus out error: {e}")
    
    def on_validation_error(self, field_name, error_message):
        """Handle validation errors"""
        print(f"❌ Validation error in {field_name}: {error_message}")
        
        # Could show user notification here
        # For now, just log the error
        
        # Store error for potential UI display
        if not hasattr(self.ps.data, 'validation_errors'):
            self.ps.data.validation_errors = {}
        
        self.ps.data.validation_errors[field_name] = error_message
    
    def clear_validation_error(self, field_name):
        """Clear validation error for field"""
        if hasattr(self.ps.data, 'validation_errors') and field_name in self.ps.data.validation_errors:
            del self.ps.data.validation_errors[field_name]
            print(f"✅ Cleared validation error for {field_name}")
    
    def validate_all_fields(self):
        """Validate all fields and return results"""
        errors = {}
        
        # Validate project name
        project_name = getattr(self.ps.data, 'project_name', '')
        is_valid, error_msg = self.ps.data_helpers.validate_project_name(project_name)
        if not is_valid:
            errors['project_name'] = error_msg
        
        # Validate account
        account = getattr(self.ps.data, 'account', '')
        if not self.ps.dropdown_handlers.validate_account_code(account):
            errors['account'] = f"Invalid account code: {account}"
        
        # Validate platform
        platform = getattr(self.ps.data, 'platform', '')
        if not self.ps.dropdown_handlers.validate_platform_code(platform):
            errors['platform'] = f"Invalid platform code: {platform}"
        
        # Validate processing modes
        modes = getattr(self.ps.data, 'selected_processing_modes', [])
        if not modes:
            errors['processing_modes'] = "At least one processing mode must be selected"
        else:
            invalid_modes = [mode for mode in modes if not self.ps.mode_selector.validate_mode(mode)]
            if invalid_modes:
                errors['processing_modes'] = f"Invalid modes: {', '.join(invalid_modes)}"
        
        return errors
    
    def on_data_change(self, field_name, old_value, new_value):
        """Handle any data change for logging/tracking"""
        print(f"📝 Data changed - {field_name}: '{old_value}' → '{new_value}'")
        
        # Could add change tracking here
        if not hasattr(self.ps.data, 'change_history'):
            self.ps.data.change_history = []
        
        self.ps.data.change_history.append({
            'field': field_name,
            'old_value': old_value,
            'new_value': new_value,
            'timestamp': __import__('time').time()
        })
        
        # Keep only last 10 changes
        if len(self.ps.data.change_history) > 10:
            self.ps.data.change_history = self.ps.data.change_history[-10:]
    
    def reset_to_defaults(self):
        """Reset all fields to their default values"""
        try:
            print("🔄 Resetting project section to defaults...")
            
            # Reset to detected values or fallbacks
            default_account = 'TR'
            default_platform = 'FB'
            default_mode = 'save_only'
            
            # Update data
            self.ps.data.account = default_account
            self.ps.data.platform = default_platform
            self.ps.data.processing_mode = default_mode
            self.ps.data.selected_processing_modes = [default_mode]
            
            # Sync UI
            self.ps.data_helpers.sync_ui_with_data()
            
            print("✅ Project section reset to defaults")
            
        except Exception as e:
            print(f"⚠️ Error resetting to defaults: {e}")