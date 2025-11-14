# PowerShell build script for Excel Data Filter Pro
Write-Host "Building Excel Data Filter Pro executable..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }

Write-Host "Cleaning completed." -ForegroundColor Green
Write-Host ""

# Build the executable
Write-Host "Starting PyInstaller build..." -ForegroundColor Yellow
& pyinstaller excel_data_filter.spec

Write-Host ""
if (Test-Path "dist\Excel_Data_Filter_Pro.exe") {
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host "Executable created at: dist\Excel_Data_Filter_Pro.exe" -ForegroundColor Cyan
    
    $fileSize = (Get-Item "dist\Excel_Data_Filter_Pro.exe").Length
    $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
    Write-Host "File size: $fileSizeMB MB" -ForegroundColor White
    
    Write-Host ""
    Write-Host "You can now distribute the Excel_Data_Filter_Pro.exe file to any Windows system." -ForegroundColor Green
} else {
    Write-Host "❌ Build failed! Check the output above for errors." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")