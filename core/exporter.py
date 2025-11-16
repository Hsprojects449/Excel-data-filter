"""
Excel export module.
Efficiently exports filtered data to Excel files using xlsxwriter.
Enhanced with progress reporting and large dataset handling.
"""

from pathlib import Path
from typing import Optional, Callable
import polars as pl
import xlsxwriter
from loguru import logger


class ExcelExporter:
    """Exports Polars DataFrames to Excel files with enhanced features."""

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
        progress_callback: Optional[Callable[[int, str], None]] = None,
        chunk_size: int = 1000,
    ) -> bool:
        """
        Export dataframe to Excel file with progress reporting.

        Args:
            output_path: Path to save the Excel file
            sheet_name: Name of the worksheet
            include_index: Whether to include row index
            auto_format: Whether to apply auto-formatting (headers, borders, etc)
            progress_callback: Function to call with progress updates (percentage, message)
            chunk_size: Number of rows to process at once for large datasets

        Returns:
            True if successful, False otherwise
        """
        try:
            if progress_callback:
                progress_callback(5, "Preparing export...")

            output_path = Path(output_path)
            
            # Ensure output directory exists with better error handling
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                logger.error(f"Permission denied creating directory {output_path.parent}: {e}")
                if progress_callback:
                    progress_callback(0, f"Permission denied: Cannot create directory {output_path.parent}")
                return False
            except Exception as e:
                logger.error(f"Failed to create directory {output_path.parent}: {e}")
                if progress_callback:
                    progress_callback(0, f"Cannot create directory: {str(e)}")
                return False

            # Check dataset size and warn for very large exports
            total_rows = len(self.dataframe)
            total_cols = len(self.dataframe.columns)
            
            if progress_callback:
                progress_callback(10, f"Exporting {total_rows:,} rows × {total_cols} columns...")

            # Create Excel workbook with optimized settings for large data
            workbook_options = {}
            if total_rows > 10000:  # For large datasets
                workbook_options['constant_memory'] = True

            # Try to create workbook with better error handling
            try:
                workbook = xlsxwriter.Workbook(str(output_path), workbook_options)
                worksheet = workbook.add_worksheet(sheet_name)
            except PermissionError as e:
                logger.error(f"Permission denied creating Excel file {output_path}: {e}")
                if progress_callback:
                    progress_callback(0, f"Permission denied: Cannot write to {output_path}")
                return False
            except Exception as e:
                logger.error(f"Failed to create Excel workbook: {e}")
                if progress_callback:
                    progress_callback(0, f"Cannot create Excel file: {str(e)}")
                return False

            if progress_callback:
                progress_callback(15, "Setting up formatting...")

            # Define formats
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#4472C4",
                    "font_color": "white",
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "font_name": "Segoe UI",
                    "font_size": 11,
                }
            ) if auto_format else None

            data_format = workbook.add_format(
                {
                    "border": 1, 
                    "align": "left", 
                    "valign": "vcenter",
                    "font_name": "Segoe UI",
                    "font_size": 10,
                }
            ) if auto_format else None

            # Optimize for large datasets
            if auto_format and total_rows > 1000:
                # Disable some formatting for very large datasets to improve performance
                data_format.set_border(0)

            if progress_callback:
                progress_callback(20, "Writing headers...")

            # Write headers
            for col_idx, col_name in enumerate(self.dataframe.columns):
                if header_format:
                    worksheet.write(0, col_idx, col_name, header_format)
                else:
                    worksheet.write(0, col_idx, col_name)

            if progress_callback:
                progress_callback(25, "Writing data...")

            # Write data in chunks for better memory management
            rows_processed = 0
            total_progress_range = 70  # 25% to 95% for data writing
            
            # Convert to pandas for efficient chunked writing if dataset is large
            if total_rows > chunk_size:
                # Process in chunks
                for start_idx in range(0, total_rows, chunk_size):
                    end_idx = min(start_idx + chunk_size, total_rows)
                    chunk = self.dataframe.slice(start_idx, end_idx - start_idx)
                    
                    # Write chunk
                    for row_idx, row in enumerate(chunk.iter_rows(), start=start_idx + 1):
                        for col_idx, value in enumerate(row):
                            # Handle None/null values
                            display_value = "" if value is None else value
                            
                            if data_format and total_rows <= 5000:  # Only format smaller datasets
                                worksheet.write(row_idx, col_idx, display_value, data_format)
                            else:
                                worksheet.write(row_idx, col_idx, display_value)
                    
                    rows_processed = end_idx
                    if progress_callback:
                        progress = 25 + int((rows_processed / total_rows) * total_progress_range)
                        progress_callback(progress, f"Written {rows_processed:,} of {total_rows:,} rows...")

            else:
                # Small dataset - write directly
                for row_idx, row in enumerate(self.dataframe.iter_rows(), start=1):
                    for col_idx, value in enumerate(row):
                        # Handle None/null values  
                        display_value = "" if value is None else value
                        
                        if data_format:
                            worksheet.write(row_idx, col_idx, display_value, data_format)
                        else:
                            worksheet.write(row_idx, col_idx, display_value)
                    
                    # Update progress periodically
                    if row_idx % 100 == 0 and progress_callback:
                        progress = 25 + int((row_idx / total_rows) * total_progress_range)
                        progress_callback(progress, f"Written {row_idx:,} of {total_rows:,} rows...")

            if progress_callback:
                progress_callback(95, "Finalizing formatting...")

            # Auto-adjust column widths (skip for very large datasets)
            if auto_format and total_rows <= 10000:
                for col_idx, col_name in enumerate(self.dataframe.columns):
                    # Calculate optimal width
                    header_width = len(str(col_name))
                    
                    # Sample some data to estimate width (for performance)
                    sample_size = min(1000, total_rows)
                    sample_data = self.dataframe.head(sample_size)
                    
                    max_data_width = 0
                    try:
                        max_data_width = max(
                            (len(str(val)) for val in sample_data[col_name] if val is not None),
                            default=0,
                        )
                    except:
                        max_data_width = 10  # fallback width

                    optimal_width = max(header_width, max_data_width)
                    worksheet.set_column(col_idx, col_idx, min(optimal_width + 2, 50))

            # Add freeze panes for better navigation
            if auto_format:
                worksheet.freeze_panes(1, 0)  # Freeze header row

            if progress_callback:
                progress_callback(98, "Saving file...")

            workbook.close()

            if progress_callback:
                progress_callback(100, "Export completed!")

            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(
                f"Successfully exported {total_rows:,} rows to {output_path.name} "
                f"({file_size_mb:.1f} MB)"
            )
            return True

        except Exception as e:
            logger.error(f"Export failed: {e}")
            if progress_callback:
                progress_callback(0, f"Export failed: {str(e)}")
            return False

    def export_to_csv(
        self, 
        output_path: str, 
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> bool:
        """Export dataframe to CSV file with progress reporting."""
        try:
            if progress_callback:
                progress_callback(10, "Preparing CSV export...")

            output_path = Path(output_path)
            
            # Ensure output directory exists with better error handling
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                logger.error(f"Permission denied creating directory {output_path.parent}: {e}")
                if progress_callback:
                    progress_callback(0, f"Permission denied: Cannot create directory {output_path.parent}")
                return False
            except Exception as e:
                logger.error(f"Failed to create directory {output_path.parent}: {e}")
                if progress_callback:
                    progress_callback(0, f"Cannot create directory: {str(e)}")
                return False

            total_rows = len(self.dataframe)
            
            if progress_callback:
                progress_callback(30, f"Exporting {total_rows:,} rows to CSV...")

            # Use Polars' efficient CSV writer with UTF-8 encoding for international characters
            try:
                # Write CSV (Polars uses UTF-8 by default)
                # To ensure proper Telugu character support in Excel, write BOM manually
                csv_bytes = self.dataframe.write_csv().encode('utf-8')
                with open(output_path, 'wb') as f:
                    f.write(b'\xef\xbb\xbf')  # UTF-8 BOM
                    f.write(csv_bytes)
            except PermissionError as e:
                logger.error(f"Permission denied writing CSV file {output_path}: {e}")
                if progress_callback:
                    progress_callback(0, f"Permission denied: Cannot write to {output_path}")
                return False
            except Exception as e:
                logger.error(f"Failed to write CSV file: {e}")
                if progress_callback:
                    progress_callback(0, f"Cannot write CSV file: {str(e)}")
                return False
            
            if progress_callback:
                progress_callback(100, "CSV export completed!")

            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(
                f"Successfully exported {total_rows:,} rows to CSV: {output_path.name} "
                f"({file_size_mb:.1f} MB)"
            )
            return True

        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            if progress_callback:
                progress_callback(0, f"CSV export failed: {str(e)}")
            return False

    def estimate_export_time(self) -> str:
        """Estimate export time based on dataset size."""
        total_rows = len(self.dataframe)
        total_cols = len(self.dataframe.columns)
        
        # Rough estimates based on typical performance
        if total_rows < 1000:
            return "< 5 seconds"
        elif total_rows < 10000:
            return "5-15 seconds"
        elif total_rows < 50000:
            return "15-60 seconds"
        elif total_rows < 100000:
            return "1-3 minutes"
        else:
            return "3+ minutes (large dataset)"

    def get_export_info(self) -> dict:
        """Get information about the export dataset."""
        total_rows = len(self.dataframe)
        total_cols = len(self.dataframe.columns)
        estimated_size_mb = (total_rows * total_cols * 50) / (1024 * 1024)  # Rough estimate
        
        return {
            "rows": total_rows,
            "columns": total_cols,
            "estimated_file_size_mb": round(estimated_size_mb, 1),
            "estimated_export_time": self.estimate_export_time(),
            "is_large_dataset": total_rows > 10000
        }
