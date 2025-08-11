# app/src/automation/reports/report_modules/report_writer.py
"""
Report Writer Module
Handles writing report to file
"""

import os

class ReportWriter:
    """Writes report content to file"""
    
    def write_report(self, lines, output_folder):
        """
        Write report lines to file
        
        Args:
            lines: List of report lines
            output_folder: Output folder path
            
        Returns:
            Path to written report or None on error
        """
        # REPLACE EVERYTHING IN THIS METHOD WITH:
        
        # CRITICAL FIX: Ensure we save in the output_folder, not temp
        if not output_folder or output_folder == '.':
            print(f"⚠️ Invalid output folder: '{output_folder}', using current directory")
            output_folder = os.getcwd()
        
        # Ensure the folder exists
        if not os.path.exists(output_folder):
            print(f"⚠️ Output folder doesn't exist: {output_folder}")
            return None
        
        # Build the report path - MUST be in output_folder
        report_path = os.path.join(output_folder, "processing_breakdown.txt")
        
        print(f"📝 Writing breakdown report to: {report_path}")
        
        # Join all lines
        report_content = "\n".join(lines)
        
        try:
            # Write the report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Verify the file was created
            if os.path.exists(report_path):
                file_size = os.path.getsize(report_path)
                print(f"✅ Breakdown report generated: {report_path} ({file_size} bytes)")
                return report_path
            else:
                print(f"❌ Report file was not created at: {report_path}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating breakdown report: {e}")
            import traceback
            traceback.print_exc()
            return None