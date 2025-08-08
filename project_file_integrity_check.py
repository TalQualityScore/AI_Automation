# project_file_integrity_check.py
"""
AI Automation Suite - Project File Integrity Checker
Checks for required files, identifies unnecessary files, and validates project structure
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

class ProjectFileChecker:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.results = {
            "required_missing": [],
            "required_present": [],
            "unnecessary_files": [],
            "archived_files": [],
            "duplicate_files": [],
            "temp_files": [],
            "backup_files": []
        }
        
    def get_required_files(self):
        """Define all required files for the project"""
        return {
            # Main entry point
            "main": [
                "local_automation.py",
                "requirements.txt",
                ".env",  # Local only
                "credentials.json"  # Local only
            ],
            
            # Core automation modules
            "automation_core": [
                "app/src/automation/__init__.py",
                "app/src/automation/video_processor.py",
                "app/src/automation/workflow_utils.py",
                "app/src/automation/error_handler.py",
                "app/src/automation/timing_report.py",
                "app/src/automation/monitor.py"
            ],
            
            # API clients
            "api_clients": [
                "app/src/automation/api_clients/__init__.py",
                "app/src/automation/api_clients/trello_client.py",
                "app/src/automation/api_clients/google_drive.py",
                "app/src/automation/api_clients/google_sheets.py",
                "app/src/automation/api_clients/account_mapper.py"
            ],
            
            # Orchestrator
            "orchestrator": [
                "app/src/automation/orchestrator/__init__.py",
                "app/src/automation/orchestrator/core.py",
                "app/src/automation/orchestrator/processing_steps.py",
                "app/src/automation/orchestrator/ui_integration.py",
                "app/src/automation/orchestrator/error_handling.py"
            ],
            
            # UI Components
            "ui_components": [
                "app/src/automation/workflow_ui_components/__init__.py",
                "app/src/automation/workflow_ui_components/theme.py",
                "app/src/automation/workflow_ui_components/confirmation_tab.py",
                "app/src/automation/workflow_ui_components/processing_tab.py",
                "app/src/automation/workflow_ui_components/results_tab.py",
                "app/src/automation/workflow_ui_components/notification_popup.py",
                "app/src/automation/workflow_ui_components/helpers.py"
            ],
            
            # Dialog management
            "dialog": [
                "app/src/automation/workflow_dialog/__init__.py",
                "app/src/automation/workflow_dialog/dialog_controller.py",
                "app/src/automation/workflow_dialog/tab_management.py",
                "app/src/automation/workflow_dialog/notification_manager.py",
                "app/src/automation/workflow_dialog/processing_thread.py",
                "app/src/automation/workflow_dialog/helpers.py"
            ],
            
            # Data models
            "data_models": [
                "app/src/automation/workflow_data_models.py"
            ],
            
            # Naming system
            "naming": [
                "app/src/naming/__init__.py",
                "app/src/naming/name_generator.py",
                "app/src/naming/project_parser.py",
                "app/src/naming/core_naming.py"
            ],
            
            # Transitions (if implemented)
            "transitions": [
                "app/src/automation/transitions/__init__.py",
                "app/src/automation/transitions/transition_types.py",
                "app/src/automation/transitions/video_info.py",
                "app/src/automation/transitions/transition_builder.py",
                "app/src/automation/transitions/processor.py"
            ],
            
            # Reports (if implemented)
            "reports": [
                "app/src/automation/reports/__init__.py",
                "app/src/automation/reports/breakdown_report.py"
            ],
            
            # Assets
            "assets": [
                "app/assets/quiz_templates/__init__.py",
                "app/assets/connectors/__init__.py"
            ]
        }
    
    def get_unnecessary_patterns(self):
        """Patterns for files that should not be in the project"""
        return {
            "backup_patterns": [
                "*_backup.py",
                "*_old.py",
                "*_BACKUP_*",
                "*.bak",
                "*~"
            ],
            "temp_patterns": [
                "*.tmp",
                "*.temp",
                "temp_*",
                "tmp_*",
                ".~*"
            ],
            "archive_patterns": [
                "*_archived.py",
                "*_ARCHIVED_*",
                "archive_*",
                "old_*"
            ],
            "duplicate_patterns": [
                "*_copy.py",
                "*_FULL.py",
                "*_IMPROVED.py",
                "*_UPDATED.py",
                "* (1).py",
                "* (2).py",
                "*_v2.py",
                "*_v3.py",
                "*_final.py",
                "*_new.py"
            ],
            "test_patterns": [
                "test_*.py",
                "*_test.py",
                "debug_*.py",
                "*_debug.py"
            ]
        }
    
    def check_required_files(self):
        """Check for presence of all required files"""
        print("\n" + "="*60)
        print("CHECKING REQUIRED FILES")
        print("="*60)
        
        all_required = []
        for category, files in self.get_required_files().items():
            all_required.extend(files)
        
        for file_path in all_required:
            full_path = self.project_root / file_path
            
            # Skip .env and credentials.json in the check as they're local only
            if file_path in ['.env', 'credentials.json']:
                if full_path.exists():
                    self.results["required_present"].append(file_path)
                    print(f"✅ [LOCAL] {file_path}")
                else:
                    print(f"⚠️ [LOCAL] {file_path} (not found - this is OK if not running locally)")
                continue
            
            if full_path.exists():
                self.results["required_present"].append(file_path)
                print(f"✅ {file_path}")
            else:
                self.results["required_missing"].append(file_path)
                print(f"❌ MISSING: {file_path}")
    
    def find_unnecessary_files(self):
        """Find backup, temp, archive, and duplicate files"""
        print("\n" + "="*60)
        print("CHECKING FOR UNNECESSARY FILES")
        print("="*60)
        
        patterns = self.get_unnecessary_patterns()
        
        # Walk through all Python files in the project
        for root, dirs, files in os.walk(self.project_root):
            # Skip virtual environments and cache directories
            dirs[:] = [d for d in dirs if d not in ['venv', 'env', '__pycache__', '.git', 'node_modules']]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_root)
                
                # Check backup patterns
                for pattern in patterns["backup_patterns"]:
                    if file_path.match(pattern):
                        self.results["backup_files"].append(str(relative_path))
                        print(f"🔄 BACKUP: {relative_path}")
                        break
                
                # Check temp patterns
                for pattern in patterns["temp_patterns"]:
                    if file_path.match(pattern):
                        self.results["temp_files"].append(str(relative_path))
                        print(f"🗑️ TEMP: {relative_path}")
                        break
                
                # Check archive patterns
                for pattern in patterns["archive_patterns"]:
                    if file_path.match(pattern):
                        self.results["archived_files"].append(str(relative_path))
                        print(f"📦 ARCHIVED: {relative_path}")
                        break
                
                # Check duplicate patterns
                for pattern in patterns["duplicate_patterns"]:
                    if file_path.match(pattern):
                        self.results["duplicate_files"].append(str(relative_path))
                        print(f"📑 DUPLICATE: {relative_path}")
                        break
    
    def check_project_structure(self):
        """Verify the project structure is correct"""
        print("\n" + "="*60)
        print("CHECKING PROJECT STRUCTURE")
        print("="*60)
        
        expected_dirs = [
            "app",
            "app/src",
            "app/src/automation",
            "app/src/automation/api_clients",
            "app/src/automation/orchestrator",
            "app/src/automation/workflow_ui_components",
            "app/src/automation/workflow_dialog",
            "app/src/naming",
            "app/assets",
            "app/assets/quiz_templates",
            "app/assets/connectors"
        ]
        
        for dir_path in expected_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                print(f"✅ Directory: {dir_path}")
            else:
                print(f"❌ MISSING Directory: {dir_path}")
    
    def check_for_orphaned_files(self):
        """Find Python files that aren't in the expected structure"""
        print("\n" + "="*60)
        print("CHECKING FOR ORPHANED FILES")
        print("="*60)
        
        # Get all Python files
        all_python_files = []
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['venv', 'env', '__pycache__', '.git']]
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    relative_path = str(file_path.relative_to(self.project_root))
                    all_python_files.append(relative_path)
        
        # Get all expected files
        expected_files = set()
        for category, files in self.get_required_files().items():
            expected_files.update(files)
        
        # Add some known OK files
        expected_files.add("local_automation.py")
        expected_files.add("project_file_integrity_check.py")  # This file
        
        # Find orphaned files
        orphaned = []
        for file in all_python_files:
            if file not in expected_files and not any(pat in file for pat in ['__pycache__', 'test_', '_test.py']):
                # Check if it's in an expected directory at least
                if not any(file.startswith(d) for d in ['app/src/', 'app/assets/']):
                    orphaned.append(file)
                    print(f"❓ ORPHANED: {file}")
        
        if not orphaned:
            print("✅ No orphaned files found")
        
        return orphaned
    
    def generate_report(self):
        """Generate a summary report"""
        print("\n" + "="*60)
        print("SUMMARY REPORT")
        print("="*60)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\nReport generated: {timestamp}")
        
        print(f"\n📊 Required Files:")
        print(f"   ✅ Present: {len(self.results['required_present'])}")
        print(f"   ❌ Missing: {len(self.results['required_missing'])}")
        
        print(f"\n🗑️ Unnecessary Files Found:")
        print(f"   📑 Duplicates: {len(self.results['duplicate_files'])}")
        print(f"   🔄 Backups: {len(self.results['backup_files'])}")
        print(f"   📦 Archived: {len(self.results['archived_files'])}")
        print(f"   🗑️ Temp files: {len(self.results['temp_files'])}")
        
        # Critical missing files
        if self.results['required_missing']:
            critical_missing = [f for f in self.results['required_missing'] 
                               if not f.endswith('__init__.py') and f not in ['.env', 'credentials.json']]
            if critical_missing:
                print(f"\n⚠️ CRITICAL MISSING FILES:")
                for file in critical_missing[:5]:  # Show first 5
                    print(f"   - {file}")
        
        # Files to clean up
        total_cleanup = (len(self.results['duplicate_files']) + 
                        len(self.results['backup_files']) + 
                        len(self.results['archived_files']) + 
                        len(self.results['temp_files']))
        
        if total_cleanup > 0:
            print(f"\n🧹 RECOMMENDED CLEANUP: {total_cleanup} files")
            print("   Run with --cleanup flag to see detailed cleanup list")
        
        # Save detailed report
        report_file = f"file_integrity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return self.results
    
    def suggest_cleanup_commands(self):
        """Generate cleanup commands for unnecessary files"""
        print("\n" + "="*60)
        print("CLEANUP COMMANDS")
        print("="*60)
        
        all_unnecessary = (self.results['duplicate_files'] + 
                           self.results['backup_files'] + 
                           self.results['archived_files'] + 
                           self.results['temp_files'])
        
        if not all_unnecessary:
            print("✅ No files to clean up!")
            return
        
        print("\n# Windows Command (PowerShell):")
        for file in all_unnecessary[:10]:  # Show first 10
            print(f'Remove-Item "{file}" -Force')
        
        print("\n# Linux/Mac Command:")
        for file in all_unnecessary[:10]:  # Show first 10
            print(f'rm "{file}"')
        
        if len(all_unnecessary) > 10:
            print(f"\n... and {len(all_unnecessary) - 10} more files")

def main():
    """Run the file integrity check"""
    print("="*60)
    print("AI AUTOMATION SUITE - FILE INTEGRITY CHECK")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists("local_automation.py"):
        print("❌ ERROR: Must run from project root directory")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    checker = ProjectFileChecker()
    
    # Run all checks
    checker.check_required_files()
    checker.check_project_structure()
    checker.find_unnecessary_files()
    checker.check_for_orphaned_files()
    
    # Generate report
    results = checker.generate_report()
    
    # Show cleanup commands if requested
    if "--cleanup" in sys.argv:
        checker.suggest_cleanup_commands()
    
    # Return exit code based on critical missing files
    critical_missing = [f for f in results['required_missing'] 
                       if not f.endswith('__init__.py') and f not in ['.env', 'credentials.json']]
    
    if critical_missing:
        print(f"\n❌ CHECK FAILED: {len(critical_missing)} critical files missing")
        sys.exit(1)
    else:
        print("\n✅ CHECK PASSED: All critical files present")
        sys.exit(0)

if __name__ == "__main__":
    main()