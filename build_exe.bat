@echo off
setlocal
echo Building XLS_Filter_Pro executable...
echo.

REM Activate virtual environment if present
if exist .venv\Scripts\activate call .venv\Scripts\activate

REM Clean previous builds (optional)
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo Cleaning completed.
echo.

REM Build the executable using the spec file
echo Starting PyInstaller build...
pyinstaller --noconfirm excel_data_filter.spec
if errorlevel 1 goto :fail

echo.
if exist "dist\XLS_Filter_Pro.exe" goto :success
goto :fail

:success
echo ✅ Build successful!
echo Executable: dist\XLS_Filter_Pro.exe
for %%I in ("dist\XLS_Filter_Pro.exe") do (echo Size: %%~zI bytes & echo Built: %%~tI)
echo.
echo You can now distribute XLS_Filter_Pro.exe.
endlocal
exit /b 0

:fail
echo ❌ Build failed! Check the PyInstaller output above for details.
if exist dist (
  echo Dist folder contents:
  dir /b dist
) else (
  echo No dist folder created.
)
endlocal
exit /b 1
