# --- File: run_for_build.py ---
# This is a special entry point script just for PyInstaller.
# It correctly sets up the path and runs the application as a module,
# which solves relative import errors during the build process.

import runpy
import sys
import os

# Ensure the project's root directory is on the Python path.
# This allows the 'app' package to be found.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Use runpy to execute the app.src package. This is the correct
# way to run a package and is what `python -m app.src` does internally.
runpy.run_module("app.src", run_name="__main__")
