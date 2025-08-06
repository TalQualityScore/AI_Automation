# naming_diagnostic.py - DIAGNOSTIC SCRIPT FOR NAMING MODULE
"""
Diagnostic script to check the naming module dependencies and imports.
Run this to identify exactly what's causing the import error.
"""

import sys
import os
import traceback

def test_individual_modules():
    """Test each naming module individually"""
    
    print("🔍 DIAGNOSTIC: Testing individual naming modules...")
    print("=" * 60)
    
    # Add the app/src directory to Python path
    app_src_path = os.path.dirname(os.path.abspath(__file__))
    if app_src_path not in sys.path:
        sys.path.insert(0, app_src_path)
        print(f"📁 Added to Python path: {app_src_path}")
    
    modules_to_test = [
        'naming.version_extractor',
        'naming.project_parser', 
        'naming.name_generator',
        'naming.content_analyzer',
        'naming.text_utils'
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        print(f"\n🧪 Testing: {module_name}")
        try:
            if module_name == 'naming.version_extractor':
                from naming.version_extractor import VersionExtractor
                extractor = VersionExtractor()
                test_result = extractor.extract_version_letter("test_250416D.mp4")
                print(f"✅ {module_name}: SUCCESS - extracted '{test_result}'")
                results[module_name] = "SUCCESS"
                
            elif module_name == 'naming.project_parser':
                from naming.project_parser import ProjectParser
                parser = ProjectParser()
                test_result = parser.parse_project_info("test folder")
                print(f"✅ {module_name}: SUCCESS - parsed {type(test_result)}")
                results[module_name] = "SUCCESS"
                
            elif module_name == 'naming.name_generator':
                from naming.name_generator import NameGenerator
                generator = NameGenerator()
                print(f"✅ {module_name}: SUCCESS - created generator")
                results[module_name] = "SUCCESS"
                
            elif module_name == 'naming.content_analyzer':
                from naming.content_analyzer import ContentAnalyzer
                analyzer = ContentAnalyzer()
                test_result = analyzer.get_image_description("dinner_video.mp4")
                print(f"✅ {module_name}: SUCCESS - analyzed '{test_result}'")
                results[module_name] = "SUCCESS"
                
            elif module_name == 'naming.text_utils':
                from naming.text_utils import TextUtils
                utils = TextUtils()
                test_result = utils.clean_project_name("test_project_name")
                print(f"✅ {module_name}: SUCCESS - cleaned '{test_result}'")
                results[module_name] = "SUCCESS"
                
        except Exception as e:
            print(f"❌ {module_name}: FAILED")
            print(f"   Error: {str(e)}")
            print(f"   Traceback: {traceback.format_exc()}")
            results[module_name] = f"FAILED: {str(e)}"
    
    return results

def test_naming_init():
    """Test the naming __init__.py file"""
    
    print(f"\n🔍 DIAGNOSTIC: Testing naming.__init__ module...")
    print("=" * 60)
    
    try:
        import naming
        print("✅ naming module imported successfully")
        
        # Test each function
        functions_to_test = [
            'generate_output_name',
            'generate_project_folder_name',
            'get_image_description', 
            'parse_project_info',
            'clean_project_name'
        ]
        
        for func_name in functions_to_test:
            if hasattr(naming, func_name):
                print(f"✅ Function '{func_name}' available")
            else:
                print(f"❌ Function '{func_name}' NOT available")
        
        # Test a simple function call
        try:
            result = naming.clean_project_name("test_name")
            print(f"✅ Function call successful: clean_project_name('test_name') = '{result}'")
        except Exception as e:
            print(f"❌ Function call failed: {e}")
            
        return "SUCCESS"
        
    except Exception as e:
        print(f"❌ naming module import FAILED")
        print(f"   Error: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        return f"FAILED: {str(e)}"

def test_naming_generator_wrapper():
    """Test the naming_generator.py wrapper"""
    
    print(f"\n🔍 DIAGNOSTIC: Testing naming_generator wrapper...")
    print("=" * 60)
    
    try:
        import naming_generator
        print("✅ naming_generator module imported successfully")
        
        # Test the main functions
        functions_to_test = [
            'generate_output_name',
            'generate_project_folder_name',
            'get_image_description',
            'parse_project_info', 
            'clean_project_name'
        ]
        
        for func_name in functions_to_test:
            if hasattr(naming_generator, func_name):
                print(f"✅ Function '{func_name}' available")
            else:
                print(f"❌ Function '{func_name}' NOT available")
        
        # Test critical function with AGMD case
        try:
            result = naming_generator.parse_project_info("AGMD_BC3_Dinner_Mashup_OPT_STOR-3133_250416")
            print(f"✅ Critical test successful: parse_project_info returned {result}")
        except Exception as e:
            print(f"❌ Critical test failed: {e}")
            
        return "SUCCESS"
        
    except Exception as e:
        print(f"❌ naming_generator import FAILED")
        print(f"   Error: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        return f"FAILED: {str(e)}"

def check_file_structure():
    """Check if all required files exist"""
    
    print(f"\n🔍 DIAGNOSTIC: Checking file structure...")
    print("=" * 60)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        'naming/__init__.py',
        'naming/version_extractor.py',
        'naming/project_parser.py',
        'naming/name_generator.py', 
        'naming/content_analyzer.py',
        'naming/text_utils.py',
        'naming_generator.py'
    ]
    
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"✅ {file_path} - EXISTS ({file_size} bytes)")
        else:
            print(f"❌ {file_path} - MISSING")

def main():
    """Run all diagnostic tests"""
    
    print("🚀 NAMING MODULE DIAGNOSTIC STARTED")
    print("=" * 80)
    
    # Check file structure first
    check_file_structure()
    
    # Test individual modules
    individual_results = test_individual_modules()
    
    # Test naming __init__
    init_result = test_naming_init()
    
    # Test wrapper
    wrapper_result = test_naming_generator_wrapper()
    
    # Summary
    print(f"\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    print("Individual Modules:")
    for module, result in individual_results.items():
        status = "✅" if result == "SUCCESS" else "❌"
        print(f"  {status} {module}: {result}")
    
    print(f"\nMain Components:")
    print(f"  {'✅' if init_result == 'SUCCESS' else '❌'} naming.__init__: {init_result}")
    print(f"  {'✅' if wrapper_result == 'SUCCESS' else '❌'} naming_generator: {wrapper_result}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    failed_modules = [k for k, v in individual_results.items() if v != "SUCCESS"]
    if failed_modules:
        print(f"   📁 Fix these modules first: {', '.join(failed_modules)}")
    
    if init_result != "SUCCESS":
        print(f"   📁 Fix naming/__init__.py imports")
    
    if wrapper_result != "SUCCESS":
        print(f"   📁 Fix naming_generator.py wrapper")
    
    if not failed_modules and init_result == "SUCCESS" and wrapper_result == "SUCCESS":
        print(f"   🎉 All systems working! The import error might be elsewhere.")
    
    print("\n🏁 DIAGNOSTIC COMPLETED")

if __name__ == "__main__":
    main()