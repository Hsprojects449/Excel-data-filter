"""
Minimal test script for executable export testing.
This will be built into a small test executable to isolate export issues.
"""
import sys
import tempfile
from pathlib import Path

def test_export():
    """Test export functionality in isolation."""
    try:
        import xlsxwriter
        print("xlsxwriter import: OK")
        
        import polars as pl
        print("polars import: OK")
        
        # Test xlsxwriter directly
        temp_dir = Path(tempfile.gettempdir())
        test_file = temp_dir / "test_xlsxwriter.xlsx"
        
        # Create a simple Excel file
        workbook = xlsxwriter.Workbook(str(test_file))
        worksheet = workbook.add_worksheet()
        
        worksheet.write(0, 0, "Name")
        worksheet.write(0, 1, "Value")
        worksheet.write(1, 0, "Test")
        worksheet.write(1, 1, 123)
        
        workbook.close()
        
        if test_file.exists():
            size = test_file.stat().st_size
            print(f"xlsxwriter test: OK ({size} bytes)")
            test_file.unlink()
        else:
            print("xlsxwriter test: FAILED - file not created")
            return False
        
        # Test polars CSV export
        df = pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})
        csv_file = temp_dir / "test_polars.csv"
        df.write_csv(csv_file)
        
        if csv_file.exists():
            size = csv_file.stat().st_size
            print(f"polars CSV test: OK ({size} bytes)")
            csv_file.unlink()
        else:
            print("polars CSV test: FAILED")
            return False
        
        # Test polars Excel export
        excel_file = temp_dir / "test_polars.xlsx"
        df.write_excel(excel_file)
        
        if excel_file.exists():
            size = excel_file.stat().st_size
            print(f"polars Excel test: OK ({size} bytes)")
            excel_file.unlink()
        else:
            print("polars Excel test: FAILED")
            return False
        
        print("ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing export functionality...")
    success = test_export()
    input("Press Enter to exit...")
    sys.exit(0 if success else 1)