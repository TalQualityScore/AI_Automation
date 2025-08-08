# safe_import_diagnostic.py
"""
SAFE DIAGNOSTIC ONLY - This script DOES NOT modify any files
It only shows you what's happening with your imports
"""

import os
import re
from pathlib import Path

def analyze_imports():
    """Analyze imports WITHOUT making any changes"""
    
    print("=" * 60)
    print("SAFE IMPORT ANALYSIS - NO FILES WILL BE MODIFIED")
    print("=" * 60)
    print("\nThis is READ-ONLY - just showing you what's happening\n")
    
    # Track what we find
    import_analysis = {
        'working_imports': [],
        'suspicious_imports': [],
        'file_exists_checks': {},
        'actual_locations': {}
    }
    
    # First, let's see what files actually exist
    print("📁 CHECKING WHICH FILES ACTUALLY EXIST:")
    print("-" * 40)
    
    files_to_check = [
        ('app/src/automation/monitor.py', 'Old monitor file'),
        ('app/src/automation/orchestrator/core.py', 'New orchestrator with monitoring'),
        ('app/src/automation/timing_report.py', 'Old timing file'),
        ('app/src/automation/api_clients/google_drive.py', 'Old Google Drive file'),
        ('app/src/automation/api_clients/google_drive_client.py', 'New Google Drive file'),
        ('app/src/automation/api_clients/__init__.py', 'API clients init'),
        ('app/src/automation/workflow_dialog/notification_manager.py', 'Old notification file'),
        ('app/src/automation/workflow_dialog/notification_handlers.py', 'New notification file'),
    ]
    
    for file_path, description in files_to_check:
        exists = os.path.exists(file_path)
        import_analysis['file_exists_checks'][file_path] = exists
        status = "✅ EXISTS" if exists else "❌ NOT FOUND"
        print(f"  {status}: {file_path}")
        print(f"           ({description})")
    
    # Now check where key classes/functions actually live
    print("\n🔍 LOCATING KEY COMPONENTS:")
    print("-" * 40)
    
    components_to_find = {
        'ActivityMonitor': 'Monitoring class',
        'download_files_from_gdrive': 'Google Drive download function',
        'write_to_google_sheets': 'Google Sheets write function',
        'GoogleDriveClient': 'Google Drive client class',
        'GoogleSheetsClient': 'Google Sheets client class',
        'NotificationManager': 'Notification manager class'
    }
    
    # Search for these components
    for root, dirs, files in os.walk('app'):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for component, description in components_to_find.items():
                        # Look for class or function definition
                        if (f'class {component}' in content or 
                            f'def {component}' in content):
                            
                            if component not in import_analysis['actual_locations']:
                                import_analysis['actual_locations'][component] = []
                            
                            import_analysis['actual_locations'][component].append(file_path)
                            print(f"  ✅ Found '{component}' in: {file_path}")
                except:
                    pass
    
    # Check for components not found
    for component in components_to_find:
        if component not in import_analysis['actual_locations']:
            print(f"  ❌ '{component}' not found in any Python files")
    
    # Now scan for import statements
    print("\n📝 SCANNING IMPORT STATEMENTS:")
    print("-" * 40)
    
    problem_patterns = [
        (r'from automation\.monitor import', 'Trying to import from monitor.py'),
        (r'from \.\.monitor import', 'Relative import from monitor.py'),
        (r'from automation\.timing_report import', 'Trying to import from timing_report.py'),
        (r'from automation\.api_clients\.google_drive import', 'Import from google_drive.py'),
        (r'from automation\.api_clients\.google_sheets import', 'Import from google_sheets.py'),
        (r'from \.\.workflow_dialog\.notification_manager import', 'Import from notification_manager.py'),
    ]
    
    files_with_imports = {}
    
    for root, dirs, files in os.walk('app'):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern, description in problem_patterns:
                            if re.search(pattern, line.strip()):
                                if file_path not in files_with_imports:
                                    files_with_imports[file_path] = []
                                
                                files_with_imports[file_path].append({
                                    'line': line_num,
                                    'content': line.strip(),
                                    'issue': description
                                })
                except:
                    pass
    
    # Report findings
    if files_with_imports:
        print(f"\n⚠️ Found {len(files_with_imports)} files with potentially problematic imports:")
        for file_path, issues in files_with_imports.items():
            print(f"\n  File: {file_path}")
            for issue in issues[:3]:  # Show first 3 issues per file
                print(f"    Line {issue['line']}: {issue['content']}")
                print(f"    Issue: {issue['issue']}")
    else:
        print("\n✅ No problematic import patterns found!")
    
    # Summary and recommendations
    print("\n" + "=" * 60)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n📊 ANALYSIS RESULTS:")
    
    # Check if old files exist but shouldn't
    old_files_exist = any([
        import_analysis['file_exists_checks'].get('app/src/automation/monitor.py', False),
        import_analysis['file_exists_checks'].get('app/src/automation/timing_report.py', False),
        import_analysis['file_exists_checks'].get('app/src/automation/api_clients/google_drive.py', False),
        import_analysis['file_exists_checks'].get('app/src/automation/api_clients/google_sheets.py', False),
    ])
    
    if old_files_exist:
        print("\n⚠️ You have OLD structure files that might be duplicates")
    
    # Check if new files exist
    new_files_exist = any([
        import_analysis['file_exists_checks'].get('app/src/automation/orchestrator/core.py', False),
        import_analysis['file_exists_checks'].get('app/src/automation/api_clients/__init__.py', False),
    ])
    
    if new_files_exist:
        print("\n✅ You have the NEW modular structure in place")
    
    if files_with_imports:
        print(f"\n⚠️ {len(files_with_imports)} files have imports pointing to old locations")
        print("   These imports might fail if the old files don't exist")
    
    print("\n💡 RECOMMENDATIONS:")
    
    if files_with_imports and not old_files_exist:
        print("\n1. Your imports are looking for files that don't exist anymore")
        print("2. The functionality has been moved to new locations")
        print("3. You need to update the imports to point to the new locations")
        print("\n🛡️ SAFE APPROACH:")
        print("   - Make a backup of your project first")
        print("   - Update imports one file at a time")
        print("   - Test after each change")
    elif files_with_imports and old_files_exist:
        print("\n1. You have BOTH old and new structure files")
        print("2. This might cause confusion or duplicate code")
        print("3. Verify which files are actually being used")
        print("\n🛡️ SAFE APPROACH:")
        print("   - Check which files your main code actually uses")
        print("   - Remove duplicates carefully")
    else:
        print("\n✅ Your import structure looks good!")
    
    # Save detailed report
    report_file = "import_diagnostic_report.txt"
    with open(report_file, 'w') as f:
        f.write("IMPORT DIAGNOSTIC REPORT\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("FILES EXISTENCE CHECK:\n")
        for file_path, exists in import_analysis['file_exists_checks'].items():
            f.write(f"  {'✅' if exists else '❌'} {file_path}\n")
        
        f.write("\nCOMPONENT LOCATIONS:\n")
        for component, locations in import_analysis['actual_locations'].items():
            f.write(f"  {component}:\n")
            for loc in locations:
                f.write(f"    - {loc}\n")
        
        if files_with_imports:
            f.write("\nPROBLEMATIC IMPORTS:\n")
            for file_path, issues in files_with_imports.items():
                f.write(f"\n  {file_path}:\n")
                for issue in issues:
                    f.write(f"    Line {issue['line']}: {issue['content']}\n")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    print("\n✅ Diagnostic complete - NO FILES WERE MODIFIED")

if __name__ == "__main__":
    import sys
    
    if not os.path.exists("local_automation.py"):
        print("❌ ERROR: Must run from project root directory")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    print("🛡️ SAFE MODE - This script will NOT modify any files")
    print("It will only analyze and report what it finds\n")
    
    analyze_imports()