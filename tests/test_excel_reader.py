"""
Unit tests for the Excel reader.
"""

import pytest
import tempfile
from pathlib import Path
import polars as pl
from core.excel_reader import ExcelReader


@pytest.fixture
def sample_excel_file():
    """Create a temporary Excel file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        # Create sample data
        df = pl.DataFrame(
            {
                "ID": [1, 2, 3],
                "Name": ["Alice", "Bob", "Charlie"],
                "Age": [25, 30, 35],
            }
        )
        df.write_excel(tmp.name, sheet_name="Sheet1")
        tmp_path = tmp.name

    yield tmp_path

    # Cleanup
    Path(tmp_path).unlink()


def test_excel_reader_creation(sample_excel_file):
    """Test ExcelReader initialization."""
    reader = ExcelReader(sample_excel_file)
    assert reader.filepath.exists()


def test_get_sheet_names(sample_excel_file):
    """Test retrieving sheet names."""
    reader = ExcelReader(sample_excel_file)
    sheets = reader.get_sheet_names()
    assert len(sheets) > 0
    assert "Sheet1" in sheets


def test_read_sheet(sample_excel_file):
    """Test reading a sheet."""
    reader = ExcelReader(sample_excel_file)
    reader.get_sheet_names()
    df = reader.read_sheet("Sheet1")
    assert len(df) == 3
    assert len(df.columns) == 3


def test_get_statistics(sample_excel_file):
    """Test statistics retrieval."""
    reader = ExcelReader(sample_excel_file)
    reader.get_sheet_names()
    reader.read_sheet("Sheet1")
    stats = reader.get_statistics()
    assert stats["total_rows"] == 3
    assert stats["total_columns"] == 3
