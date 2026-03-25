#!/usr/bin/env python
"""Test imports and basic syntax."""
import sys
import os

os.chdir('c:\\Users\\khanf\\OneDrive\\Documents\\Buildmyx1')

try:
    print("Testing imports...")
    import config
    print("✓ config.py")
    
    import data_utils
    print("✓ data_utils.py")
    
    import optimizer
    print("✓ optimizer.py")
    
    import draft
    print("✓ draft.py")
    
    import pitch_viz
    print("✓ pitch_viz.py")
    
    print("\n✓ All modules import successfully!")
    
except SyntaxError as e:
    print(f"✗ Syntax Error: {e}")
    import traceback
    traceback.print_exc()
except ImportError as e:
    print(f"✗ Import Error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
