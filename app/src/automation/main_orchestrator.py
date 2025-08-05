# app/src/automation/main_orchestrator.py - NEW SIMPLIFIED VERSION
"""
Main orchestrator entry point - now delegates to the orchestrator module.
This file maintains backward compatibility while using the new modular structure.
"""

import sys
from .orchestrator import main

# For backward compatibility, expose the main function directly
def main_orchestrator_entry(card_id=None, use_ui=True):
    """Backward compatible entry point"""
    return main(card_id, use_ui)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main_orchestrator.py <TRELLO_CARD_ID> [--headless]")
        print("Example: python main_orchestrator.py 'abc123xyz'")
        print("         python main_orchestrator.py 'abc123xyz' --headless")
    else:
        card_id = sys.argv[1]
        use_ui = "--headless" not in sys.argv
        main(card_id, use_ui)