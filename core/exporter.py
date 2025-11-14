"""
Excel export module.
Efficiently exports filtered data to Excel files using xlsxwriter.
"""

from pathlib import Path
from typing import Optional
import polars as pl
import xlsxwriter
from loguru import logger


class ExcelExporter:
    """Exports Polars DataFrames to Excel files."""

    def __init__(self, dataframe: pl.DataFrame):
        self.dataframe = dataframe
        self.workbook = None
        self.worksheet = None

    def export(
        self,
        output_path: str,
        sheet_name: str = "Filtered Data",
        include_index: bool = False,
        auto_format: bool = True,
    ) -> bool:
        """
        Export dataframe to Excel file.

        Args:
            output_path: Path to save the Excel file
            sheet_name: Name of the worksheet
            include_index: Whether to include row index
            auto_format: Whether to apply auto-formatting (headers, borders, etc)

        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Create Excel workbook
            workbook = xlsxwriter.Workbook(str(output_path))
            worksheet = workbook.add_worksheet(sheet_name)

            # Define formats
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#4472C4",
                    "font_color": "white",
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                }
            ) if auto_format else None

            data_format = workbook.add_format(
                {"border": 1, "align": "left", "valign": "vcenter"}
            ) if auto_format else None

            # Write headers
            for col_idx, col_name in enumerate(self.dataframe.columns):
                if header_format:
                    worksheet.write(0, col_idx, col_name, header_format)
                else:
                    worksheet.write(0, col_idx, col_name)

            # Write data
            for row_idx, row in enumerate(self.dataframe.iter_rows(), start=1):
                for col_idx, value in enumerate(row):
                    if data_format:
                        worksheet.write(row_idx, col_idx, value, data_format)
                    else:
                        worksheet.write(row_idx, col_idx, value)

            # Auto-adjust column widths
            if auto_format:
                for col_idx, col_name in enumerate(self.dataframe.columns):
                    max_width = max(
                        len(str(col_name)),
                        max(
                            (len(str(val)) for val in self.dataframe[col_name]),
                            default=0,
                        ),
                    )
                    worksheet.set_column(col_idx, col_idx, min(max_width + 2, 50))

            workbook.close()

            logger.info(
                f"Exported {len(self.dataframe)} rows to {output_path.name}"
            )
            return True

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False

    def export_to_csv(self, output_path: str) -> bool:
        """Export dataframe to CSV file."""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            self.dataframe.write_csv(output_path)
            logger.info(f"Exported {len(self.dataframe)} rows to CSV: {output_path.name}")
            return True

        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return False
