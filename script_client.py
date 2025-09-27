#!/usr/bin/env python3
"""
Script Client - Minecraft Utility Client
Entry point for Minescript execution

Usage: \\script_client
"""

import sys
import os

# Set Python executable path (from config.txt)
python_path = r"C:\Users\snook\AppData\Local\Programs\Python\Python313\python.exe"
if os.path.exists(python_path):
    sys.executable = python_path

# Add the script_client directory to Python path
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'script_client')
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import and run the DearPyGui interface
from app import main

if __name__ == "__main__":
    main()
