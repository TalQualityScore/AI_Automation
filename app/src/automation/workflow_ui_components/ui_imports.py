# app/src/automation/workflow_ui_components/ui_imports.py
"""
Shared UI imports module - Optimizes startup time by centralizing imports
"""

# Core tkinter imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font

# Export all common UI components
__all__ = [
    'tk',
    'ttk', 
    'messagebox',
    'filedialog',
    'font'
]

# Commonly used tkinter constants
SIDE_LEFT = tk.LEFT
SIDE_RIGHT = tk.RIGHT
SIDE_TOP = tk.TOP
SIDE_BOTTOM = tk.BOTTOM
FILL_X = tk.X
FILL_Y = tk.Y
FILL_BOTH = tk.BOTH
ANCHOR_W = tk.W
ANCHOR_E = tk.E
ANCHOR_N = tk.N
ANCHOR_S = tk.S
ANCHOR_CENTER = tk.CENTER

# Export constants
__all__.extend([
    'SIDE_LEFT', 'SIDE_RIGHT', 'SIDE_TOP', 'SIDE_BOTTOM',
    'FILL_X', 'FILL_Y', 'FILL_BOTH',
    'ANCHOR_W', 'ANCHOR_E', 'ANCHOR_N', 'ANCHOR_S', 'ANCHOR_CENTER'
])