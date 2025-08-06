# app/__init__.py
"""
App package initialization

Makes 'app' a proper Python package so imports like 'app.naming_generator' work.
"""

# Import naming_generator from src and make it available at app.naming_generator
try:
    from .src import naming_generator
    print("✅ app.naming_generator path created successfully")
    
    # Make naming_generator available as app.naming_generator
    import sys
    sys.modules['app.naming_generator'] = naming_generator
    
except ImportError as e:
    print(f"⚠️ Could not create app.naming_generator path: {e}")

# This file makes the app directory a Python package