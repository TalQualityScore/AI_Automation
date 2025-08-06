# app/src/automation/api_clients/trello_client.py
"""
Trello API Client
Handles all Trello-specific operations
"""

import re
import requests
from typing import Dict, Optional, Tuple
from .config import TRELLO_API_KEY, TRELLO_TOKEN

class TrelloClient:
    """Handles Trello API operations"""
    
    def __init__(self):
        self.api_key = TRELLO_API_KEY
        self.token = TRELLO_TOKEN
        self.base_url = "https://api.trello.com/1"
    
    def get_card_data(self, card_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Fetch card name, description, and extract Google Drive link
        
        Args:
            card_id: Trello card ID
            
        Returns:
            Tuple of (card_data, error_message)
            card_data contains: name, desc, gdrive_url
        """
        
        if not self.api_key or not self.token:
            return None, "Trello API credentials not configured"
        
        url = f"{self.base_url}/cards/{card_id}"
        query = {
            "key": self.api_key, 
            "token": self.token
        }
        
        try:
            print(f"🔗 Fetching Trello card: {card_id}")
            response = requests.get(url, params=query, timeout=10)
            response.raise_for_status()
            card = response.json()
            
            card_name = card.get('name', '')
            card_desc = card.get('desc', '')
            
            print(f"📋 Card: {card_name}")
            print(f"📝 Description: {card_desc[:100]}...")
            
            # Extract Google Drive link from description
            gdrive_url = self.extract_gdrive_link(card_desc)
            
            if not gdrive_url:
                return None, "Google Drive link not found in Trello card description."
            
            return {
                "name": card_name,
                "desc": card_desc,
                "gdrive_url": gdrive_url
            }, None
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Trello API request failed: {e}"
            print(f"❌ {error_msg}")
            return None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error fetching Trello card: {e}"
            print(f"❌ {error_msg}")
            return None, error_msg
    
    def extract_gdrive_link(self, description: str) -> Optional[str]:
        """
        Extract Google Drive folder link from card description
        
        Args:
            description: Card description text
            
        Returns:
            Google Drive folder URL or None
        """
        
        if not description:
            return None
        
        # Look for Google Drive folder URLs
        gdrive_pattern = r'https?://drive\.google\.com/drive/folders/[\w-]+'
        match = re.search(gdrive_pattern, description)
        
        if match:
            url = match.group(0)
            print(f"🔗 Found Google Drive link: {url}")
            return url
        
        print(f"⚠️ No Google Drive link found in description")
        return None
    
    def validate_card_data(self, card_data: Dict) -> Tuple[bool, list]:
        """
        Validate card data for required fields
        
        Args:
            card_data: Card data dictionary
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        
        issues = []
        
        # Check card name
        if not card_data.get('name', '').strip():
            issues.append("Card has no title")
        
        # Check card description
        if not card_data.get('desc', '').strip():
            issues.append("Card has no description")
        
        # Check Google Drive link
        if not card_data.get('gdrive_url'):
            issues.append("No Google Drive link found in description")
        
        is_valid = len(issues) == 0
        return is_valid, issues