# app/src/automation/orchestrator/processing/coordinator_modules/path_resolver.py
"""
Path Resolver Module
Resolves and validates various project paths
"""

import os

class PathResolver:
    """Resolves project paths with multiple strategies"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def resolve_client_videos_path(self, project_paths):
        """
        Resolve the client videos path using multiple strategies
        
        Args:
            project_paths: Dictionary of project paths
            
        Returns:
            Path to client videos folder or None
        """
        print(f"🔍 DEBUG - Checking project paths...")
        
        # Validate project_paths
        if not project_paths:
            print(f"❌ ERROR: project_paths not available")
            
            # Try to get from orchestrator
            if hasattr(self.orchestrator, 'project_paths'):
                project_paths = self.orchestrator.project_paths
                print(f"✅ Retrieved project_paths from orchestrator")
            else:
                print(f"❌ No project_paths found in orchestrator either")
                return None
        
        print(f"✅ Found project_paths: {list(project_paths.keys())}")
        
        # Try multiple strategies to find client videos path
        client_videos_path = None
        
        # Strategy 1: Direct client_videos key
        if 'client_videos' in project_paths:
            client_videos_path = project_paths['client_videos']
            print(f"📁 Found client_videos path (direct): {client_videos_path}")
            return client_videos_path
        
        # Strategy 2: Look for _Footage/Video/Client pattern
        if 'base_output' in project_paths:
            client_videos_path = self._try_base_output_strategy(project_paths['base_output'])
            if client_videos_path:
                return client_videos_path
        
        # Strategy 3: Search for any path containing "Client"
        client_videos_path = self._search_for_client_path(project_paths)
        if client_videos_path:
            return client_videos_path
        
        print("❌ ERROR: Could not determine client videos path")
        print(f"   Available paths: {project_paths}")
        return None
    
    def _try_base_output_strategy(self, base_path):
        """Try to find client path via base_output"""
        potential_path = os.path.join(base_path, '_Footage', 'Video', 'Client')
        
        if os.path.exists(potential_path):
            print(f"📁 Found client path via base_output: {potential_path}")
            return potential_path
        
        # Try to create it
        try:
            os.makedirs(potential_path, exist_ok=True)
            print(f"📁 Created client path via base_output: {potential_path}")
            return potential_path
        except Exception as e:
            print(f"❌ Could not create client path: {e}")
            return None
    
    def _search_for_client_path(self, project_paths):
        """Search for any path containing 'Client'"""
        for key, path in project_paths.items():
            if 'Client' in path or 'client' in path:
                print(f"📁 Found client path via search ({key}): {path}")
                return path
        return None
    
    def ensure_directory_exists(self, directory_path):
        """Ensure a directory exists, create if necessary"""
        if directory_path:
            os.makedirs(directory_path, exist_ok=True)
            print(f"✅ Directory ready: {directory_path}")
            return True
        return False