# app/src/automation/client_database.py
"""
Client and Account Database System
Manages client information, account codes, and project tracking
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ClientInfo:
    """Client information structure"""
    account_code: str
    full_name: str
    industry: str
    contact_email: str
    contact_name: str
    active: bool = True
    created_date: str = ""
    last_project_date: str = ""
    total_projects: int = 0
    notes: str = ""

@dataclass
class ProjectRecord:
    """Individual project record"""
    project_name: str
    account_code: str
    processing_mode: str
    files_processed: int
    duration: str
    date_completed: str
    output_folder: str
    trello_card_id: str = ""

class ClientDatabase:
    """Manages client and project data"""
    
    def __init__(self, db_file: str = "client_database.json"):
        self.db_file = db_file
        self.clients: Dict[str, ClientInfo] = {}
        self.projects: List[ProjectRecord] = []
        self.load_database()
    
    def load_database(self):
        """Load database from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load clients
                for code, client_data in data.get('clients', {}).items():
                    self.clients[code] = ClientInfo(**client_data)
                
                # Load projects
                for project_data in data.get('projects', []):
                    self.projects.append(ProjectRecord(**project_data))
                    
            except Exception as e:
                print(f"Error loading database: {e}")
                self.initialize_default_clients()
        else:
            self.initialize_default_clients()
    
    def save_database(self):
        """Save database to JSON file"""
        try:
            data = {
                'clients': {code: asdict(client) for code, client in self.clients.items()},
                'projects': [asdict(project) for project in self.projects],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def initialize_default_clients(self):
        """Initialize database with default clients"""
        default_clients = [
            ClientInfo(
                account_code="OO",
                full_name="Olive Oil Company",
                industry="Food & Nutrition",
                contact_email="contact@oliveoil.com",
                contact_name="Marketing Team",
                created_date=datetime.now().isoformat()
            ),
            ClientInfo(
                account_code="MCT",
                full_name="MCT Oil Solutions",
                industry="Health & Wellness",
                contact_email="info@mctoil.com",
                contact_name="Content Manager",
                created_date=datetime.now().isoformat()
            ),
            ClientInfo(
                account_code="PP",
                full_name="Pro Plant Nutrition",
                industry="Plant-Based Products",
                contact_email="marketing@proplant.com",
                contact_name="Brand Manager",
                created_date=datetime.now().isoformat()
            ),
            ClientInfo(
                account_code="GH",
                full_name="Green House Organics",
                industry="Organic Foods",
                contact_email="team@greenhouse.com",
                contact_name="Creative Director",
                created_date=datetime.now().isoformat()
            ),
            ClientInfo(
                account_code="AT",
                full_name="Auto Tech Solutions",
                industry="Automotive",
                contact_email="support@autotech.com",
                contact_name="Marketing Lead",
                created_date=datetime.now().isoformat()
            )
        ]
        
        for client in default_clients:
            self.clients[client.account_code] = client
        
        self.save_database()
        print("✅ Initialized client database with default clients")
    
    def add_client(self, client: ClientInfo) -> bool:
        """Add new client to database"""
        if client.account_code in self.clients:
            print(f"⚠️ Client {client.account_code} already exists")
            return False
        
        client.created_date = datetime.now().isoformat()
        self.clients[client.account_code] = client
        self.save_database()
        print(f"✅ Added client: {client.account_code} - {client.full_name}")
        return True
    
    def get_client(self, account_code: str) -> Optional[ClientInfo]:
        """Get client by account code"""
        return self.clients.get(account_code.upper())
    
    def get_all_clients(self) -> Dict[str, ClientInfo]:
        """Get all clients"""
        return self.clients.copy()
    
    def get_active_clients(self) -> Dict[str, ClientInfo]:
        """Get only active clients"""
        return {code: client for code, client in self.clients.items() if client.active}
    
    def update_client(self, account_code: str, **updates) -> bool:
        """Update client information"""
        if account_code not in self.clients:
            return False
        
        client = self.clients[account_code]
        for key, value in updates.items():
            if hasattr(client, key):
                setattr(client, key, value)
        
        self.save_database()
        return True
    
    def add_project_record(self, project: ProjectRecord):
        """Add completed project record"""
        project.date_completed = datetime.now().isoformat()
        self.projects.append(project)
        
        # Update client statistics
        if project.account_code in self.clients:
            client = self.clients[project.account_code]
            client.total_projects += 1
            client.last_project_date = project.date_completed
        
        self.save_database()
        print(f"✅ Added project record: {project.project_name}")
    
    def get_client_projects(self, account_code: str) -> List[ProjectRecord]:
        """Get all projects for a specific client"""
        return [p for p in self.projects if p.account_code == account_code]
    
    def get_recent_projects(self, limit: int = 10) -> List[ProjectRecord]:
        """Get most recent projects"""
        sorted_projects = sorted(self.projects, key=lambda p: p.date_completed, reverse=True)
        return sorted_projects[:limit]
    
    def get_client_statistics(self) -> Dict:
        """Get database statistics"""
        stats = {
            'total_clients': len(self.clients),
            'active_clients': len([c for c in self.clients.values() if c.active]),
            'total_projects': len(self.projects),
            'projects_by_client': {},
            'most_active_client': None
        }
        
        # Projects by client
        for code, client in self.clients.items():
            client_projects = len(self.get_client_projects(code))
            stats['projects_by_client'][code] = {
                'name': client.full_name,
                'projects': client_projects
            }
        
        # Most active client
        if stats['projects_by_client']:
            most_active = max(stats['projects_by_client'].items(), 
                            key=lambda x: x[1]['projects'])
            stats['most_active_client'] = {
                'code': most_active[0],
                'name': most_active[1]['name'],
                'projects': most_active[1]['projects']
            }
        
        return stats
    
    def detect_account_from_project_name(self, project_name: str) -> Optional[str]:
        """Auto-detect account code from project name"""
        project_upper = project_name.upper()
        
        # Check for exact account code matches
        for code in self.clients.keys():
            if code in project_upper:
                return code
        
        # Check for client name matches
        for code, client in self.clients.items():
            name_words = client.full_name.upper().split()
            if any(word in project_upper for word in name_words if len(word) > 3):
                return code
        
        return None
    
    def export_client_list(self) -> str:
        """Export client list as formatted text"""
        output = ["AI AUTOMATION - CLIENT DATABASE", "=" * 40, ""]
        
        for code, client in sorted(self.clients.items()):
            status = "✅ ACTIVE" if client.active else "❌ INACTIVE"
            output.extend([
                f"Account Code: {code}",
                f"Name: {client.full_name}",
                f"Industry: {client.industry}",
                f"Contact: {client.contact_name} ({client.contact_email})",
                f"Status: {status}",
                f"Total Projects: {client.total_projects}",
                f"Last Project: {client.last_project_date or 'Never'}",
                f"Notes: {client.notes or 'None'}",
                "-" * 30, ""
            ])
        
        return "\n".join(output)

# Global database instance
client_db = ClientDatabase()

# Helper functions for easy integration
def get_client_info(account_code: str) -> Optional[ClientInfo]:
    """Quick access to client info"""
    return client_db.get_client(account_code)

def add_project_completion(project_name: str, account_code: str, processing_mode: str, 
                         files_processed: int, duration: str, output_folder: str,
                         trello_card_id: str = ""):
    """Quick function to log completed project"""
    project = ProjectRecord(
        project_name=project_name,
        account_code=account_code,
        processing_mode=processing_mode,
        files_processed=files_processed,
        duration=duration,
        output_folder=output_folder,
        trello_card_id=trello_card_id
    )
    client_db.add_project_record(project)

def detect_client_from_project(project_name: str) -> Optional[ClientInfo]:
    """Detect and return client info from project name"""
    account_code = client_db.detect_account_from_project_name(project_name)
    if account_code:
        return client_db.get_client(account_code)
    return None

# Example usage and testing
if __name__ == "__main__":
    # Test the database
    print("🗄️ Testing Client Database System")
    print("-" * 40)
    
    # Show all clients
    clients = client_db.get_all_clients()
    print(f"📊 Loaded {len(clients)} clients:")
    for code, client in clients.items():
        print(f"  {code}: {client.full_name} ({client.industry})")
    
    # Test project detection
    test_projects = [
        "OO Grocery Store Oils VTD 12036",
        "MCT Health Benefits Quiz Campaign",
        "Green House Organic Foods Promo"
    ]
    
    print(f"\n🔍 Testing account detection:")
    for project in test_projects:
        detected = client_db.detect_account_from_project_name(project)
        print(f"  '{project}' → {detected}")
    
    # Show statistics
    stats = client_db.get_client_statistics()
    print(f"\n📈 Database Statistics:")
    print(f"  Total clients: {stats['total_clients']}")
    print(f"  Active clients: {stats['active_clients']}")
    print(f"  Total projects: {stats['total_projects']}")
    if stats['most_active_client']:
        print(f"  Most active: {stats['most_active_client']['name']} ({stats['most_active_client']['projects']} projects)")