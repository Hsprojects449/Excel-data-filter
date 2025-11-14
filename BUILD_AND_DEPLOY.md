# Excel Data Filter - Build & Deployment Guide

## 🎯 Overview

This guide covers building, testing, packaging, and deploying the Excel Data Filter application across different platforms.

---

## 🧪 Pre-Build Checklist

Before building any release, verify:

```bash
# 1. All tests pass
pytest tests/ -v

# 2. No linting issues
python -m py_compile core/*.py ui/*.py services/*.py main.py

# 3. No import errors
python -c "from ui.main_window import MainWindow; print('✓ Imports OK')"

# 4. Application runs
python main.py &  # Start and manually verify it works
```

---

## 📦 Building Standalone Executable

### Windows

#### Step 1: Create Virtual Environment and Install Dependencies

```powershell
# Navigate to project
cd "e:\ExcelDataFilter\excel_filter_app"

# Create venv
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 2: Build Executable

```powershell
# Install PyInstaller
pip install pyinstaller==6.1.0

# Build one-file executable
pyinstaller --onefile `
  --windowed `
  --name "ExcelDataFilter" `
  --distpath "./dist" `
  --buildpath "./build" `
  --specpath "./build" `
  --add-data "logs:logs" `
  main.py

# Result: dist\ExcelDataFilter.exe
```

#### Step 3: Verify Executable

```powershell
# Test the executable
.\dist\ExcelDataFilter.exe

# Check file size
Get-Item .\dist\ExcelDataFilter.exe | Format-List Length
```

#### Step 4: Create Installer (Optional)

```powershell
# Install NSIS (Nullsoft Scriptable Install System)
# Download: https://nsis.sourceforge.io/

# Create NSIS script (setup.nsi):
# ... see example below ...

# Build installer
"C:\Program Files (x86)\NSIS\makensis.exe" setup.nsi

# Result: ExcelDataFilter-1.0.0-Setup.exe
```

### macOS

#### Step 1: Setup Virtual Environment

```bash
cd ~/ExcelDataFilter/excel_filter_app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 2: Build Executable

```bash
pip install pyinstaller==6.1.0

pyinstaller --onefile \
  --windowed \
  --name "ExcelDataFilter" \
  --distpath "./dist" \
  --buildpath "./build" \
  --specpath "./build" \
  --icon="icon.icns" \
  main.py

# Result: dist/ExcelDataFilter
```

#### Step 3: Create App Bundle

```bash
# PyInstaller creates a standalone binary, but to make it a proper macOS app:

mkdir -p dist/ExcelDataFilter.app/Contents/MacOS
mkdir -p dist/ExcelDataFilter.app/Contents/Resources

cp dist/ExcelDataFilter dist/ExcelDataFilter.app/Contents/MacOS/

# Create Info.plist
cat > dist/ExcelDataFilter.app/Contents/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>ExcelDataFilter</string>
    <key>CFBundleIdentifier</key>
    <string>com.excelldatafilter.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Excel Data Filter</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
</dict>
</plist>
EOF

# Create DMG (optional)
hdiutil create -volname "ExcelDataFilter" -srcfolder dist/ExcelDataFilter.app -ov -format UDZO ExcelDataFilter-1.0.0.dmg
```

### Linux

#### Step 1: Setup Virtual Environment

```bash
cd ~/ExcelDataFilter/excel_filter_app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 2: Build Executable

```bash
pip install pyinstaller==6.1.0

pyinstaller --onefile \
  --windowed \
  --name "ExcelDataFilter" \
  --distpath "./dist" \
  --buildpath "./build" \
  --specpath "./build" \
  main.py

# Result: dist/ExcelDataFilter
```

#### Step 3: Create Desktop Entry

```bash
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/excelfilter.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Excel Data Filter
Exec=/path/to/dist/ExcelDataFilter
Icon=application-vnd.ms-excel
Categories=Utility;Office;
EOF

# Make executable
chmod +x ~/dist/ExcelDataFilter
```

---

## 🧪 Testing the Build

### Unit Tests

```bash
# Activate venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov=ui --cov-report=term-missing
```

### Integration Testing

```bash
# Test standalone executable
./dist/ExcelDataFilter  # macOS/Linux
# or
.\dist\ExcelDataFilter.exe  # Windows

# Manual tests:
# 1. Open a sample Excel file
# 2. Apply filters
# 3. Export results
# 4. Check logs in application directory
```

### Performance Testing

