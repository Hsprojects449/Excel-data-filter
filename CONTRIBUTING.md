# Development & Contribution Guide

## 🎯 Getting Started

### Prerequisites
- Python 3.11+
- Virtual environment (venv)
- All dependencies installed (see QUICKSTART.md)

### Project Setup

```bash
# Clone/navigate to project
cd excel_filter_app

# Create and activate venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## 📁 Project Structure

```
excel_filter_app/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── setup.bat / setup.sh    # Setup scripts
├── pytest.ini             # Pytest configuration
│
├── ui/                    # User Interface (PyQt6)
│   ├── __init__.py
│   ├── main_window.py     # Main window and orchestration
│   └── preview_table.py   # Table widget with pagination
│
├── core/                  # Business Logic
│   ├── __init__.py
│   ├── excel_reader.py    # Excel file I/O
│   ├── filter_engine.py   # Filtering logic
│   └── exporter.py        # Export to Excel/CSV
│
├── services/              # Utilities & Services
│   ├── __init__.py
│   ├── logger.py          # Logging setup (loguru)
│   ├── config_manager.py  # Configuration management
│   └── temp_cleanup.py    # Temp file cleanup
│
├── tests/                 # Unit Tests (pytest)
│   ├── __init__.py
│   ├── test_filter_engine.py
│   ├── test_excel_reader.py
│   └── test_exporter.py
│
├── logs/                  # Application logs (created at runtime)
├── config.json           # Configuration (created at runtime)
│
├── README.md             # Project overview
├── QUICKSTART.md         # Setup and usage guide
├── ARCHITECTURE.md       # Technical architecture
└── CONTRIBUTING.md       # This file
```

---

## 🚀 Running the Application

### Development Mode (with logging)

```bash
# Activate venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1

# Run directly
python main.py

# Logs appear in both console and logs/app_*.log
```

### Debug Mode (with verbose logging)

Edit `services/logger.py` and change `level="DEBUG"` for more details.

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_filter_engine.py -v
```

### Run Specific Test

```bash
pytest tests/test_filter_engine.py::test_apply_equals_filter -v
```

### Run with Coverage

```bash
pytest tests/ --cov=core --cov=ui --cov-report=html
```

Coverage report will be in `htmlcov/index.html`

---

## 💻 Code Style & Standards

### Python Style Guide

- Follow **PEP 8** standards
- Use **type hints** where applicable
- Keep functions under 50 lines
- Use **docstrings** for modules and functions

### Example

```python
"""
Module docstring explaining purpose.
"""

from typing import Optional, List
import polars as pl
from loguru import logger


def process_data(df: pl.DataFrame, threshold: int = 100) -> Optional[pl.DataFrame]:
    """
    Process DataFrame with given threshold.
    
    Args:
        df: Input DataFrame
        threshold: Minimum value threshold
        
    Returns:
        Filtered DataFrame or None if error
    """
    try:
        return df.filter(pl.col("value") > threshold)
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return None
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `FilterEngine`, `ExcelReader`)
- **Functions**: `snake_case` (e.g., `apply_filters`, `read_sheet`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_ROWS`, `DEFAULT_CONFIG`)
- **Private methods**: Prefix with `_` (e.g., `_apply_single_filter`)

---

## 🔧 Development Tasks

### Adding a New Filter Type

1. **Edit `core/filter_engine.py`:**

```python
elif rule.operator == "starts_with":
    return df.filter(pl.col(rule.column).str.starts_with(str(rule.value)))
```

2. **Add Test in `tests/test_filter_engine.py`:**

```python
def test_apply_starts_with_filter(sample_dataframe):
    """Test starts_with filter."""
    engine = FilterEngine(sample_dataframe)
    rule = FilterRule("Name", "starts_with", "Al")
    engine.add_filter(rule)
    result = engine.apply_filters()
    assert len(result) == 1  # Alice
```

3. **Run Tests:**

```bash
pytest tests/test_filter_engine.py::test_apply_starts_with_filter -v
```

### Adding a UI Component

1. **Create new file in `ui/`:**

```python
# ui/filter_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

class FilterDialog(QDialog):
    """Dialog for configuring filters."""
    
    filter_applied = pyqtSignal(dict)  # Signal to emit filter config
    
    def __init__(self):
        super().__init__()
        self._init_ui()
```

2. **Integrate in `ui/main_window.py`:**

```python
from ui.filter_dialog import FilterDialog

# In MainWindow class
def _show_filter_dialog(self):
    dialog = FilterDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Handle filter config
        pass
```

### Adding a Service

1. **Create new file in `services/`:**

