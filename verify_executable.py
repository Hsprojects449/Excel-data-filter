"""
Test script to verify Excel_Data_Filter_Pro.exe can load and process Excel files.
This simulates what happens when a user opens an Excel file in the application.
"""
import sys
import traceback
from pathlib import Path

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

try:
    # Test importing core modules that use fastexcel/polars
    from core.excel_reader import ExcelReader
    
    print("✓ Successfully imported ExcelReader")
    
    # Test creating ExcelReader with our sample file
    test_file = Path("sample_test.xlsx")
    if test_file.exists():
        print(f"✓ Found test file: {test_file}")
        
        # Create reader instance
        reader = ExcelReader(str(test_file))
        print("✓ ExcelReader instance created successfully")
        
        # Test getting sheet names
        sheets = reader.get_sheet_names()
        print(f"✓ Sheet names retrieved: {sheets}")
        
        # Test reading sheet data
        df = reader.read_sheet("Employees")
        print(f"✓ Data loaded successfully - Shape: {df.shape}")
        print(f"✓ Columns: {list(df.columns)}")
        
        # Test getting statistics
        stats = reader.get_statistics()
        print(f"✓ Statistics: {stats}")
        
        print("\n🎉 ALL TESTS PASSED! The executable should work correctly with Excel files.")
        
    else:
        print(f"❌ Test file not found: {test_file}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)