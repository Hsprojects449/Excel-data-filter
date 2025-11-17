"""
Runtime hook for PyInstaller to optimize module loading.
This runs before the main application starts.
"""

import os
import sys

# Disable bytecode writing to speed up imports
sys.dont_write_bytecode = True

# Set environment variables to optimize library behavior
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Disable polars string cache preloading for faster startup
os.environ['POLARS_EAGER_EXECUTION'] = '1'

# Optimize Qt for faster startup
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
