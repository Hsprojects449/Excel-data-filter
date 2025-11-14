# Excel Data Filter - Quick Start Guide

## ⚡ Prerequisites

- **Python 3.11+** – [Download here](https://www.python.org/downloads/)
- Windows, macOS, or Linux
- ~500MB disk space

---

## 🚀 Installation & Setup

### Step 1: Install Python

**Windows:**
- Download Python from https://www.python.org/downloads/
- **Important:** Check ✅ "Add Python to PATH" during installation
- Verify: Open PowerShell and run:
  ```powershell
  python --version
  ```

**macOS/Linux:**
```bash
# macOS (with Homebrew)
brew install python3.11

# Ubuntu/Debian
sudo apt-get install python3.11 python3.11-venv
```

---

### Step 2: Setup the Project

**Windows (PowerShell):**
```powershell
cd "e:\ExcelDataFilter\excel_filter_app"
python -m venv venv
venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

**macOS/Linux (Terminal):**
```bash
cd ~/ExcelDataFilter/excel_filter_app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Or use the automated setup script:

**Windows:**
```powershell
cd "e:\ExcelDataFilter\excel_filter_app"
./setup.bat
```

**macOS/Linux:**
```bash
cd ~/ExcelDataFilter/excel_filter_app
chmod +x setup.sh
./setup.sh
```

---

### Step 3: Run the Application

```bash
# Activate virtual environment (if not already active)

# Windows
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate

# Run the app
python main.py
```

---

## 🧪 Running Tests

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # or venv\Scripts\Activate.ps1 on Windows

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_filter_engine.py

# Run with coverage
pytest tests/ --cov=core --cov=ui
```

---

## 📦 Building Standalone Executable

Once the app works, create a standalone `.exe` for Windows:

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1

# Install PyInstaller (if not already in requirements)
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name "ExcelDataFilter" main.py

# Executable will be in: dist/ExcelDataFilter.exe
```

For macOS/Linux:
```bash
pyinstaller --onefile --windowed --name "ExcelDataFilter" main.py
```

---

## 🛠️ Troubleshooting

### "Python not found"
- Ensure Python is installed and added to PATH
- Restart your terminal/PowerShell after installing Python
- Try: `python3 --version` instead of `python --version`

### "Module not found" errors
- Activate the virtual environment first
- Verify all packages installed: `pip list`
- Reinstall if needed: `pip install -r requirements.txt --force-reinstall`

### "PyQt6 import error"
- Ensure PyQt6 is installed: `pip install PyQt6==6.7.0`
- On some systems, you may need: `pip install PyQt6-sip`

### GUI doesn't open
- Verify PyQt6: `python -c "import PyQt6; print(PyQt6.__version__)"`
- On headless systems, you may need X11 forwarding

---

## 📁 Project Structure

```
excel_filter_app/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── setup.bat / setup.sh       # Setup scripts
├── config.json               # App config (created at runtime)
│
├── ui/
│   ├── main_window.py        # Main GUI window
│   └── preview_table.py      # Data preview table
│
├── core/
│   ├── excel_reader.py       # Read Excel files
│   ├── filter_engine.py      # Filtering logic
│   └── exporter.py           # Export to Excel/CSV
│
├── services/
│   ├── logger.py             # Logging setup
│   ├── config_manager.py     # Config management
│   └── temp_cleanup.py       # Temp file cleanup
│
├── tests/
│   ├── test_filter_engine.py
│   ├── test_excel_reader.py
│   └── test_exporter.py
│
└── logs/                      # Application logs (created at runtime)
```

---

## 🎯 Key Features

| Feature | Details |
|---------|---------|
| **High Performance** | Polars (10-20x faster than Pandas) |
| **Large Files** | Handles 1M+ row Excel files |
| **UI Responsiveness** | No freezing during data load/filter |
| **Advanced Filtering** | Equals, Contains, Regex, Numeric ranges, Date ranges |
| **Export Options** | Excel (.xlsx) and CSV (.csv) |
| **Logging** | Structured logs with loguru |
| **Cross-Platform** | Windows, macOS, Linux |

---

## 🔧 Development

### Adding a New Filter Type

Edit `core/filter_engine.py`:

```python
elif rule.operator == "custom_filter":
    # Your logic here
    return df.filter(...)
```

### Adding Tests

Create a test file in `tests/test_*.py`:

```python
def test_my_feature():
    # Test code
    assert condition
```

Run: `pytest tests/`

---

## 📝 License

MIT License – See LICENSE file for details

---

## 🤝 Support

For issues or questions:
1. Check troubleshooting section above
2. Review application logs in `logs/` directory
3. Verify dependencies: `pip list | grep -E "polars|PyQt6|openpyxl"`

---

**Happy filtering!** 🎉
