"""
Unit tests for the Excel exporter.
"""

import pytest
import tempfile
from pathlib import Path
import polars as pl
from core.exporter import ExcelExporter


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    return pl.DataFrame(
        {
            "ID": [1, 2, 3],
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [25, 30, 35],
        }
    )


def test_export_to_excel(sample_dataframe):
    """Test exporting to Excel."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_export.xlsx"
        exporter = ExcelExporter(sample_dataframe)
        success = exporter.export(str(output_path))

        assert success
        assert output_path.exists()


def test_export_to_csv(sample_dataframe):
    """Test exporting to CSV."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_export.csv"
        exporter = ExcelExporter(sample_dataframe)
        success = exporter.export_to_csv(str(output_path))

        assert success
        assert output_path.exists()
