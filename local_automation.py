# local_automation.py - Enhanced entry point with UI integration
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.src.automation.main_orchestrator import main

def show_usage():
    """Show usage information"""
    print("🎬 AI Automation Suite - Production Ready")
    print("=" * 50)
    print("Usage:")
    print("  python local_automation.py <TRELLO_CARD_ID>              # UI Mode (recommended)")
    print("  python local_automation.py <TRELLO_CARD_ID> --headless   # Headless Mode")
    print("  python local_automation.py --test                        # Run Integration Tests")
    print()
    print("Examples:")
    print("  python local_automation.py 'abc123xyz'")
    print("  python local_automation.py 'abc123xyz' --headless") 
    print("  python local_automation.py --test")
    print()
    print("Modes:")
    print("  UI Mode      - Shows confirmation dialog, progress, and results")
    print("  Headless     - Command-line only (legacy mode)")
    print("  Test Mode    - Run integration tests for the UI system")

def run_integration_tests():
    """Run the integration test suite"""
    try:
        from test_integration_fixed import run_all_tests
        print("🧪 Starting Integration Test Suite...")
        print("-" * 50)
        run_all_tests()
    except ImportError as e:
        print(f"❌ Could not import test suite: {e}")
        print("Make sure test_integration_fixed.py is in the project root.")
    except Exception as e:
        print(f"❌ Test suite failed: {e}")

if __name__ == "__main__":
    # Handle special cases
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    
    # Check for test mode
    if "--test" in sys.argv:
        run_integration_tests()
        sys.exit(0)
    
    # Get card ID and determine mode
    card_id = sys.argv[1]
    use_ui = "--headless" not in sys.argv
    
    # Validate card ID
    if not card_id or card_id.startswith('--'):
        print("❌ Error: Invalid Trello card ID")
        show_usage()
        sys.exit(1)
    
    # Show mode information
    mode = "UI Mode" if use_ui else "Headless Mode"
    print(f"🚀 Starting AI Automation Suite ({mode})")
    print(f"📋 Card ID: {card_id}")
    print("-" * 50)
    
    # Execute automation
    try:
        success = main(card_id, use_ui)
        
        if success:
            print("\n🎉 Automation completed successfully!")
        else:
            print("\n❌ Automation was cancelled or failed.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Automation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Automation failed: {e}")
        sys.exit(1)