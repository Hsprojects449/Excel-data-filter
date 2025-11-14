"""
Excel file reading module.
Supports reading .xlsx files using openpyxl and Polars.
Handles large files efficiently with lazy loading.
"""

from pathlib import Path
from typing import Optional, Tuple
import polars as pl
from openpyxl import load_workbook
from loguru import logger


class ExcelReader:
    """Reads Excel files using Polars for performance."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.dataframe: Optional[pl.DataFrame] = None
        self.sheet_names: list = []

    def get_sheet_names(self) -> list:
        """Get all available sheet names in the Excel file."""
        try:
            wb = load_workbook(self.filepath, read_only=True, data_only=True)
            self.sheet_names = wb.sheetnames
            wb.close()
            logger.info(f"Found {len(self.sheet_names)} sheets in {self.filepath.name}")
            return self.sheet_names
        except Exception as e:
            logger.error(f"Failed to read sheet names: {e}")
            return []

    def read_sheet(self, sheet_name: str = None) -> pl.DataFrame:
        """
        Read a sheet into a Polars DataFrame.
        Uses lazy evaluation for better memory efficiency with large files.
        """
        try:
            if sheet_name is None:
                sheet_name = self.sheet_names[0] if self.sheet_names else "Sheet1"

            logger.info(f"Reading sheet '{sheet_name}' from {self.filepath.name}")

            # Read with Polars (automatically handles .xlsx)
            df = pl.read_excel(
                self.filepath,
                sheet_name=sheet_name,
            )

            self.dataframe = df
            logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            return df

        except Exception as e:
            logger.error(f"Failed to read Excel file: {e}")
            raise

    def get_column_info(self) -> dict:
        """Get metadata about columns (names, data types)."""
        if self.dataframe is None:
            return {}

        return {
            col: str(dtype)
            for col, dtype in zip(self.dataframe.columns, self.dataframe.schema.values())
        }

    def get_preview(self, n_rows: int = 100) -> pl.DataFrame:
        """Get first n rows as preview."""
        if self.dataframe is None:
            raise ValueError("No dataframe loaded. Call read_sheet() first.")
        return self.dataframe.head(n_rows)

    def get_statistics(self) -> dict:
        """Get basic statistics about the dataset."""
        if self.dataframe is None:
            return {}

        return {
            "total_rows": len(self.dataframe),
            "total_columns": len(self.dataframe.columns),
            "column_names": self.dataframe.columns,
            "memory_usage_mb": self.dataframe.estimated_size("mb"),
        }
