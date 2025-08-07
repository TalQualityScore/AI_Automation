# app/src/automation/preflight_checks.py
"""
Preflight checks to verify environment before starting automation
Run these checks early to fail fast with clear error messages
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
from dotenv import load_dotenv

class PreflightError(Exception):
    """Custom exception for preflight check failures"""
    pass

class PreflightChecker:
    """Performs preflight checks before automation starts"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def run_all_checks(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run all preflight checks
        
        Returns:
            Tuple of (success, errors, warnings)
        """
        print("🔍 Running preflight checks...")
        
        # Load environment variables
        load_dotenv()
        
        # Check Python version
        self._check_python_version()
        
        # Check FFmpeg
        self._check_ffmpeg()
        
        # Check environment variables
        self._check_environment_variables()
        
        # Check Google credentials
        self._check_google_credentials()
        
        # Check required directories
        self._check_required_directories()
        
        # Check disk space
        self._check_disk_space()
        
        # Print results
        if self.errors:
            print("\n❌ Preflight checks FAILED:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("\n⚠️ Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if not self.errors:
            print("✅ All preflight checks passed!")
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _check_python_version(self):
        """Check Python version is 3.11+"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            self.errors.append(
                f"Python 3.11+ required, but found {version.major}.{version.minor}.{version.micro}"
            )
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is installed and accessible"""
        ffmpeg_path = shutil.which("ffmpeg")
        
        if not ffmpeg_path:
            self.errors.append(
                "FFmpeg not found in PATH. Please install FFmpeg and add it to your system PATH.\n"
                "      Download from: https://ffmpeg.org/download.html"
            )
            return
        
        # Try to get version
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if lines:
                    version_line = lines[0]
                    print(f"   ✓ FFmpeg found: {version_line}")
        except Exception as e:
            self.warnings.append(f"Could not verify FFmpeg version: {e}")
    
    def _check_environment_variables(self):
        """Check required environment variables"""
        required_vars = {
            "TRELLO_API_KEY": "Trello API key for card management",
            "TRELLO_TOKEN": "Trello authentication token",
            "GOOGLE_SHEET_ID": "Google Sheets ID for tracking"
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value or value == f"your_{var.lower()}_here":
                missing_vars.append(f"{var}: {description}")
        
        if missing_vars:
            self.errors.append(
                "Missing or unconfigured environment variables:\n" +
                "\n".join(f"      • {var}" for var in missing_vars) +
                "\n      Please copy .env.example to .env and configure it"
            )
    
    def _check_google_credentials(self):
        """Check Google service account credentials"""
        cred_file = os.getenv("SERVICE_ACCOUNT_FILE", "credentials.json")
        
        if not os.path.exists(cred_file):
            self.errors.append(
                f"Google credentials file not found: {cred_file}\n"
                "      Please download your service account JSON from Google Cloud Console\n"
                "      and save it as 'credentials.json' in the project root"
            )
            return
        
        # Check if file is valid JSON
        try:
            import json
            with open(cred_file, 'r') as f:
                creds = json.load(f)
                if 'type' in creds and creds['type'] == 'service_account':
                    print(f"   ✓ Google credentials found: {cred_file}")
                else:
                    self.warnings.append(
                        f"Credentials file exists but may not be a service account key"
                    )
        except Exception as e:
            self.errors.append(f"Invalid credentials file: {e}")
    
    def _check_required_directories(self):
        """Check if required directories exist"""
        required_dirs = {
            "Assets": "Asset templates and resources",
            "Assets/Videos/connectors": "Connector video templates",
            "Assets/Videos/quiz_outro": "Quiz outro templates"
        }
        
        missing_dirs = []
        for dir_path, description in required_dirs.items():
            if not os.path.exists(dir_path):
                missing_dirs.append(f"{dir_path}: {description}")
        
        if missing_dirs:
            self.warnings.append(
                "Missing asset directories (will affect some features):\n" +
                "\n".join(f"      • {dir_info}" for dir_info in missing_dirs)
            )
    
    def _check_disk_space(self):
        """Check available disk space"""
        try:
            import shutil
            stat = shutil.disk_usage(".")
            free_gb = stat.free / (1024 ** 3)
            
            if free_gb < 1:
                self.errors.append(
                    f"Insufficient disk space: {free_gb:.2f} GB free (minimum 1 GB required)"
                )
            elif free_gb < 5:
                self.warnings.append(
                    f"Low disk space: {free_gb:.2f} GB free (recommend at least 5 GB)"
                )
            else:
                print(f"   ✓ Disk space: {free_gb:.1f} GB available")
        except Exception as e:
            self.warnings.append(f"Could not check disk space: {e}")

def run_preflight_checks() -> bool:
    """
    Convenience function to run all preflight checks
    
    Returns:
        True if all checks pass, False otherwise
    """
    checker = PreflightChecker()
    success, errors, warnings = checker.run_all_checks()
    
    if not success:
        print("\n⛔ Cannot proceed until preflight errors are resolved.")
        print("Please fix the issues above and try again.")
    
    return success

def require_preflight_checks():
    """
    Run preflight checks and exit if they fail
    Call this at the start of your main script
    """
    if not run_preflight_checks():
        sys.exit(1)