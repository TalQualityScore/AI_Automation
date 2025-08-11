# local_automation.py - FIXED entry point with UI integration
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib

# Clear module cache before importing
modules_to_clear = [
    'app.src.automation.main_orchestrator',
    'app.src.automation.unified_workflow_dialog',
    'app.src.automation.api_clients',
    'app.src.automation.video_processor',
    'app.src.automation.validation_engine',
    'app.src.automation.instruction_parser'
]

for module in modules_to_clear:
    if module in sys.modules:
        del sys.modules[module]

# Clear importlib cache
importlib.invalidate_caches()

from app.src.automation.main_orchestrator import main

def show_usage():
    """Show usage information"""
    print("🎬 AI Automation Suite - Production Ready")
    print("=" * 50)
    print("Usage:")
    print("  python local_automation.py                               # UI Mode (shows Trello popup)")
    print("  python local_automation.py <TRELLO_CARD_ID>              # UI Mode with card ID")
    print("  python local_automation.py <TRELLO_CARD_ID> --headless   # Headless Mode")
    print()
    print("Examples:")
    print("  python local_automation.py                               # Opens Trello card popup")
    print("  python local_automation.py 'abc123xyz'")
    print("  python local_automation.py 'abc123xyz' --headless") 
    print()
    print("Modes:")
    print("  UI Mode      - Shows confirmation dialog, progress, and results")
    print("  Headless     - Command-line only (legacy mode)")

if __name__ == "__main__":
    # FIXED: Handle no arguments case - show UI with popup
    if len(sys.argv) == 1:
        # No arguments provided - show UI with Trello card popup
        print("🚀 Starting AI Automation Suite (UI Mode with Trello Card Popup)")
        print("-" * 50)
        try:
            success = main(card_id=None, use_ui=True)  # This will trigger the popup
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
        sys.exit(0)
    
    # Check for special flags
    if "--help" in sys.argv or "-h" in sys.argv:
        show_usage()
        sys.exit(0)
    
    # Handle arguments provided
    card_id = sys.argv[1]
    
    # Validate card ID  
    if not card_id or card_id.startswith('--'):
        print("❌ Error: Invalid Trello card ID")
        print("💡 Use --help to see usage examples")
        show_usage()
        sys.exit(1)
    
    # Determine mode
    use_ui = "--headless" not in sys.argv
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