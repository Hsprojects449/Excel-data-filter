"""
Test script to diagnose export issues in the executable.
This will help identify what's failing during export operations.
"""
import sys
import traceback
import tempfile
from pathlib import Path

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def test_export_functionality():
    """Test various export scenarios to identify the issue."""
    print("🔍 Testing Export Functionality in Development Environment\n")
    
    try:
        # Test imports first
        print("1. Testing imports...")
        from core.excel_reader import ExcelReader
        from core.exporter import ExcelExporter
        import polars as pl
        import xlsxwriter
        print("   ✅ All imports successful\n")
        
        # Test sample data creation
        print("2. Creating sample data...")
        test_data = {
            'ID': [1, 2, 3, 4, 5],
            'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'Value': [100, 200, 300, 400, 500]
        }
        df = pl.DataFrame(test_data)
        print(f"   ✅ Sample data created: {df.shape}\n")
        
        # Test exporter creation
        print("3. Creating ExcelExporter...")
        exporter = ExcelExporter(df)
        print("   ✅ ExcelExporter created\n")
        
        # Test temp directory access
        print("4. Testing file system access...")
        temp_dir = Path(tempfile.gettempdir())
        print(f"   Temp directory: {temp_dir}")
        print(f"   Temp dir exists: {temp_dir.exists()}")
        print(f"   Temp dir writable: {temp_dir.is_dir()}")
        
        # Test Excel export to temp file
        print("\n5. Testing Excel export...")
        temp_excel = temp_dir / "test_export.xlsx"
        
        def progress_callback(percentage, message):
            print(f"   Progress: {percentage}% - {message}")
            
        success = exporter.export(
            output_path=str(temp_excel),
            progress_callback=progress_callback
        )
        
        if success and temp_excel.exists():
            file_size = temp_excel.stat().st_size
            print(f"   ✅ Excel export successful! File size: {file_size} bytes")
            temp_excel.unlink()  # cleanup
        else:
            print(f"   ❌ Excel export failed! File exists: {temp_excel.exists()}")
        
        # Test CSV export
        print("\n6. Testing CSV export...")
        temp_csv = temp_dir / "test_export.csv"
        
        success = exporter.export_to_csv(
            output_path=str(temp_csv),
            progress_callback=progress_callback
        )
        
        if success and temp_csv.exists():
            file_size = temp_csv.stat().st_size
            print(f"   ✅ CSV export successful! File size: {file_size} bytes")
            temp_csv.unlink()  # cleanup
        else:
            print(f"   ❌ CSV export failed! File exists: {temp_csv.exists()}")
        
        # Test xlsxwriter directly
        print("\n7. Testing xlsxwriter directly...")
        temp_direct = temp_dir / "test_direct.xlsx"
        try:
            workbook = xlsxwriter.Workbook(str(temp_direct))
            worksheet = workbook.add_worksheet("Test")
            worksheet.write(0, 0, "Hello")
            worksheet.write(0, 1, "World")
            workbook.close()
            
            if temp_direct.exists():
                file_size = temp_direct.stat().st_size
                print(f"   ✅ Direct xlsxwriter test successful! File size: {file_size} bytes")
                temp_direct.unlink()
            else:
                print("   ❌ Direct xlsxwriter test failed!")
        except Exception as e:
            print(f"   ❌ Direct xlsxwriter error: {e}")
        
        # Test polars write operations
        print("\n8. Testing polars write operations...")
        temp_polars_csv = temp_dir / "test_polars.csv"
        temp_polars_excel = temp_dir / "test_polars.xlsx"
        
        try:
            # CSV write
            df.write_csv(temp_polars_csv)
            if temp_polars_csv.exists():
                print(f"   ✅ Polars CSV write successful!")
                temp_polars_csv.unlink()
            else:
                print("   ❌ Polars CSV write failed!")
            
            # Excel write
            df.write_excel(temp_polars_excel)
            if temp_polars_excel.exists():
                print(f"   ✅ Polars Excel write successful!")
                temp_polars_excel.unlink()
            else:
                print("   ❌ Polars Excel write failed!")
                
        except Exception as e:
            print(f"   ❌ Polars write error: {e}")
        
        print("\n🎉 Export functionality test completed!")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False
    
    return True

def test_specific_paths():
    """Test writing to specific paths that the exe might use."""
    print("\n🔍 Testing Specific Path Access\n")
    
    # Test current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    print(f"Current dir writable: {current_dir.exists() and current_dir.is_dir()}")
    
    # Test user home directory
    home_dir = Path.home()
    print(f"Home directory: {home_dir}")
    print(f"Home dir writable: {home_dir.exists() and home_dir.is_dir()}")
    
    # Test Documents folder
    docs_dir = home_dir / "Documents"
    print(f"Documents directory: {docs_dir}")
    print(f"Documents dir writable: {docs_dir.exists() and docs_dir.is_dir()}")
    
    # Try writing a test file in each location
    test_locations = [current_dir, home_dir, docs_dir]
    
    for location in test_locations:
        try:
            if location.exists() and location.is_dir():
                test_file = location / "export_test.txt"
                test_file.write_text("Test write operation")
                if test_file.exists():
                    print(f"   ✅ Write successful: {location}")
                    test_file.unlink()
                else:
                    print(f"   ❌ Write failed: {location}")
            else:
                print(f"   ❌ Location not accessible: {location}")
        except Exception as e:
            print(f"   ❌ Write error in {location}: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Excel Data Filter Pro - Export Functionality Test")
    print("=" * 60)
    
    # Test export functionality
    test_export_functionality()
    
    # Test path access
    test_specific_paths()
    
    print("\n" + "=" * 60)
    print("Test completed. Use this information to debug the executable.")
    print("=" * 60)