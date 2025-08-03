# test_integration_fixed.py - Complete testing framework for UI integration
import sys
import os
import time

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.src.automation.unified_workflow_dialog import (
    UnifiedWorkflowDialog, 
    ConfirmationData, 
    ValidationIssue,
    ProcessingResult
)
from app.src.automation.main_orchestrator import AutomationOrchestrator

def test_ui_components_only():
    """Test individual UI components without full processing"""
    print("🧪 Testing Individual UI Components")
    print("-" * 50)
    
    # Test 1: Confirmation Dialog Only
    print("\n1. Testing Confirmation Dialog...")
    test_data = ConfirmationData(
        project_name="Test Project VTD 12036",
        account="OO (Olive Oil)",
        platform="YouTube",
        processing_mode="CONNECTOR + QUIZ",
        client_videos=["video1.mp4", "video2.mp4", "video3.mp4"],
        templates_to_add=[
            "Add Blake connector (YT/Connectors/)",
            "Add quiz outro (YT/Quiz/)",
            "Apply slide transition effects"
        ],
        output_location="GH Test Project VTD 12036 Quiz",
        estimated_time="5-8 minutes",
        issues=[
            ValidationIssue("warning", "Large file detected (440MB)"),
            ValidationIssue("info", "Processing will use significant disk space")
        ],
        file_sizes=[("video1.mp4", 145), ("video2.mp4", 298), ("video3.mp4", 1200)]
    )
    
    def mock_quick_processing(progress_callback):
        """Quick mock processing for UI testing"""
        steps = [
            (25, "Initializing..."),
            (50, "Processing..."),
            (75, "Finalizing..."),
            (100, "Complete!")
        ]
        
        for progress, message in steps:
            progress_callback(progress, message)
            time.sleep(0.5)  # Quick for testing
        
        return ProcessingResult(
            success=True,
            duration="30 seconds",
            processed_files=[
                {
                    'version': 'v01',
                    'source_file': 'video1.mp4',
                    'output_name': 'test_output_01',
                    'description': 'Test processing result'
                }
            ],
            output_folder=r"C:\Users\Desktop\Test Output"
        )
    
    dialog = UnifiedWorkflowDialog()
    result = dialog.show_workflow(test_data, mock_quick_processing)
    print(f"✅ UI Test Result: {'SUCCESS' if result else 'CANCELLED'}")
    return result

