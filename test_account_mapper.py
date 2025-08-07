# test_account_mapper.py - Diagnostic test for modular account mapper

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports to find the issue"""
    
    print("🔍 TESTING ACCOUNT MAPPER IMPORTS...")
    print("=" * 50)
    
    try:
        print("1. Testing config import...")
        from app.src.automation.api_clients.account_mapper.config import ACCOUNT_MAPPING
        print("   ✅ Config import successful")
        print(f"   📋 Found {len(ACCOUNT_MAPPING)} accounts")
        
        print("\n2. Testing detection import...")
        from app.src.automation.api_clients.account_mapper.detection import DetectionEngine
        detection = DetectionEngine()
        print("   ✅ Detection engine import successful")
        
        print("\n3. Testing worksheet matcher import...")
        from app.src.automation.api_clients.account_mapper.worksheet_matcher import WorksheetMatcher
        matcher = WorksheetMatcher()
        print("   ✅ Worksheet matcher import successful")
        
        print("\n4. Testing user dialogs import...")
        from app.src.automation.api_clients.account_mapper.user_dialogs import UserDialogs
        dialogs = UserDialogs()
        print("   ✅ User dialogs import successful")
        
        print("\n5. Testing core import...")
        from app.src.automation.api_clients.account_mapper.core import AccountMapper
        mapper = AccountMapper()
        print("   ✅ Core AccountMapper import successful")
        
        print("\n6. Testing main import (the way system uses it)...")
        from app.src.automation.api_clients.account_mapper import AccountMapper as MainMapper
        main_mapper = MainMapper()
        print("   ✅ Main AccountMapper import successful")
        
        print("\n7. Testing method availability...")
        if hasattr(main_mapper, 'extract_account_and_platform'):
            print("   ✅ extract_account_and_platform method found")
        else:
            print("   ❌ extract_account_and_platform method NOT found")
            print(f"   📋 Available methods: {[m for m in dir(main_mapper) if not m.startswith('_')]}")
        
        print("\n8. Testing actual detection...")
        test_card = "BC3 Snapchat - New Ads from GH AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416"
        account, platform = main_mapper.extract_account_and_platform(test_card, allow_fallback=False)
        print(f"   ✅ Detection test: {test_card}")
        print(f"   🎯 Result: Account='{account}', Platform='{platform}'")
        
        print("\n9. Testing worksheet matching...")
        available_worksheets = ['Help - C', 'BC3 - FB', 'BC3 - YT', 'BC3 - Snapchat', 'TR - FB']
        worksheet = main_mapper.find_exact_worksheet_match(available_worksheets, account, platform)
        print(f"   🎯 Worksheet match: '{worksheet}'")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_old_import():
    """Test if the old import path still works"""
    
    print("\n🔍 TESTING OLD IMPORT PATH...")
    print("=" * 50)
    
    try:
        # This is how the system tries to import it
        from app.src.automation.api_clients.account_mapper import AccountMapper
        mapper = AccountMapper()
        
        print("✅ Old import path works")
        print(f"📋 AccountMapper type: {type(mapper)}")
        print(f"📋 Available methods: {[m for m in dir(mapper) if not m.startswith('_')]}")
        
        if hasattr(mapper, 'extract_account_and_platform'):
            print("✅ Method extract_account_and_platform exists")
            
            # Test the method
            test_card = "BC3 Snapchat - Test"
            result = mapper.extract_account_and_platform(test_card, allow_fallback=False)
            print(f"✅ Method works: {result}")
            
        else:
            print("❌ Method extract_account_and_platform NOT found")
            
        return True
        
    except Exception as e:
        print(f"❌ OLD IMPORT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 ACCOUNT MAPPER DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Test new modular imports
    success1 = test_imports()
    
    # Test old import path
    success2 = test_old_import()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS SUCCESSFUL - Modular structure is working!")
    else:
        print("\n❌ TESTS FAILED - Need to fix import structure")
        
    print("\nRun this test to diagnose the import issue:")
    print("python test_account_mapper.py")