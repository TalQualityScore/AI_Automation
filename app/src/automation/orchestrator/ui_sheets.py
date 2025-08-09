# app/src/automation/orchestrator/ui_sheets.py
"""
UI Sheets Module
Handles Google Sheets updates and report generation
Split from ui_integration.py for better organization
"""

import os
import time

class UISheets:
    """Handles Google Sheets updates and reporting"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def update_google_sheets(self, processed_files, project_info, creds, project_paths, 
                            routing_name, column1_name, progress_callback):
        """Update Google Sheets with processing results"""
        progress_callback(90, "📊 Updating Google Sheets...")
        
        print(f"\n📊 GOOGLE SHEETS UPDATE STRATEGY:")
        print(f"   🔍 Routing name (find worksheet): '{routing_name}'")
        print(f"   📁 Column 1 name (display in sheet): '{column1_name}'")
        print(f"   📊 Detected Account: '{self.orchestrator.detected_account_code}'")
        print(f"   📊 Detected Platform: '{self.orchestrator.detected_platform_code}'")
        
        # Call finalize with both names
        self.finalize_with_correct_names(
            processed_files, project_info, creds, project_paths, 
            routing_name, column1_name
        )
    
    def finalize_with_correct_names(self, processed_files, project_info, creds, project_paths, 
                                   routing_name, column1_name):
        """FIXED: Use routing name for worksheet selection, folder name for column 1"""
        
        print(f"\n--- Step 5: Logging to Google Sheets ---")
        print(f"🔍 Routing name (worksheet lookup): '{routing_name}'")
        print(f"📁 Column 1 name (folder display): '{column1_name}'")
        
        if not processed_files:
            print("No files were processed, skipping log.")
            return
        
        data_to_write = [
            [pf['version'], pf['description'], pf['output_name']]
            for pf in processed_files
        ]
        
        def write_results():
            # Use detected account/platform for precise worksheet routing
            if (hasattr(self.orchestrator, 'detected_account_code') and 
                hasattr(self.orchestrator, 'detected_platform_code') and
                self.orchestrator.detected_account_code != 'UNKNOWN' and
                self.orchestrator.detected_platform_code != 'UNKNOWN'):
                
                print(f"✅ Using DETECTED account/platform for routing:")
                print(f"   Account: '{self.orchestrator.detected_account_code}'")
                print(f"   Platform: '{self.orchestrator.detected_platform_code}'")
                
                try:
                    from ..api_clients import GoogleSheetsClient, AccountMapper
                    
                    sheets_client = GoogleSheetsClient(creds)
                    mapper = AccountMapper()
                    
                    worksheet_titles = sheets_client.get_worksheet_names()
                    print(f"📋 Available worksheets: {worksheet_titles}")
                    
                    target_worksheet = mapper.find_exact_worksheet_match(
                        worksheet_titles, 
                        self.orchestrator.detected_account_code, 
                        self.orchestrator.detected_platform_code
                    )
                    
                    if target_worksheet:
                        print(f"✅ EXACT WORKSHEET MATCH: '{target_worksheet}'")
                        error, _ = sheets_client.write_to_sheet_with_custom_name(
                            target_worksheet,
                            column1_name,
                            data_to_write, 
                            creds
                        )
                    else:
                        print(f"❌ NO EXACT WORKSHEET FOUND")
                        raise Exception(f"No worksheet found for {self.orchestrator.detected_account_code} - {self.orchestrator.detected_platform_code}")
                        
                except Exception as worksheet_error:
                    print(f"❌ WORKSHEET ROUTING ERROR: {worksheet_error}")
                    raise Exception(f"Google Sheets routing failed: {worksheet_error}")
                    
            else:
                print(f"⚠️ NO DETECTED ACCOUNT/PLATFORM CODES")
                print(f"🆘 USING EMERGENCY FALLBACK ROUTING")
                from ..api_clients import write_to_google_sheets_with_custom_name
                error, _ = write_to_google_sheets_with_custom_name(
                    routing_name, column1_name, data_to_write, creds
                )
            
            if error:
                print(f"❌ GOOGLE SHEETS WRITE ERROR: {error}")
                raise Exception(f"Failed to write to Google Sheets: {error}")
            
            print(f"✅ GOOGLE SHEETS WRITE SUCCESSFUL")
            return "Results logged successfully"
        
        # Execute with monitoring
        result = self.orchestrator.monitor.execute_with_activity_monitoring(
            write_results,
            "Google Sheets Logging",
            no_activity_timeout=120
        )
        print(result)
        
        # Cleanup
        self._cleanup_temp_files()
    
    def generate_breakdown_report(self, processed_files, project_paths, use_transitions, progress_callback):
        """Generate breakdown report"""
        progress_callback(95, "📝 Generating breakdown report...")
        
        # Calculate duration
        duration_seconds = time.time() - self.orchestrator.start_time
        if duration_seconds < 60:
            duration_display = f"{duration_seconds:.1f} seconds"
        else:
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            duration_display = f"{minutes}m {seconds}s"
        
        try:
            from ..reports.breakdown_report import generate_breakdown_report
            
            # Enhance processed files with video paths
            enhanced_files = []
            for file_info in processed_files:
                enhanced_info = file_info.copy()
                enhanced_info['client_video_path'] = file_info.get('client_video_path', '')
                enhanced_info['connector_path'] = file_info.get('connector_path', '')
                enhanced_info['quiz_path'] = file_info.get('quiz_path', '')
                enhanced_files.append(enhanced_info)
            
            # Generate the report
            report_path = generate_breakdown_report(
                enhanced_files,
                project_paths['project_root'],
                duration_display,
                use_transitions
            )
            
            if report_path:
                print(f"✅ Breakdown report generated: {report_path}")
        
        except ImportError:
            print(f"⚠️ Breakdown report module not found - skipping report generation")
        except Exception as e:
            print(f"⚠️ Could not generate breakdown report: {e}")
    
    def _cleanup_temp_files(self):
        """Cleanup temporary files"""
        print("\n--- Step 6: Cleaning up temporary files ---")
        temp_dir = "temp_downloads"
        
        if os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                print(f"✅ Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                print(f"⚠️ Warning: Could not remove temp directory {temp_dir}: {e}")
        else:
            print(f"✅ No temporary files to clean up (temp directory {temp_dir} does not exist)")
        
        print("✅ Finalization completed successfully")