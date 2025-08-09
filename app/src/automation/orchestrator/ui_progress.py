# app/src/automation/orchestrator/ui_progress.py
"""
UI Progress Module  
Handles project name updates and progress tracking
Split from ui_integration.py for better organization
"""

import time

class UIProgress:
    """Handles project name updates and progress management"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def check_and_update_project_name(self, progress_callback):
        """Check for and update project name from various sources"""
        progress_callback(15, "🔍 Fetching Data from Trello...")
        time.sleep(0.5)
        
        print(f"\n🔍 CHECKING FOR UPDATED PROJECT NAME:")
        
        # Initialize tracking
        final_project_name = None
        sources_checked = []
        name_changed = False
        
        # Check all sources
        final_project_name, sources_checked, name_changed = self._check_all_name_sources()
        
        # Debug output
        self._print_debug_info(sources_checked, final_project_name, name_changed)
        
        # Update project info if needed
        self._update_project_info_if_needed(final_project_name)
        
        return final_project_name
    
    def _check_all_name_sources(self):
        """Check all possible sources for updated project name"""
        final_project_name = None
        sources_checked = []
        name_changed = False
        
        # Source 1: Direct orchestrator attribute
        if (hasattr(self.orchestrator, 'updated_project_name') and 
            self.orchestrator.updated_project_name and 
            self.orchestrator.updated_project_name.strip() != ''):
            
            final_project_name = self.orchestrator.updated_project_name.strip()
            sources_checked.append(f"✅ orchestrator.updated_project_name: '{final_project_name}'")
            name_changed = True
        else:
            sources_checked.append("❌ orchestrator.updated_project_name: Not set or empty")
        
        # Source 2: Dialog controller
        if (not final_project_name and 
            hasattr(self.orchestrator, 'dialog_controller') and 
            self.orchestrator.dialog_controller):
            
            if (hasattr(self.orchestrator.dialog_controller, 'updated_project_name') and 
                self.orchestrator.dialog_controller.updated_project_name and
                self.orchestrator.dialog_controller.updated_project_name.strip() != ''):
                
                final_project_name = self.orchestrator.dialog_controller.updated_project_name.strip()
                sources_checked.append(f"✅ dialog_controller.updated_project_name: '{final_project_name}'")
                name_changed = True
            else:
                sources_checked.append("❌ dialog_controller.updated_project_name: Not set or empty")
        else:
            sources_checked.append("❌ dialog_controller: Not available")
        
        # Source 3: Confirmation data
        if (not final_project_name and 
            hasattr(self.orchestrator, 'confirmation_data') and 
            self.orchestrator.confirmation_data):
            
            if (hasattr(self.orchestrator.confirmation_data, 'project_name') and
                self.orchestrator.confirmation_data.project_name.strip() != ''):
                
                # Check if it's different from original
                original_name = self.orchestrator.project_info.get('project_name', '')
                ui_name = self.orchestrator.confirmation_data.project_name.strip()
                
                if ui_name != original_name:
                    final_project_name = ui_name
                    sources_checked.append(f"✅ confirmation_data.project_name: '{final_project_name}' (changed from '{original_name}')")
                    name_changed = True
                else:
                    sources_checked.append(f"ℹ️ confirmation_data.project_name: '{ui_name}' (same as original)")
            else:
                sources_checked.append("❌ confirmation_data.project_name: Not available")
        else:
            sources_checked.append("❌ confirmation_data: Not available")
        
        # Source 4: Fallback to original
        if not final_project_name:
            final_project_name = self.orchestrator.project_info['project_name']
            sources_checked.append(f"🔄 original project_info.project_name: '{final_project_name}' (fallback)")
        
        return final_project_name, sources_checked, name_changed
    
    def _print_debug_info(self, sources_checked, final_project_name, name_changed):
        """Print debug information about name sources"""
        print(f"🔍 PROJECT NAME SOURCES CHECKED:")
        for source in sources_checked:
            print(f"   {source}")
        
        print(f"🎯 FINAL PROJECT NAME DETERMINED: '{final_project_name}'")
        if name_changed:
            print(f"🔄 PROJECT NAME WAS CHANGED BY USER")
        else:
            print(f"ℹ️ PROJECT NAME UNCHANGED FROM ORIGINAL")
    
    def _update_project_info_if_needed(self, final_project_name):
        """Update project info if name has changed"""
        original_name = self.orchestrator.project_info['project_name']
        
        if final_project_name != original_name:
            print(f"\n🔄 UPDATING PROJECT_INFO:")
            print(f"   FROM: '{original_name}'")
            print(f"   TO:   '{final_project_name}'")
            
            self.orchestrator.project_info['project_name'] = final_project_name
            print(f"✅ PROJECT_INFO UPDATED SUCCESSFULLY")
            
            # Verify the update
            if self.orchestrator.project_info['project_name'] == final_project_name:
                print(f"✅ VERIFICATION: project_info now contains '{self.orchestrator.project_info['project_name']}'")
            else:
                print(f"❌ ERROR: project_info update failed!")
        else:
            print(f"ℹ️ NO PROJECT NAME CHANGE NEEDED")