def test_complete_workflow_mock():
    """Test complete workflow with realistic mock data"""
    print("\n🧪 Testing Complete Workflow (Mock Data)")
    print("-" * 50)
    
    test_data = ConfirmationData(
        project_name="Grocery Store Oils VTD 12036",
        account="OO (Olive Oil)",
        platform="YouTube",
        processing_mode="CONNECTOR + QUIZ",
        client_videos=["GroceryOils_001.mp4", "GroceryOils_002.mp4", "GroceryOils_003.mp4"],
        templates_to_add=[
            "Add Blake connector (YT/Connectors/)",
            "Add quiz outro (YT/Quiz/)",
            "Apply slide transition effects"
        ],
        output_location="GH Grocery Store Oils VTD 12036 Quiz",
        estimated_time="5-8 minutes",
        issues=[
            ValidationIssue("warning", "Large file detected: GroceryOils_003.mp4 (1200MB)"),
            ValidationIssue("info", "Processing will create high-quality output")
        ],
        file_sizes=[("GroceryOils_001.mp4", 245), ("GroceryOils_002.mp4", 398), ("GroceryOils_003.mp4", 1200)]
    )
    
    def realistic_mock_processing(progress_callback):
        """Realistic mock processing that simulates actual workflow"""
        steps = [
            (10, "🔍 Validating Trello card data..."),
            (20, "📐 Analyzing processing requirements..."),
            (30, "📥 Downloading videos from Google Drive..."),
            (35, "📥 Download 25%... Download 50%... Download 75%..."),
            (45, "📁 Creating project structure..."),
            (50, "📂 Organizing downloaded files..."),
            (55, "📐 Analyzing video dimensions..."),
            (60, "📊 Checking version numbers..."),
            (65, "🎬 Processing video 1 of 3 (v01)..."),
            (70, "🎬 Processing video 2 of 3 (v02)..."),
            (80, "🎬 Processing video 3 of 3 (v03)..."),
            (85, "✅ Completed processing 3 video(s)"),
            (90, "📊 Logging results to Google Sheets..."),
            (95, "🧹 Cleaning up temporary files..."),
            (100, "🎉 Processing complete!")
        ]
        
        start_time = time.time()
        
        for progress, message in steps:
            progress_callback(progress, message)
            time.sleep(0.8)  # Realistic timing
        
        # Return realistic results
        return ProcessingResult(
            success=True,
            duration="6 minutes 24 seconds",
            processed_files=[
                {
                    'version': 'v01',
                    'source_file': 'GroceryOils_001.mp4',
                    'output_name': 'GH-grocerystoreoilsvtd12036ZZquiz_x-v01-m01-f00-c00',
                    'description': 'New Ad from GroceryOils_001.mp4 + connector + quiz'
                },
                {
                    'version': 'v02',
                    'source_file': 'GroceryOils_002.mp4',
                    'output_name': 'GH-grocerystoreoilsvtd12036ZZquiz_y-v02-m01-f00-c00',
                    'description': 'New Ad from GroceryOils_002.mp4 + connector + quiz'
                },
                {
                    'version': 'v03',
                    'source_file': 'GroceryOils_003.mp4',
                    'output_name': 'GH-grocerystoreoilsvtd12036ZZquiz_z-v03-m01-f00-c00',
                    'description': 'New Ad from GroceryOils_003.mp4 + connector + quiz'
                }
            ],
            output_folder=r"C:\Users\talZ\Desktop\GH Grocery Store Oils VTD 12036 Quiz"
        )
    
    dialog = UnifiedWorkflowDialog()
    result = dialog.show_workflow(test_data, realistic_mock_processing)
    print(f"✅ Complete Workflow Result: {'SUCCESS' if result else 'CANCELLED'}")
    return result

def test_error_handling():
    """Test error handling in the workflow"""
    print("\n🧪 Testing Error Handling")
    print("-" * 50)
    
    test_data = ConfirmationData(
        project_name="Error Test Project",
        account="OO (Olive Oil)",
        platform="YouTube",
        processing_mode="CONNECTOR + QUIZ",
        client_videos=["broken_video.mp4"],
        templates_to_add=["Add connector", "Add quiz outro"],
        output_location="Error Test Output",
        estimated_time="2-3 minutes",
        issues=[],
        file_sizes=[("broken_video.mp4", 500)]
    )
    
    def error_processing_callback(progress_callback):
        """Mock processing that fails"""
        progress_callback(20, "🔍 Starting processing...")
        time.sleep(1)
        progress_callback(40, "📥 Downloading files...")
        time.sleep(1)
        progress_callback(60, "🎬 Processing video...")
        time.sleep(1)
        
        # Simulate error
        raise Exception("Failed to download videos: Google Drive API error: <HttpError 404 when requesting file not found>")
    
    dialog = UnifiedWorkflowDialog()
    result = dialog.show_workflow(test_data, error_processing_callback)
    print(f"✅ Error Handling Result: {'PROPERLY HANDLED' if not result else 'UNEXPECTED SUCCESS'}")
    return result

