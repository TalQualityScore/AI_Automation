# local_automation.py - Simplified entry point
import sys
from app.src.automation.main_orchestrator import main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python local_automation.py <TRELLO_CARD_ID>")
        print("Example: python local_automation.py 'abc123xyz'")
    else:
        main(sys.argv[1])