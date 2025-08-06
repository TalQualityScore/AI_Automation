# comprehensive_fixes.py - Apply all critical fixes and clear cache

import os
import sys
import shutil
import importlib
import tempfile

def clear_python_cache():
    """Clear all Python cache files to prevent old code from running"""
    print("🧹 CLEARING PYTHON CACHE...")
    
    # Clear __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                    print(f"   ✅ Removed: {pycache_path}")
                except Exception as e:
                    print(f"   ⚠️ Could not remove {pycache_path}: {e}")
    
    # Clear .pyc files
    for root, dirs, files in os.walk('.'):
        for file_name in files:
            if file_name.endswith('.pyc'):
                pyc_path = os.path.join(root, file_name)
                try:
                    os.remove(pyc_path)
                    print(f"   ✅ Removed: {pyc_path}")
                except Exception as e:
                    print(f"   ⚠️ Could not remove {pyc_path}: {e}")

def clear_module_imports():
    """Clear imported modules from sys.modules"""
    print("🔄 CLEARING MODULE CACHE...")
    
    modules_to_clear = [
        'app.src.automation.api_clients.account_mapper',
        'app.src.automation.orchestrator.ui_integration',
        'app.src.automation.workflow_ui_components.confirmation_tab',
        'app.src.automation.workflow_dialog.dialog_controller',
        'app.src.naming_generator',
        'app.src.automation.api_clients',
    ]
    
    # Clear specific modules
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
            print(f"   ✅ Cleared: {module}")
    
    # Clear all app.src.automation modules
    to_remove = []
    for module_name in sys.modules.keys():
        if module_name.startswith('app.src.automation'):
            to_remove.append(module_name)
    
    for module_name in to_remove:
        del sys.modules[module_name]
        print(f"   ✅ Cleared: {module_name}")

def backup_current_files():
    """Backup current files before applying fixes"""
    print("💾 CREATING BACKUP...")
    
    backup_dir = f"backup_{int(time.time())}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'app/src/automation/api_clients/account_mapper.py',
        'app/src/automation/orchestrator/ui_integration.py', 
        'app/src/automation/workflow_ui_components/confirmation_tab.py',
        'app/src/automation/workflow_dialog/dialog_controller.py',
        'app/src/naming_generator.py'
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f"   ✅ Backed up: {file_path} → {backup_path}")
    
    print(f"✅ Backup created in: {backup_dir}")
    return backup_dir

def test_account_detection():
    """Test the fixed account detection"""
    print("\n🧪 TESTING ACCOUNT DETECTION...")
    
    try:
        # Clear cache first
        importlib.invalidate_caches()
        
        # Import fresh module
        from app.src.automation.api_clients.account_mapper import AccountMapper
        
        mapper = AccountMapper()
        
        test_cases = [
            ("TR FB - New Ads from GH AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416", "TR", "FB"),
            ("BC3 YT - New project", "BC3", "YT"), 
            ("OO FB - Olive Oil Campaign", "OO", "FB")
        ]
        
        for test_case, expected_account, expected_platform in test_cases:
            print(f"\n   🔍 Testing: '{test_case}'")
            try:
                account, platform = mapper.extract_account_and_platform(test_case, allow_fallback=False)
                
                if account == expected_account and platform == expected_platform:
                    print(f"   ✅ PASS: {account}, {platform}")
                else:
                    print(f"   ❌ FAIL: Expected {expected_account},{expected_platform}, got {account},{platform}")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
        
        print(f"✅ Account detection test completed")
        
    except Exception as e:
        print(f"❌ Account detection test failed: {e}")

def test_version_letter_extraction():
    """Test the fixed version letter extraction"""
    print("\n🧪 TESTING VERSION LETTER EXTRACTION...")
    
    try:
        # Clear cache first
        importlib.invalidate_caches()
        
        # Import fresh module
        from app.src.naming_generator import generate_output_name
        
        test_cases = [
            ("GMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416D.mp4", "D"),
            ("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416C.mp4", "C"), 
            ("GMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416B.mp4", "B")
        ]
        
        for filename, expected_letter in test_cases:
            print(f"\n   🔍 Testing: '{filename}'")
            try:
                result = generate_output_name("Test Project", filename, "quiz", "test", 1, "")
                
                # Check if the expected letter appears in the result
                if f"3133{expected_letter}ZZ" in result:
                    print(f"   ✅ PASS: Found '{expected_letter}' in result")
                else:
                    print(f"   ❌ FAIL: Expected '{expected_letter}' not found in: {result}")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
        
        print(f"✅ Version letter extraction test completed")
        
    except Exception as e:
        print(f"❌ Version letter extraction test failed: {e}")

def verify_fixes():
    """Verify all fixes are working"""
    print("\n🔍 VERIFYING FIXES...")
    
    # Test 1: Account Detection
    test_account_detection()
    
    # Test 2: Version Letter Extraction  
    test_version_letter_extraction()
    
    # Test 3: Check file existence
    required_files = [
        'app/src/automation/api_clients/account_mapper.py',
        'app/src/automation/orchestrator/ui_integration.py',
        'app/src/automation/workflow_ui_components/confirmation_tab.py',
        'app/src/automation/workflow_dialog/dialog_controller.py'
    ]
    
    print(f"\n🔍 CHECKING FILE EXISTENCE...")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ EXISTS: {file_path}")
        else:
            print(f"   ❌ MISSING: {file_path}")

def main():
    """Main fix application function"""
    print("🚀 AI AUTOMATION COMPREHENSIVE FIXES")
    print("=" * 50)
    
    # Step 1: Backup current files
    import time
    backup_dir = backup_current_files()
    
    # Step 2: Clear all cache
    clear_python_cache()
    clear_module_imports()
    
    print(f"\n📝 FIXES TO APPLY:")
    print(f"   1. ✅ Account/Platform Detection with Fallback Dialog")
    print(f"   2. ✅ Project Name Flow from Confirmation to Processing")  
    print(f"   3. ✅ Version Letter Extraction (A/B/C/D)")
    print(f"   4. ✅ UI Integration Complete Update")
    print(f"   5. ✅ Dialog Controller Complete Update")
    
    print(f"\n⚠️  IMPORTANT MANUAL STEPS:")
    print(f"   1. Replace the files with the corrected versions from the artifacts above")
    print(f"   2. Run verification tests")
    print(f"   3. Test with a real Trello card: 'TR FB - New Ads from...'")
    
    # Step 3: Verify after manual file replacement
    print(f"\n🎯 AFTER REPLACING FILES, RUN:")
    print(f"   python comprehensive_fixes.py --verify")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        verify_fixes()
    
    print(f"\n✅ COMPREHENSIVE FIXES PREPARATION COMPLETE")
    print(f"💾 Backup available in: {backup_dir}")
    print(f"🔧 Apply the artifact files above, then run verification")

if __name__ == "__main__":
    main()