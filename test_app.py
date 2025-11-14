#!/usr/bin/env python3
"""
Simple test script to verify the application can start without errors.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        # Test core imports
        from ui.main_window import MainWindow
        from ui.preview_table import PreviewTable
        from ui.filter_panel import FilterPanel
        from core.excel_reader import ExcelReader
        from core.filter_engine import FilterEngine
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_ui_creation():
    """Test that UI components can be created without errors."""
    try:
        from PyQt6.QtWidgets import QApplication
        
        # Create application (required for widgets)
        app = QApplication([])
        
        # Test widget creation
        from ui.preview_table import PreviewTable
        preview_table = PreviewTable()
        
        from ui.filter_panel import FilterPanel
        filter_panel = FilterPanel()
        
        print("✅ UI components created successfully")
        
        # Clean up
        app.quit()
        return True
    except Exception as e:
        print(f"❌ UI creation error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Excel Data Filter Application")
    print("-" * 40)
    
    # Run tests
    import_success = test_imports()
    ui_success = test_ui_creation()
    
    if import_success and ui_success:
        print("\n🎉 All tests passed! Application should work correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)