```python
# Create test_performance.py
import time
import polars as pl
from core.excel_reader import ExcelReader
from core.filter_engine import FilterEngine, FilterRule

# Generate large test file
df = pl.DataFrame({
    "id": range(100000),
    "value": range(100000),
    "name": ["Item " + str(i) for i in range(100000)]
})

# Time the operations
start = time.time()
engine = FilterEngine(df)
engine.add_filter(FilterRule("value", "gt", 50000))
result = engine.apply_filters()
elapsed = time.time() - start

print(f"Filtered 100k rows in {elapsed:.2f}s")
```

---

## 📊 Release Versioning

### Version Format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Update Version

```bash
# Update in main.py
# Update in requirements.txt comments
# Update in CONTRIBUTING.md
# Update in ARCHITECTURE.md

# Tag in git
git tag v1.0.0
git push origin v1.0.0
```

---

## 🔐 Security Considerations

### Before Release

- [ ] Verify no hardcoded passwords or secrets
- [ ] Check for external dependencies vulnerabilities
- [ ] Review file permissions (especially temp files)
- [ ] Verify no debug mode enabled in production
- [ ] Check logging doesn't expose sensitive data

### Dependency Audit

```bash
# Install safety
pip install safety

# Check for known vulnerabilities
safety check

# Or use pip-audit
pip install pip-audit
pip-audit
```

---

## 📈 Deployment Checklist

### Before Releasing to Users

- [ ] All tests pass (`pytest tests/`)
- [ ] Code reviewed by team
- [ ] Performance tested with 1M+ row files
- [ ] UI tested on target OS (Windows/Mac/Linux)
- [ ] Error handling verified
- [ ] Logging verified
- [ ] Documentation complete
- [ ] Version number updated
- [ ] Release notes prepared

### Release Process

1. **Create Release Branch**
   ```bash
   git checkout -b release/v1.0.0
   ```

2. **Update Version Files**
   - `main.py`: Update `__version__`
   - `requirements.txt`: Add comments with version
   - Create `RELEASE_NOTES.md`

3. **Final Testing**
   ```bash
   pytest tests/
   python main.py  # Manual verification
   ```

4. **Build Executables**
   ```bash
   # Build on each platform
   # Windows, macOS, Linux
   ```

5. **Create Distribution**
   ```bash
   # Create release archives
   # Create checksums (SHA256)
   ```

6. **Tag Release**
   ```bash
   git commit -am "Release v1.0.0"
   git tag -a v1.0.0 -m "Version 1.0.0 release"
   git push origin v1.0.0
   ```

7. **Publish**
   - Upload executables to release hosting
   - Create GitHub release with notes
   - Update website/documentation

---

## 🔧 Continuous Integration (GitHub Actions Example)

```yaml
# .github/workflows/build.yml
name: Build Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          source venv/bin/activate
          pytest tests/
      
      - name: Build executable
        run: |
          source venv/bin/activate
          pyinstaller --onefile --windowed main.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-build
          path: dist/
```

---

## 📝 Release Notes Template

```markdown
# Excel Data Filter v1.0.0

**Release Date**: December 2024

## ✨ Features

- High-performance Excel filtering for 1M+ rows
- PyQt6 professional GUI
- Multiple filter types (equals, contains, regex, numeric ranges)
- Efficient export to Excel and CSV
- Offline operation with no dependencies

## 🐛 Bug Fixes

- Fixed memory leak in filter engine
- Improved error handling for corrupted Excel files

## 🚀 Performance

- 10-20x faster than pandas-based solutions
- Instant pagination for large datasets
- Efficient streaming export

## 📦 Downloads

- Windows: ExcelDataFilter-1.0.0.exe
- macOS: ExcelDataFilter-1.0.0.dmg
- Linux: ExcelDataFilter-1.0.0.tar.gz

## 🔗 Links

- Documentation: [README.md](README.md)
- Quick Start: [QUICKSTART.md](QUICKSTART.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
```

---

## 🐛 Troubleshooting Builds

### PyInstaller Issues

```bash
# If PyInstaller build fails, try:

# 1. Clean previous builds
rm -rf build dist *.spec

# 2. Recreate venv
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Rebuild
pyinstaller --onefile --windowed main.py

# 4. Check for import errors
python -c "from ui.main_window import MainWindow"
```

### Missing Modules

```bash
# Check all imports are available
python -c "
import polars
import openpyxl
import xlsxwriter
import PyQt6
import loguru
print('All imports OK')
"
```

### Size Optimization

```bash
# For smaller executables:
pyinstaller --onefile --windowed \
  --strip \
  --compress=9 \
  main.py
```

---

## 📞 Support & Updates

- Check GitHub releases: https://github.com/.../releases
- Report issues: https://github.com/.../issues
- Documentation: README.md, QUICKSTART.md, ARCHITECTURE.md

---

**Happy building! 🚀**
