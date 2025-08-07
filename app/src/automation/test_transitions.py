# test_transitions.py
# Place this file in: app/src/automation/
# Run it to diagnose import issues

import os
import sys

print("=" * 60)
print("TRANSITIONS MODULE IMPORT TEST")
print("=" * 60)

# Show current directory
print(f"\n1. Current working directory:")
print(f"   {os.getcwd()}")

# Show script location
print(f"\n2. This script location:")
print(f"   {os.path.abspath(__file__)}")

# Check if transitions folder exists
transitions_path = os.path.join(os.path.dirname(__file__), 'transitions')
print(f"\n3. Checking transitions folder:")
print(f"   Path: {transitions_path}")
print(f"   Exists: {os.path.exists(transitions_path)}")

if os.path.exists(transitions_path):
    print(f"   Contents: {os.listdir(transitions_path)}")
    
    # Check __init__.py
    init_file = os.path.join(transitions_path, '__init__.py')
    print(f"\n4. Checking __init__.py:")
    print(f"   Path: {init_file}")
    print(f"   Exists: {os.path.exists(init_file)}")
    
    if os.path.exists(init_file):
        print(f"   Size: {os.path.getsize(init_file)} bytes")
        # Check if file is empty
        with open(init_file, 'r') as f:
            content = f.read()
            if not content.strip():
                print("   ⚠️ WARNING: __init__.py is empty!")
            else:
                print(f"   ✅ __init__.py has content ({len(content)} chars)")

# Try different import methods
print(f"\n5. Testing import methods:")

# Method 1: Direct import
try:
    from transitions import apply_transitions_to_video
    print("   ✅ Method 1 worked: from transitions import apply_transitions_to_video")
except ImportError as e:
    print(f"   ❌ Method 1 failed: {e}")

# Method 2: Relative import
try:
    from .transitions import apply_transitions_to_video
    print("   ✅ Method 2 worked: from .transitions import apply_transitions_to_video")
except ImportError as e:
    print(f"   ❌ Method 2 failed: {e}")

# Method 3: Add to path and import
try:
    sys.path.insert(0, os.path.dirname(__file__))
    import transitions
    print(f"   ✅ Method 3 worked: Added to sys.path and imported")
    
    # Check what's in the module
    print(f"\n6. Module contents:")
    print(f"   Module file: {transitions.__file__ if hasattr(transitions, '__file__') else 'No __file__ attribute'}")
    print(f"   Available attributes: {dir(transitions)[:10]}...")  # First 10 attributes
    
    # Try to get the function
    if hasattr(transitions, 'apply_transitions_to_video'):
        print(f"   ✅ apply_transitions_to_video found in module")
    else:
        print(f"   ❌ apply_transitions_to_video NOT found in module")
        print(f"   Available functions: {[x for x in dir(transitions) if not x.startswith('_')]}")
        
except ImportError as e:
    print(f"   ❌ Method 3 failed: {e}")

# Method 4: Import specific module file
try:
    from transitions.processor import TransitionProcessor
    print("   ✅ Method 4 worked: from transitions.processor import TransitionProcessor")
except ImportError as e:
    print(f"   ❌ Method 4 failed: {e}")

# Check Python path
print(f"\n7. Python path (first 5):")
for i, path in enumerate(sys.path[:5]):
    print(f"   {i}: {path}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)