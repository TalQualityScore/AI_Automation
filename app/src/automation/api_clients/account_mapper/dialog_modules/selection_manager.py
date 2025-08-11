# app/src/automation/api_clients/account_mapper/dialog_modules/selection_manager.py
"""
Selection Manager Module
Manages user selections and validation
"""

class SelectionManager:
    """Manages account and platform selections"""
    
    def __init__(self):
        self.account_var = None
        self.platform_var = None
        self.result = {
            "account": None, 
            "platform": None, 
            "action": None, 
            "done": False
        }
    
    def set_variables(self, account_var, platform_var):
        """Set the tkinter variables for selections"""
        self.account_var = account_var
        self.platform_var = platform_var
    
    def process_selection(self):
        """Process user selection when Apply is clicked"""
        account_selection = self.account_var.get()
        platform_selection = self.platform_var.get()
        
        if account_selection and platform_selection:
            # Extract codes from "CODE - Name" format
            account_code = account_selection.split(' - ')[0]
            platform_code = platform_selection.split(' - ')[0]
            
            self.result["account"] = account_code
            self.result["platform"] = platform_code
            self.result["action"] = "apply"
            self.result["done"] = True
            
            print(f"✅ User applied: {account_code}, {platform_code}")
            return True
        
        return False
    
    def handle_window_close(self):
        """Handle window close event"""
        self.result["account"] = None
        self.result["platform"] = None
        self.result["action"] = "exit_program"
        self.result["done"] = True
        print(f"❌ User chose to exit program instead of selecting")
    
    def get_result(self):
        """Get the final result"""
        return self.result
    
    def is_done(self):
        """Check if selection is complete"""
        return self.result["done"]