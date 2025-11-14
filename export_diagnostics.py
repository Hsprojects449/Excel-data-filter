"""
Diagnostic script to run alongside Excel_Data_Filter_Pro.exe 
to identify export issues and provide troubleshooting information.
"""
import sys
import os
from pathlib import Path
import tempfile
import subprocess

def check_permissions():
    """Check file system permissions in common locations."""
    print("=== PERMISSION DIAGNOSTICS ===")
    
    # Test locations
    locations = [
        Path.cwd(),
        Path.home(),
        Path.home() / "Documents",
        Path.home() / "Downloads",
        Path.home() / "Desktop",
        Path(tempfile.gettempdir())
    ]
    
    for location in locations:
        print(f"\nTesting: {location}")
        try:
            if location.exists():
                # Test directory read
                print(f"  Read access: {'✓' if location.is_dir() else '✗'}")
                
                # Test file creation
                test_file = location / "excel_filter_test.tmp"
                try:
                    test_file.write_text("test")
                    if test_file.exists():
                        print("  Write access: ✓")
                        test_file.unlink()
                    else:
                        print("  Write access: ✗ (file not created)")
                except Exception as e:
                    print(f"  Write access: ✗ ({e})")
            else:
                print("  Location does not exist")
        except Exception as e:
            print(f"  Error accessing location: {e}")

def check_executable_environment():
    """Check the environment when running as executable vs development."""
    print("\n=== EXECUTABLE ENVIRONMENT ===")
    
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Script location: {Path(__file__).parent}")
    print(f"Home directory: {Path.home()}")
    print(f"Temp directory: {Path(tempfile.gettempdir())}")
    
    # Check if running from PyInstaller bundle
    if getattr(sys, 'frozen', False):
        print("Running as PyInstaller executable")
        print(f"Executable path: {sys.executable}")
        print(f"Bundle directory: {sys._MEIPASS if hasattr(sys, '_MEIPASS') else 'Not available'}")
    else:
        print("Running in development environment")
    
    # Check environment variables that might affect file operations
    important_vars = ['TEMP', 'TMP', 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA']
    print("\nEnvironment variables:")
    for var in important_vars:
        value = os.environ.get(var, 'Not set')
        print(f"  {var}: {value}")

def test_export_libraries():
    """Test if export libraries can be imported and used."""
    print("\n=== LIBRARY TESTING ===")
    
    try:
        import xlsxwriter
        print("✓ xlsxwriter import successful")
        
        # Test xlsxwriter in temp directory
        temp_dir = Path(tempfile.gettempdir())
        test_xlsx = temp_dir / "diagnostic_test.xlsx"
        
        workbook = xlsxwriter.Workbook(str(test_xlsx))
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, "Test")
        workbook.close()
        
        if test_xlsx.exists():
            size = test_xlsx.stat().st_size
            print(f"✓ xlsxwriter file creation successful ({size} bytes)")
            test_xlsx.unlink()
        else:
            print("✗ xlsxwriter file creation failed")
            
    except Exception as e:
        print(f"✗ xlsxwriter error: {e}")
    
    try:
        import polars as pl
        print("✓ polars import successful")
        
        # Test polars CSV export
        df = pl.DataFrame({"test": [1, 2, 3]})
        temp_csv = Path(tempfile.gettempdir()) / "diagnostic_test.csv"
        
        df.write_csv(temp_csv)
        if temp_csv.exists():
            size = temp_csv.stat().st_size
            print(f"✓ polars CSV export successful ({size} bytes)")
            temp_csv.unlink()
        else:
            print("✗ polars CSV export failed")
            
    except Exception as e:
        print(f"✗ polars error: {e}")

def check_dialog_paths():
    """Test default paths that file dialogs might use."""
    print("\n=== FILE DIALOG PATH TESTING ===")
    
    # Common file dialog default paths
    default_paths = [
        Path.home() / "Documents",
        Path.home() / "Downloads", 
        Path.home() / "Desktop",
        Path.cwd()
    ]
    
    for path in default_paths:
        print(f"\nTesting default path: {path}")
        if path.exists():
            try:
                # Test creating a file with Excel extension
                test_excel = path / "excel_filter_test.xlsx"
                test_excel.touch()
                if test_excel.exists():
                    print(f"  ✓ Can create Excel files here")
                    test_excel.unlink()
                else:
                    print(f"  ✗ Cannot create Excel files here")
            except Exception as e:
                print(f"  ✗ Error creating files: {e}")
        else:
            print(f"  Path does not exist")

def main():
    print("=" * 60)
    print("Excel Data Filter Pro - Export Diagnostics")
    print("=" * 60)
    
    check_executable_environment()
    check_permissions()
    test_export_libraries()
    check_dialog_paths()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 60)
    
    print("\nIf export is still failing, try:")
    print("1. Run as Administrator")
    print("2. Save to Documents folder instead of default location")
    print("3. Check Windows Defender or antivirus settings")
    print("4. Ensure the destination folder is not read-only")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()