# app/src/automation/orchestrator/processing/coordinator_modules/summary_reporter.py
"""
Summary Reporter Module
Generates summary reports for file operations
"""

class SummaryReporter:
    """Generates summary reports for file organization"""
    
    def generate_summary(self, moved_count, failed_moves, dest_path):
        """
        Generate and print summary report
        
        Args:
            moved_count: Number of successfully moved files
            failed_moves: List of (filename, error) tuples
            dest_path: Destination path
        """
        print(f"📊 FILE ORGANIZATION SUMMARY:")
        print(f"   ✅ Successfully moved: {moved_count} videos")
        
        if failed_moves:
            print(f"   ❌ Failed moves: {len(failed_moves)}")
            for filename, error in failed_moves:
                print(f"      - {filename}: {error}")
        
        print(f"   📁 Destination: {dest_path}")
    
    def generate_detailed_report(self, operation_stats):
        """
        Generate detailed operation report
        
        Args:
            operation_stats: Dictionary with operation statistics
            
        Returns:
            Formatted report string
        """
        report_lines = [
            "=" * 60,
            "FILE ORGANIZATION OPERATION REPORT",
            "=" * 60,
            "",
            f"Videos Found: {operation_stats.get('videos_found', 0)}",
            f"Videos Moved: {operation_stats.get('videos_moved', 0)}",
            f"Failed Moves: {operation_stats.get('failed_moves', 0)}",
            f"Directories Cleaned: {operation_stats.get('dirs_cleaned', 0)}",
            ""
        ]
        
        if operation_stats.get('errors'):
            report_lines.append("Errors:")
            for error in operation_stats['errors']:
                report_lines.append(f"  - {error}")
        
        return "\n".join(report_lines)