```python
# services/cache_manager.py
class CacheManager:
    """Manages caching of filtered results."""
    
    def __init__(self):
        self.cache = {}
    
    def cache_filter(self, key: str, data: pl.DataFrame) -> None:
        """Cache filtered data."""
        self.cache[key] = data
```

2. **Use in main components:**

```python
from services.cache_manager import CacheManager

cache = CacheManager()
```

---

## 🐛 Debugging Tips

### Enable Debug Logging

Edit `services/logger.py`:
```python
logger.add(sys.stdout, level="DEBUG", ...)  # Change to DEBUG
```

### Print DataFrame Info

```python
import polars as pl

df = pl.read_excel("file.xlsx")
print(df.schema)        # Column names and types
print(df.head())        # First 5 rows
print(df.describe())    # Statistics
print(f"Shape: {df.shape}")  # Rows x Columns
```

### Check Current Filters

```python
engine = FilterEngine(df)
print(f"Applied filters: {len(engine.applied_filters)}")
for rule in engine.applied_filters:
    print(f"  {rule.column} {rule.operator} {rule.value}")
```

### Inspect UI State

```python
# In main_window.py debug code
print(f"Current dataframe shape: {self.current_dataframe.shape}")
print(f"Filter count: {len(self.filter_engine.applied_filters)}")
```

---

## 📝 Writing Tests

### Test Structure

```python
import pytest
from core.filter_engine import FilterEngine, FilterRule

@pytest.fixture
def sample_data():
    """Fixture for test data."""
    import polars as pl
    return pl.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"]
    })

def test_feature(sample_data):
    """Test description."""
    # Arrange
    engine = FilterEngine(sample_data)
    
    # Act
    engine.add_filter(FilterRule("id", "gt", 1))
    result = engine.apply_filters()
    
    # Assert
    assert len(result) == 2
```

### Test Checklist

- ✅ Test normal cases
- ✅ Test edge cases (empty data, None values)
- ✅ Test error conditions
- ✅ Test with large datasets (1000+ rows)
- ✅ Use descriptive test names

---

## 🔄 Git Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/my-feature
```

### Before Committing

```bash
# Run tests
pytest tests/

# Check code style
python -m py_compile *.py core/*.py ui/*.py services/*.py

# Format code (optional with black)
# black .
```

### Commit Message Format

```
feat: Add new filter type
  - Implemented starts_with filter
  - Added corresponding tests
  - Updated documentation

fix: Handle empty dataframes
  - Fixed IndexError when dataframe is empty
  - Added defensive check in filter_engine.py

docs: Update README with filter examples
```

---

## 🚀 Building Release

### Create Standalone Executable

```bash
# Activate venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1

# Build with PyInstaller
pyinstaller --onefile --windowed --name "ExcelDataFilter" \
    --icon=icon.png \
    --distpath=./dist \
    --buildpath=./build \
    main.py

# Result: dist/ExcelDataFilter.exe (Windows) or dist/ExcelDataFilter (Mac/Linux)
```

### Create Distribution Package

```bash
# Package with setuptools
pip install build
python -m build
# Creates: dist/excel_filter_app-1.0.0-py3-none-any.whl
```

---

## 📊 Performance Profiling

### Profile Execution Time

```python
import time
from loguru import logger

start = time.time()
# Code to profile
elapsed = time.time() - start
logger.info(f"Operation took {elapsed:.2f}s")
```

### Profile Memory Usage

```python
import tracemalloc

tracemalloc.start()
# Code to profile
current, peak = tracemalloc.get_traced_memory()
logger.info(f"Current: {current / 1024 / 1024:.1f}MB, Peak: {peak / 1024 / 1024:.1f}MB")
```

---

## 🎓 Learning Resources

- **Polars Documentation**: https://www.pola-rs.com/
- **PyQt6 Documentation**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Python Best Practices**: https://pep8.org/
- **Pytest Guide**: https://docs.pytest.org/

---

## 🤝 Getting Help

1. Check existing issues in project tracker
2. Review logs in `logs/` directory
3. Enable debug logging for detailed information
4. Run tests to isolate issues: `pytest -v`
5. Check documentation in `README.md` and `ARCHITECTURE.md`

---

## 📋 Checklist for Contributions

- [ ] Code follows PEP 8 style
- [ ] Tests added for new features
- [ ] All tests pass: `pytest tests/`
- [ ] Docstrings added to new functions
- [ ] No hardcoded values (use config or constants)
- [ ] Error handling implemented
- [ ] Logging added for debugging
- [ ] Documentation updated if needed

---

**Happy coding! 🚀**
