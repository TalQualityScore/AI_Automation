# test_integration.py - Test the complete UI integration
import sys
import os
import time

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.src.automation.workflow_controller import (
    AutomationWorkflowController, 
    create_confirmation_data_from_orchestrator,
    create_processing_result_from_orchestrator
)
from app.src.automation.confirmation_dialog import ConfirmationData, ValidationIssue
from app.src.automation.results_dialog import ProcessingResult

def test_with_real_trello_card():
    """Test the UI with a real Trello card (without actual processing)"""
    
    # Simulate your existing orchestrator data
    mock_card_data = {
        'name': 'OO_GroceryStoreOils_AD_VTD-12036A_003.mp4',
        'desc': 'Process these videos with connector and quiz outro. Google Drive link: https://drive.google.com/drive/folders/1234567890'
    }
    
    mock_project_info = {
        'project_name': 'Grocery Store Oils',
        'ad_type': 'VTD',
        'test_name': '12036',
        'version_letter': 'A',
        'account_code': 'OO'
    }
    
    mock_downloaded_videos = [
        'video1.mp4',
        'video2.mp4', 
        'video3.mp4'
    ]
    
    mock_validation_issues = [
        {'severity': 'warning', 'message': 'Large file detected (1200MB)'},
        {'severity': 'info', 'message': 'Processing will create high-quality output'}
    ]
    
    # Create confirmation data using helper function
    confirmation_data = create_confirmation_data_from_orchestrator(
        card_data=mock_card_data,
        processing_mode='connector_quiz',
        project_info=mock_project_info,
        downloaded_videos=mock_downloaded_videos,
        validation_issues=mock_validation_issues
    )
    
    def mock_processing_callback(progress_callback):
        """Mock processing that simulates your orchestrator"""
        steps = [
            (10, "🔍 Validating Trello card data..."),
            (25, "📥 Downloading videos from Google Drive..."),
            (40, "📐 Analyzing video dimensions..."),
            (55, "🎬 Processing video 1 of 3..."),
            (70, "🎬 Processing video 2 of 3..."),
            (85, "🎬 Processing video 3 of 3..."),
            (95, "✨ Applying effects and saving..."),
            (100, "🎉 Processing complete!")
        ]
        
        start_time = time.time()
        
        for progress, message in steps:
            progress_callback(progress, message)
            time.sleep(1.5)  # Simulate processing time
        
        # Return successful result
        return create_processing_result_from_orchestrator(
            processed_files=[
                {
                    'version': 'v01',
                    'source_file': 'video1.mp4', 
                    'output_name': 'GH-grocerystoreoilsvtd12036ZZquiz_x-v01-m01-f00-c00',
                    'description': 'New Ad from video1.mp4 + connector + quiz',
                    'duration': '1:45'
                },
                {
                    'version': 'v02',
                    'source_file': 'video2.mp4',
                    'output_name': 'GH-grocerystoreoilsvtd12036ZZquiz_y-v02-m01-f00-c00', 
                    'description': 'New Ad from video2.mp4 + connector + quiz',
                    'duration': '2:12'
                }
            ],
            start_time=start_time,
            output_folder=r"C:\Users\talZ\Desktop\GH Grocery Store Oils VTD 12036 Quiz",
            success=True
        )
    
    # Start the workflow
    controller = AutomationWorkflowController()
    success = controller.start_workflow(
        confirmation_data=confirmation_data,
        processing_callback=mock_processing_callback,
        estimated_duration="3-5 minutes"
    )
    
    print(f"\n{'='*60}")
    print(f"🎯 INTEGRATION TEST RESULT: {'SUCCESS' if success else 'CANCELLED/FAILED'}")
    print(f"{'='*60}")
    
    return success

def test_error_scenario():
    """Test the error handling workflow"""
    
    confirmation_data = ConfirmationData(
        project_name="Test Error Project",
        account="OO (Olive Oil)",
        platform="YouTube",
        processing_mode="CONNECTOR + QUIZ", 
        client_videos=["broken_video.mp4"],
        templates_to_add=["Add connector", "Add quiz outro"],
        output_location="Test Error Output",
        estimated_time="2-3 minutes",
        issues=[],
        file_sizes=[("broken_video.mp4", 500)]
    )
    
    def error_processing_callback(progress_callback):
        """Mock processing that fails"""
        progress_callback(20, "Starting processing...")
        time.sleep(1)
        progress_callback(40, "Downloading files...")
        time.sleep(1)
        
        # Simulate error
        raise Exception("Failed to download videos: Google Drive API error - File not found")
    
    controller = AutomationWorkflowController()
    success = controller.start_workflow(
        confirmation_data=confirmation_data,
        processing_callback=error_processing_callback,
        estimated_duration="2-3 minutes"
    )
    
    print(f"\n{'='*60}")
    print(f"🎯 ERROR TEST RESULT: {'SUCCESS' if success else 'PROPERLY HANDLED ERROR'}")
    print(f"{'='*60}")
    
    return success

def test_ui_only():
    """Test just the UI components without processing"""
    print("🧪 Testing UI Components Only...")
    
    # Test confirmation dialog
    print("\n1. Testing Confirmation Dialog...")
    from app.src.automation.confirmation_dialog import test_confirmation_dialog
    test_confirmation_dialog()
    
    # Test processing dialog
    print("\n2. Testing Processing Dialog...")
    from app.src.automation.processing_dialog import test_processing_dialog  
    test_processing_dialog()
    
    # Test results dialogs
    print("\n3. Testing Success Dialog...")
    from app.src.automation.results_dialog import test_success_dialog
    test_success_dialog()
    
    print("\n4. Testing Error Dialog...")
    from app.src.automation.results_dialog import test_error_dialog
    test_error_dialog()

if __name__ == "__main__":
    print("🚀 AI Automation UI Integration Tests")
    print("="*60)
    
    test_choice = input("""
Choose test type:
1. UI Components Only (safe)
2. Complete Workflow (with mock data)
3. Error Handling Test
4. All Tests

Enter choice (1-4): """).strip()
    
    if test_choice == "1":
        test_ui_only()
    elif test_choice == "2":
        test_with_real_trello_card()
    elif test_choice == "3": 
        test_error_scenario()
    elif test_choice == "4":
        print("\n🧪 Running All Tests...")
        test_ui_only()
        input("\nPress Enter to continue to workflow test...")
        test_with_real_trello_card()
        input("\nPress Enter to continue to error test...")
        test_error_scenario()
    else:
        print("Invalid choice. Running UI tests only...")
        test_ui_only()
    
    print("\n✅ Testing completed!")