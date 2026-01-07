# run.py
import sys
import os
import locale

# Set the locale to use UTF-8 encoding
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        print("Warning: Could not set UTF-8 locale")

# Set environment variables
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import and run the main script
from main import main

if __name__ == "__main__":
    main()
