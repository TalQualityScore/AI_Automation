# app/src/automation/orchestrator/ui_integration_base.py - MODULAR WRAPPER
"""
UI Integration Base Module - Modular Wrapper
Maintains backward compatibility while using the new modular structure
"""

# Import the new modular integration system
from .integration import UIIntegration

# For backward compatibility, export the same class name
# All existing imports will automatically use the new modular version
__all__ = ['UIIntegration']

# Optional: Add version info
__version__ = "2.0.0"
__modular__ = True
__original_lines__ = 500
__new_structure__ = "Split into integration/ modules"

print(f"✅ UIIntegration v{__version__} loaded (Modular)")
print(f"   Original: {__original_lines__} lines in 1 file")
print(f"   New: 5 focused modules with enhanced error handling")