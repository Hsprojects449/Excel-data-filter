@echo off
echo Building Excel Data Filter Pro executable...
echo.

REM Activate virtual environment
call .venv\Scripts\activate

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo Cleaning completed.
echo.

REM Build the executable using the spec file
echo Starting PyInstaller build...
pyinstaller excel_data_filter.spec

echo.
if exist "dist\Excel_Data_Filter_Pro.exe" (
    echo ✅ Build successful! 
    echo Executable created at: dist\Excel_Data_Filter_Pro.exe
    echo File size: 
    for %%i in ("dist\Excel_Data_Filter_Pro.exe") do echo %%~zi bytes
    echo.
    echo You can now distribute the Excel_Data_Filter_Pro.exe file to any Windows system.
) else (
    echo ❌ Build failed! Check the output above for errors.
)

echo.
pause