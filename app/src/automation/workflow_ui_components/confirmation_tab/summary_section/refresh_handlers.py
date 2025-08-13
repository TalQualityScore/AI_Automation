# app/src/automation/workflow_ui_components/confirmation_tab/summary_section/refresh_handlers.py
"""
Refresh Handlers - Summary Section Refresh Logic
Handles all refresh operations and transitions updates for summary section
FIXED: Transitions checkbox updates summary immediately
"""

class RefreshHandlers:
    """Handles all refresh operations for summary section"""
    
    def __init__(self, summary_section):
        self.ss = summary_section  # Reference to main SummarySection
    
    def refresh(self):
        """ENHANCED: Refresh summary when settings change"""
        print("DEBUG: Summary refresh() called")
        try:
            self._update_summary_content()
            self._update_transitions_display()
            print("✅ Summary refreshed successfully")
        except Exception as e:
            print(f"❌ Error in summary refresh: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_with_modes(self, selected_modes):
        """ENHANCED: Refresh summary when modes change"""
        print(f"DEBUG: Summary refresh_with_modes({selected_modes}) called")
        
        try:
            # Update mode display if labels exist
            self._update_mode_display(selected_modes)
            
            # Update output display
            self._update_output_display(selected_modes)
            
            # Update estimated time
            self._update_time_display(selected_modes)
            
            # Update transitions display
            self._update_transitions_display()
            
            print(f"✅ Summary refreshed for {len(selected_modes)} modes")
            
        except Exception as e:
            print(f"❌ Error in refresh_with_modes: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_summary_content(self):
        """ENHANCED: Update all summary content including transitions"""
        print("DEBUG: Updating summary content...")
        
        # Clear existing content
        self._clear_summary_content()
        
        # Reset label references
        self._reset_label_references()
        
        # Get current data
        video_count = self.ss.data_extractors.get_video_count()
        selected_modes = self.ss.data_extractors.get_selected_modes()
        
        # Create video count display
        self._create_video_count_display(video_count)
        
        # Create mode display
        self._create_mode_display(selected_modes)
        
        # Create transitions display
        self._create_transitions_display()
        
        # Create output display
        self._create_output_display(selected_modes)
        
        # Create time display
        self._create_time_display(video_count, selected_modes)
        
        print("✅ Summary content updated")
    
    def _update_transitions_display(self):
        """NEW: Update transitions display in summary"""
        print("DEBUG: Updating transitions display...")
        
        try:
            # Remove existing transitions label if it exists
            if hasattr(self.ss, 'transitions_label') and self.ss.transitions_label:
                self.ss.transitions_label.destroy()
                self.ss.transitions_label = None
            
            # Create new transitions label
            transitions_enabled = self._get_transitions_setting()
            transition_text = "with smooth transitions" if transitions_enabled else "without transitions"
            
            # Create the label
            import tkinter as tk
            from tkinter import ttk
            
            self.ss.transitions_label = ttk.Label(
                self.ss.summary_frame, 
                text=f"• Processing type: {transition_text}",
                style='Body.TLabel', 
                font=('Segoe UI', 8)
            )
            self.ss.transitions_label.pack(anchor=tk.W)
            
            print(f"✅ Transitions display updated: {transition_text}")
            
        except Exception as e:
            print(f"❌ Error updating transitions display: {e}")
            # Create fallback label
            try:
                import tkinter as tk
                from tkinter import ttk
                
                self.ss.transitions_label = ttk.Label(
                    self.ss.summary_frame, 
                    text="• Processing type: with smooth transitions",
                    style='Body.TLabel', 
                    font=('Segoe UI', 8)
                )
                self.ss.transitions_label.pack(anchor=tk.W)
                print("✅ Fallback transitions label created")
            except Exception as fallback_error:
                print(f"❌ Fallback transitions label failed: {fallback_error}")
    
    def _update_mode_display(self, selected_modes):
        """Update mode display labels"""
        if not hasattr(self.ss, 'mode_label') or not self.ss.mode_label:
            return
        
        try:
            if len(selected_modes) > 1:
                # Multi-mode display
                self.ss.mode_label.config(text=f"• Processing modes: {len(selected_modes)} selected")
                
                # Update detailed mode list if exists
                if hasattr(self.ss, 'mode_details') and self.ss.mode_details:
                    details_text = ""
                    for i, mode in enumerate(selected_modes, 1):
                        mode_display = self.ss.mode_formatters.get_mode_display(mode)
                        details_text += f"  {i}. {mode_display}\n"
                    self.ss.mode_details.config(text=details_text.strip())
            else:
                # Single mode display
                mode_display = self.ss.mode_formatters.get_mode_display(selected_modes[0] if selected_modes else 'save_only')
                self.ss.mode_label.config(text=f"• Processing type: {mode_display}")
                
                # Clear detailed mode list for single mode
                if hasattr(self.ss, 'mode_details') and self.ss.mode_details:
                    self.ss.mode_details.config(text="")
            
            print(f"✅ Mode display updated for {len(selected_modes)} modes")
            
        except Exception as e:
            print(f"❌ Error updating mode display: {e}")
    
    def _update_output_display(self, selected_modes):
        """Update output display labels"""
        if not hasattr(self.ss, 'output_label') or not self.ss.output_label:
            return
        
        try:
            if len(selected_modes) > 1:
                output_text = f"{len(selected_modes)} separate folders will be created"
            else:
                output_text = "1 folder will be created"
            
            self.ss.output_label.config(text=f"• Output: {output_text}")
            print(f"✅ Output display updated: {output_text}")
            
        except Exception as e:
            print(f"❌ Error updating output display: {e}")
    
    def _update_time_display(self, selected_modes):
        """Update estimated time display"""
        if not hasattr(self.ss, 'time_label') or not self.ss.time_label:
            return
        
        try:
            video_count = self.ss.data_extractors.get_video_count()
            estimated_time = self.ss.time_calculator.calculate_estimated_time(video_count, selected_modes)
            
            self.ss.time_label.config(text=f"• Estimated processing time: {estimated_time}")
            print(f"✅ Time display updated: {estimated_time}")
            
        except Exception as e:
            print(f"❌ Error updating time display: {e}")
    
    def _get_transitions_setting(self):
        """Get current transitions setting"""
        try:
            if hasattr(self.ss.main_tab, 'use_transitions'):
                return self.ss.main_tab.use_transitions.get()
            else:
                print("⚠️ Transitions variable not available, defaulting to True")
                return True
        except Exception as e:
            print(f"⚠️ Error getting transitions setting: {e}")
            return True
    
    def _clear_summary_content(self):
        """Clear existing summary content"""
        try:
            if hasattr(self.ss, 'summary_frame'):
                for widget in self.ss.summary_frame.winfo_children():
                    widget.destroy()
                print("✅ Summary content cleared")
        except Exception as e:
            print(f"❌ Error clearing summary content: {e}")
    
    def _reset_label_references(self):
        """Reset all label references"""
        self.ss.video_label = None
        self.ss.mode_label = None
        self.ss.mode_details = None
        self.ss.transitions_label = None
        self.ss.output_label = None
        self.ss.time_label = None
        print("✅ Label references reset")
    
    def _create_video_count_display(self, video_count):
        """Create video count display"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            self.ss.video_label = ttk.Label(
                self.ss.summary_frame, 
                text=f"• {video_count} client video{'s' if video_count != 1 else ''} will be processed",
                style='Body.TLabel', 
                font=('Segoe UI', 8)
            )
            self.ss.video_label.pack(anchor=tk.W)
            print(f"✅ Video count display created: {video_count} videos")
            
        except Exception as e:
            print(f"❌ Error creating video count display: {e}")
    
    def _create_mode_display(self, selected_modes):
        """Create mode display based on selection"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            if len(selected_modes) == 1:
                # Single mode display
                mode_display = self.ss.mode_formatters.get_mode_display(selected_modes[0])
                self.ss.mode_label = ttk.Label(
                    self.ss.summary_frame, 
                    text=f"• Processing type: {mode_display}",
                    style='Body.TLabel', 
                    font=('Segoe UI', 8)
                )
                self.ss.mode_label.pack(anchor=tk.W)
                
                # Show endpoint if not save_only
                if selected_modes[0] != 'save_only':
                    endpoint = self.ss.mode_formatters.get_endpoint_from_mode(selected_modes[0])
                    endpoint_label = ttk.Label(
                        self.ss.summary_frame, 
                        text=f"• Videos will be connected to: {endpoint}",
                        style='Body.TLabel', 
                        font=('Segoe UI', 8)
                    )
                    endpoint_label.pack(anchor=tk.W)
            else:
                # Multi-mode display
                self.ss.mode_label = ttk.Label(
                    self.ss.summary_frame, 
                    text=f"• Processing modes: {len(selected_modes)} selected",
                    style='Body.TLabel', 
                    font=('Segoe UI', 8)
                )
                self.ss.mode_label.pack(anchor=tk.W)
                
                # Create detailed mode list
                details_text = ""
                for i, mode in enumerate(selected_modes, 1):
                    mode_display = self.ss.mode_formatters.get_mode_display(mode)
                    details_text += f"  {i}. {mode_display}\n"
                
                if details_text:
                    self.ss.mode_details = ttk.Label(
                        self.ss.summary_frame, 
                        text=details_text.strip(),
                        style='Body.TLabel', 
                        font=('Segoe UI', 8)
                    )
                    self.ss.mode_details.pack(anchor=tk.W)
            
            print(f"✅ Mode display created for {len(selected_modes)} modes")
            
        except Exception as e:
            print(f"❌ Error creating mode display: {e}")
    
    def _create_transitions_display(self):
        """Create transitions display"""
        self._update_transitions_display()
    
    def _create_output_display(self, selected_modes):
        """Create output display"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            if len(selected_modes) > 1:
                output_text = f"{len(selected_modes)} separate folders will be created"
            else:
                output_text = "1 folder will be created"
            
            self.ss.output_label = ttk.Label(
                self.ss.summary_frame, 
                text=f"• Output: {output_text}",
                style='Body.TLabel', 
                font=('Segoe UI', 8)
            )
            self.ss.output_label.pack(anchor=tk.W)
            print(f"✅ Output display created: {output_text}")
            
        except Exception as e:
            print(f"❌ Error creating output display: {e}")
    
    def _create_time_display(self, video_count, selected_modes):
        """Create estimated time display"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            estimated_time = self.ss.time_calculator.calculate_estimated_time(video_count, selected_modes)
            
            self.ss.time_label = ttk.Label(
                self.ss.summary_frame, 
                text=f"• Estimated processing time: {estimated_time}",
                style='Body.TLabel', 
                font=('Segoe UI', 8)
            )
            self.ss.time_label.pack(anchor=tk.W)
            print(f"✅ Time display created: {estimated_time}")
            
        except Exception as e:
            print(f"❌ Error creating time display: {e}")
    
    def force_refresh_transitions(self):
        """Force refresh of transitions display (called from processing section)"""
        print("🔄 Force refreshing transitions display...")
        self._update_transitions_display()
    
    def refresh_data(self, new_data):
        """Refresh with new data"""
        print("📄 Refreshing summary with new data...")
        try:
            self.ss.data = new_data
            self.refresh()
            print("✅ Summary data refreshed")
        except Exception as e:
            print(f"❌ Error refreshing summary data: {e}")