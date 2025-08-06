# import_test.py - DEBUG IMPORT PATHS
"""
Test script to debug import paths and see what's failing
"""

import sys
import os

print("🔍 DEBUGGING IMPORT PATHS")
print("=" * 50)

# Print current working directory and Python path
print(f"📁 Current working directory: {os.getcwd()}")
print(f"📂 Python path entries:")
for i, path in enumerate(sys.path):
    print(f"   {i}: {path}")

# Test different import scenarios
print("\n🧪 TESTING IMPORT SCENARIOS:")
print("=" * 50)

# Test 1: Direct naming_generator import
print("\n1. Testing: import naming_generator")
try:
    import naming_generator
    print("✅ SUCCESS: naming_generator imported")
    print(f"   Location: {naming_generator.__file__}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 2: app.naming_generator import
print("\n2. Testing: import app.naming_generator")
try:
    import app.naming_generator
    print("✅ SUCCESS: app.naming_generator imported")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 3: From app.src import naming_generator
print("\n3. Testing: from app.src import naming_generator")
try:
    from app.src import naming_generator
    print("✅ SUCCESS: app.src.naming_generator imported")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 4: Add paths and try again
print("\n4. Testing: Adding paths and retrying")
try:
    # Add potential paths
    potential_paths = [
        os.path.join(os.getcwd(), 'app', 'src'),
        os.path.join(os.getcwd(), 'app'),
        os.path.dirname(os.path.abspath(__file__))
    ]
    
    for path in potential_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
            print(f"   Added: {path}")
    
    # Try importing again
    import naming_generator
    print("✅ SUCCESS: naming_generator imported after path adjustment")
    
    # Test a function call
    result = naming_generator.clean_project_name("test_project")
    print(f"   Function test: clean_project_name('test_project') = '{result}'")
    
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 5: Check if we can import the specific functions we need
print("\n5. Testing: Import specific functions")
try:
    from naming_generator import (
        generate_output_name,
        generate_project_folder_name,
        get_image_description,
        parse_project_info,
        clean_project_name
    )
    print("✅ SUCCESS: All required functions imported")
    
    # Test each function exists
    functions = [
        generate_output_name,
        generate_project_folder_name, 
        get_image_description,
        parse_project_info,
        clean_project_name
    ]
    
    for func in functions:
        print(f"   ✅ {func.__name__} - Available")
        
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n🏁 IMPORT TESTING COMPLETED")