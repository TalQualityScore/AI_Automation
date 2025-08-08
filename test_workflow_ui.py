#!/usr/bin/env python3
"""
COMPREHENSIVE Test script to check ALL UI components and methods
Run this from the project root: python test_workflow_ui.py
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_workflow():
    """Test the complete workflow UI with actual component creation"""
    print("=" * 60)
    print("COMPREHENSIVE UI COMPONENT TEST")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Create test root window (hidden)
    root = tk.Tk()
    root.withdraw()
    
    try:
        # TEST 1: Import all required modules
        print("\n1. TESTING IMPORTS...")
        print("-" * 40)
        
        try:
            from app.src.automation.workflow_data_models import ConfirmationData, ValidationIssue, ProcessingResult
            print("✅ workflow_data_models imported")
        except Exception as e:
            errors.append(f"Cannot import workflow_data_models: {e}")
            print(f"❌ workflow_data_models: {e}")
            return False  # Critical failure
        
        try:
            from app.src.automation.workflow_ui_components import WorkflowTheme
            print("✅ WorkflowTheme imported")
        except Exception as e:
            errors.append(f"Cannot import WorkflowTheme: {e}")
            print(f"❌ WorkflowTheme: {e}")
        
        try:
            from app.src.automation.workflow_ui_components.confirmation_tab import ConfirmationTab
            print("✅ ConfirmationTab imported")
        except Exception as e:
            errors.append(f"Cannot import ConfirmationTab: {e}")
            print(f"❌ ConfirmationTab: {e}")
        
        try:
            from app.src.automation.workflow_ui_components.processing_tab import ProcessingTab
            print("✅ ProcessingTab imported")
        except Exception as e:
            errors.append(f"Cannot import ProcessingTab: {e}")
            print(f"❌ ProcessingTab: {e}")
        
        try:
            from app.src.automation.workflow_ui_components.results_tab import ResultsTab
            print("✅ ResultsTab imported")
        except Exception as e:
            errors.append(f"Cannot import ResultsTab: {e}")
            print(f"❌ ResultsTab: {e}")
        
        # TEST 2: Create test data
        print("\n2. CREATING TEST DATA...")
        print("-" * 40)
        
        test_data = ConfirmationData(
            project_name="Test Project",
            account="OO (Olive Oil)",
            platform="Facebook",
            processing_mode="QUIZ ONLY",
            client_videos=["video1.mp4", "video2.mp4"],
            templates_to_add=["Add quiz outro (Facebook/Quiz/)"],
            output_location="Test Output Folder",
            estimated_time="2-3 minutes",
            issues=[],
            file_sizes=[("video1.mp4", 150), ("video2.mp4", 200)]
        )
        print("✅ Test ConfirmationData created")
        
        # TEST 3: Create Theme
        print("\n3. TESTING THEME...")
        print("-" * 40)
        
        theme = WorkflowTheme(root)
        
        # Check color keys
        required_colors = ['bg', 'accent', 'success', 'warning', 'error', 
                          'text_primary', 'text_secondary', 'border', 
                          'tab_active', 'tab_inactive']
        
        for color in required_colors:
            if color not in theme.colors:
                errors.append(f"Theme missing color: {color}")
                print(f"❌ Missing color: {color}")
            else:
                print(f"✅ Color '{color}' exists: {theme.colors[color]}")
        
        # Check for wrong 'primary' key
        if 'primary' in theme.colors:
            warnings.append("Theme has unexpected 'primary' color key")
            print("⚠️ Theme has 'primary' key (should use 'accent')")
        
        # TEST 4: Create and test ConfirmationTab
        print("\n4. TESTING CONFIRMATION TAB...")
        print("-" * 40)
        
        test_frame = ttk.Frame(root)
        
        try:
            confirmation_tab = ConfirmationTab(test_frame, test_data, theme)
            print("✅ ConfirmationTab created successfully")
            
            # Check for required methods
            required_methods = ['create_tab', 'set_orchestrator', 'set_dialog_controller', 
                              'get_updated_data', '_create_ui', '_on_confirm', '_on_cancel']
            
            for method in required_methods:
                if not hasattr(confirmation_tab, method):
                    errors.append(f"ConfirmationTab missing method: {method}")
                    print(f"❌ Missing method: {method}")
                else:
                    print(f"✅ Method '{method}' exists")
            
            # Test create_tab method
            try:
                tab_frame = confirmation_tab.create_tab()
                print("✅ create_tab() executed successfully")
                if tab_frame is None:
                    errors.append("create_tab() returned None")
                    print("❌ create_tab() returned None")
            except Exception as e:
                errors.append(f"create_tab() failed: {e}")
                print(f"❌ create_tab() failed: {e}")
            
            # Check state variables
            if not hasattr(confirmation_tab, 'use_transitions'):
                errors.append("ConfirmationTab missing 'use_transitions' variable")
                print("❌ Missing 'use_transitions' variable")
            else:
                print(f"✅ use_transitions variable exists")
                
        except Exception as e:
            errors.append(f"ConfirmationTab creation failed: {e}")
            print(f"❌ ConfirmationTab creation failed: {e}")
        
        # TEST 5: Test ProcessingTab
        print("\n5. TESTING PROCESSING TAB...")
        print("-" * 40)
        
        try:
            processing_tab = ProcessingTab(test_frame, theme)
            print("✅ ProcessingTab created successfully")
            
            # Check for required methods
            required_methods = ['create_tab', 'start_processing', 'update_progress']
            
            for method in required_methods:
                if not hasattr(processing_tab, method):
                    errors.append(f"ProcessingTab missing method: {method}")
                    print(f"❌ Missing method: {method}")
                else:
                    print(f"✅ Method '{method}' exists")
                    
        except Exception as e:
            errors.append(f"ProcessingTab creation failed: {e}")
            print(f"❌ ProcessingTab creation failed: {e}")
        
        # TEST 6: Test ResultsTab
        print("\n6. TESTING RESULTS TAB...")
        print("-" * 40)
        
        try:
            results_tab = ResultsTab(test_frame, theme)
            print("✅ ResultsTab created successfully")
            
            # Check for required methods
            required_methods = ['create_tab', 'show_success_results', 'show_error_results']
            
            for method in required_methods:
                if not hasattr(results_tab, method):
                    errors.append(f"ResultsTab missing method: {method}")
                    print(f"❌ Missing method: {method}")
                else:
                    print(f"✅ Method '{method}' exists")
                    
        except Exception as e:
            errors.append(f"ResultsTab creation failed: {e}")
            print(f"❌ ResultsTab creation failed: {e}")
        
        # TEST 7: Test Dialog Controller
        print("\n7. TESTING DIALOG CONTROLLER...")
        print("-" * 40)
        
        try:
            from app.src.automation.workflow_dialog.dialog_controller import UnifiedWorkflowDialog
            dialog = UnifiedWorkflowDialog(root)
            print("✅ UnifiedWorkflowDialog created")
            
            # Check required methods
            required_methods = ['show_workflow', 'set_orchestrator', '_create_dialog']
            
            for method in required_methods:
                if not hasattr(dialog, method):
                    errors.append(f"UnifiedWorkflowDialog missing method: {method}")
                    print(f"❌ Missing method: {method}")
                else:
                    print(f"✅ Method '{method}' exists")
                    
        except Exception as e:
            errors.append(f"UnifiedWorkflowDialog creation failed: {e}")
            print(f"❌ UnifiedWorkflowDialog: {e}")
        
        # TEST 8: Check for common attribute errors
        print("\n8. CHECKING FOR COMMON ERRORS...")
        print("-" * 40)
        
        # Read confirmation_tab source to check for common mistakes
        try:
            import inspect
            source = inspect.getsource(ConfirmationTab)
            
            problematic_patterns = [
                ("self.theme.colors['primary']", "Should use 'accent' not 'primary'"),
                ("self.data.account_info", "Should use 'account' not 'account_info'"),
                ("self.data.mode", "Should use 'processing_mode' not 'mode'"),
                ("self.data.output_file", "Should use 'output_location' not 'output_file'")
            ]
            
            for pattern, message in problematic_patterns:
                if pattern in source:
                    errors.append(f"ConfirmationTab source: {message}")
                    print(f"❌ Found '{pattern}': {message}")
                else:
                    print(f"✅ Pattern '{pattern}' not found (good)")
                    
        except Exception as e:
            warnings.append(f"Could not inspect source: {e}")
            print(f"⚠️ Could not inspect source: {e}")
        
    except Exception as e:
        errors.append(f"Unexpected error during testing: {e}")
        print(f"❌ Unexpected error: {e}")
    
    finally:
        root.destroy()
    
    # SUMMARY
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ FOUND {len(errors)} ERROR(S):\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    
    if warnings:
        print(f"\n⚠️ FOUND {len(warnings)} WARNING(S):\n")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    if not errors:
        print("\n✅ ALL TESTS PASSED! The UI should work correctly.")
    else:
        print("\n" + "=" * 60)
        print("FIXES REQUIRED")
        print("=" * 60)
        
        # Provide specific fixes based on errors
        if any("create_tab" in str(e) for e in errors):
            print("\nFIX: ConfirmationTab needs a create_tab() method that returns a frame:")
            print("```python")
            print("def create_tab(self):")
            print("    '''Create and return the tab frame'''")
            print("    if not hasattr(self, 'frame'):")
            print("        self.frame = ttk.Frame(self.parent, style='White.TFrame')")
            print("        self._create_ui()  # Build the UI in the frame")
            print("    return self.frame")
            print("```")
        
        if any("'primary'" in str(e) for e in errors):
            print("\nFIX: Change all occurrences of:")
            print("  FROM: self.theme.colors['primary']")
            print("  TO:   self.theme.colors['accent']")
    
    return len(errors) == 0

if __name__ == "__main__":
    try:
        success = test_complete_workflow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)