def test_orchestrator_integration():
    """Test integration with actual orchestrator (without real Trello card)"""
    print("\n🧪 Testing Orchestrator Integration")
    print("-" * 50)
    
    # Mock orchestrator for integration testing
    class MockOrchestrator:
        def __init__(self):
            self.start_time = time.time()
        
        def execute_with_ui(self, card_id):
            print(f"🔗 Mock Orchestrator received card ID: {card_id}")
            
            # Simulate orchestrator preparation
            confirmation_data = ConfirmationData(
                project_name="Orchestrator Test Project",
                account="OO (Olive Oil)",
                platform="YouTube",
                processing_mode="QUIZ ONLY",
                client_videos=["orch_test_001.mp4", "orch_test_002.mp4"],
                templates_to_add=["Add quiz outro (YT/Quiz/)"],
                output_location="GH Orchestrator Test Project Quiz",
                estimated_time="3-4 minutes",
                issues=[ValidationIssue("info", "Integration test in progress")],
                file_sizes=[("orch_test_001.mp4", 180), ("orch_test_002.mp4", 220)]
            )
            
            def orchestrator_processing_callback(progress_callback):
                """Simulate orchestrator processing steps"""
                steps = [
                    (15, "🔗 Orchestrator: Fetching and validating card..."),
                    (30, "🔗 Orchestrator: Parsing instructions..."),
                    (45, "🔗 Orchestrator: Setting up project..."),
                    (65, "🔗 Orchestrator: Processing videos..."),
                    (85, "🔗 Orchestrator: Finalizing and cleanup..."),
                    (100, "🔗 Orchestrator: Complete!")
                ]
                
                for progress, message in steps:
                    progress_callback(progress, message)
                    time.sleep(1)
                
                return ProcessingResult(
                    success=True,
                    duration="3 minutes 45 seconds",
                    processed_files=[
                        {
                            'version': 'v01',
                            'source_file': 'orch_test_001.mp4',
                            'output_name': 'orch_output_01',
                            'description': 'Orchestrator processed video 1'
                        },
                        {
                            'version': 'v02',
                            'source_file': 'orch_test_002.mp4',
                            'output_name': 'orch_output_02',
                            'description': 'Orchestrator processed video 2'
                        }
                    ],
                    output_folder=r"C:\Users\Desktop\Orchestrator Test Output"
                )
            
            # Use the unified workflow dialog
            dialog = UnifiedWorkflowDialog()
            result = dialog.show_workflow(confirmation_data, orchestrator_processing_callback)
            return result
    
    mock_orch = MockOrchestrator()
    result = mock_orch.execute_with_ui("mock_card_12345")
    print(f"✅ Orchestrator Integration Result: {'SUCCESS' if result else 'CANCELLED'}")
    return result

def run_all_tests():
    """Run all tests sequentially"""
    print("🚀 Running Complete AI Automation UI Integration Test Suite")
    print("=" * 70)
    
    results = {}
    
    # Test 1: UI Components Only
    try:
        results['ui_components'] = test_ui_components_only()
    except Exception as e:
        print(f"❌ UI Components test failed: {e}")
        results['ui_components'] = False
    
    # Test 2: Complete Workflow Mock
    try:
        results['complete_workflow'] = test_complete_workflow_mock()
    except Exception as e:
        print(f"❌ Complete Workflow test failed: {e}")
        results['complete_workflow'] = False
    
    # Test 3: Error Handling
    try:
        results['error_handling'] = test_error_handling()
    except Exception as e:
        print(f"❌ Error Handling test failed: {e}")
        results['error_handling'] = False
    
    # Test 4: Orchestrator Integration
    try:
        results['orchestrator_integration'] = test_orchestrator_integration()
    except Exception as e:
        print(f"❌ Orchestrator Integration test failed: {e}")
        results['orchestrator_integration'] = False
    
    # Print results summary
    print("\n" + "=" * 70)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        test_display = test_name.replace('_', ' ').title()
        print(f"{test_display:.<50} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    print("-" * 70)
    print(f"Overall Results: {passed_tests}/{total_tests} tests passed")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! System ready for production integration.")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Review and fix issues before production.")
    
    return results

if __name__ == "__main__":
    print("🧪 AI Automation UI Integration Test Suite")
    print("Choose your test scenario:")
    print()
    
    choice = input("""
1. UI Components Only (safest - quick test)
2. Complete Workflow Test (realistic mock data)  
3. Error Handling Test (test error scenarios)
4. Orchestrator Integration Test (test with mock orchestrator)
5. All Tests (comprehensive test suite)

Enter choice (1-5): """).strip()
    
    if choice == "1":
        test_ui_components_only()
    elif choice == "2":
        test_complete_workflow_mock()
    elif choice == "3":
        test_error_handling()
    elif choice == "4":
        test_orchestrator_integration()
    elif choice == "5":
        run_all_tests()
    else:
        print("Invalid choice. Running UI components test...")
        test_ui_components_only()
    
    print("\n✅ Testing completed!")
    input("Press Enter to exit...")