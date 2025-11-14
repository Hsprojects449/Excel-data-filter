"""
Main application window using PyQt6.
Orchestrates the UI components and business logic.
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from pathlib import Path
import polars as pl

from loguru import logger
from services.config_manager import config_manager
from services.logger import logger as app_logger
from core.excel_reader import ExcelReader
from core.filter_engine import FilterEngine, FilterRule as EngineFilterRule
from core.exporter import ExcelExporter
from ui.preview_table import PreviewTable
from ui.filter_panel import FilterPanel


class LoadDataThread(QThread):
    """Worker thread for loading Excel data asynchronously."""

    finished = pyqtSignal(pl.DataFrame)
    error = pyqtSignal(str)

    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath

    def run(self):
        try:
            reader = ExcelReader(self.filepath)
            sheet_names = reader.get_sheet_names()
            df = reader.read_sheet(sheet_names[0] if sheet_names else None)
            self.finished.emit(df)
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Data Filter")
        self.setGeometry(100, 100, 1600, 900)

        self.current_dataframe: pl.DataFrame = None
        self.filter_engine: FilterEngine = None
        self.current_filepath: str = None

        # Initialize UI
        self._init_ui()
        self._connect_signals()

        logger.info("Application started")

    def _init_ui(self):
        """Initialize the UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top toolbar with gradient background
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
        toolbar_layout.setSpacing(10)

        toolbar_widget = QWidget()
        toolbar_widget.setStyleSheet(
            """
            QWidget {
                background-color: #f5f5f5;
                border-bottom: 2px solid #e0e0e0;
            }
        """
        )
        toolbar_widget.setLayout(toolbar_layout)

        # App Title
        title = QLabel("📊 Excel Data Filter")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        toolbar_layout.addWidget(title)

        toolbar_layout.addSpacing(30)

        # Open file button
        open_btn = QPushButton("📁 Open Excel File")
        open_btn.setMinimumHeight(40)
        open_btn.setMinimumWidth(140)
        open_btn.clicked.connect(self._open_file)
        open_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        toolbar_layout.addWidget(open_btn)

        # Export button
        export_btn = QPushButton("💾 Export Filtered Data")
        export_btn.setMinimumHeight(40)
        export_btn.setMinimumWidth(150)
        export_btn.clicked.connect(self._export_data)
        export_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """
        )
        toolbar_layout.addWidget(export_btn)

        toolbar_layout.addStretch()

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #666;")
        toolbar_layout.addWidget(self.status_label)

        main_layout.addWidget(toolbar_widget)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """
        )
        main_layout.addWidget(self.progress_bar)

        # Filter Panel (top - full width)
        self.filter_panel = FilterPanel()
        self.filter_panel.filters_applied.connect(self._on_filters_applied)
        self.filter_panel.setStyleSheet(
            """
            FilterPanel {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
            }
        """
        )
        main_layout.addWidget(self.filter_panel, 0)

        # Preview table (below filters - takes remaining space)
        self.preview_table = PreviewTable()
        self.preview_table.setStyleSheet(
            """
            PreviewTable {
                background-color: white;
            }
        """
        )
        main_layout.addWidget(self.preview_table, 1)

        central_widget.setLayout(main_layout)

    def _connect_signals(self):
        """Connect signals for threading."""
        pass

    def _open_file(self):
        """Open file dialog to select Excel file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Excel File",
            config_manager.get("default_export_dir", str(Path.home())),
            "Excel Files (*.xlsx);;All Files (*)",
        )

        if filepath:
            self.current_filepath = filepath
            config_manager.update_recent_files(filepath)
            self._load_excel_file(filepath)

    def _load_excel_file(self, filepath: str):
        """Load Excel file in background thread."""
        self.status_label.setText(f"Loading {Path(filepath).name}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        self.load_thread = LoadDataThread(filepath)
        self.load_thread.finished.connect(self._on_data_loaded)
        self.load_thread.error.connect(self._on_load_error)
        self.load_thread.start()

    def _on_data_loaded(self, df: pl.DataFrame):
        """Handle successful data load."""
        self.current_dataframe = df
        self.filter_engine = FilterEngine(df)

        # Update filter panel with columns
        self.filter_panel.set_columns(df.columns)

        # Update preview table
        self.preview_table.set_data(df)

        stats = {
            "rows": len(df),
            "columns": len(df.columns),
        }
        self.status_label.setText(
            f"✅ Loaded {stats['rows']:,} rows × {stats['columns']} columns"
        )
        self.progress_bar.setVisible(False)

        logger.info(f"Data loaded successfully: {stats}")

    def _on_load_error(self, error: str):
        """Handle data load error."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Error loading file")
        QMessageBox.critical(self, "Error", f"Failed to load file:\n{error}")
        logger.error(f"Load error: {error}")

    def _on_filters_applied(self, filters: list, logic: str):
        """Handle filters applied from filter panel."""
        # If no filters (clear was clicked), show original data
        if not filters:
            self.preview_table.set_data(self.current_dataframe)
            self.status_label.setText(
                f"✅ Showing original data: {len(self.current_dataframe):,} rows"
            )
            logger.info("Filters cleared - showing original data")
            return

        if not self.filter_engine:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        try:
            self.status_label.setText("Filtering data...")
            self.progress_bar.setVisible(True)

            # Clear previous filters
            self.filter_engine.clear_filters()

            # Apply new filters
            for filter_data in filters:
                column = filter_data["column"]
                operator = filter_data["operator"]
                value = filter_data["value"]

                if not value:
                    QMessageBox.warning(
                        self, "Empty Value", f"Please enter a value for {column}"
                    )
                    return

                # Map UI operators to engine operators
                operator_map = {
                    "contains": "contains",
                    "is": "equals",
                    "not contains": "not_contains",
                    "starts with": "starts_with",
                    "ends with": "ends_with",
                    "equals": "equals",
                    "not equals": "not_equals",
                    ">": "gt",
                    "<": "lt",
                    ">=": "gte",
                    "<=": "lte",
                    "between": "between",
                }

                engine_operator = operator_map.get(operator, "contains")
                rule = EngineFilterRule(column, engine_operator, value)
                self.filter_engine.add_filter(rule)

            # Apply all filters with specified logic
            filtered_df = self.filter_engine.apply_filters()

            # Update preview with filtered data
            self.preview_table.set_data(filtered_df)

            # Update statistics
            stats = self.filter_engine.get_statistics()
            self.status_label.setText(
                f"✅ Filtered: {stats['filtered_rows']:,} rows "
                f"(removed {stats['rows_removed']:,} rows) | Logic: {logic}"
            )

            logger.info(f"Filters applied: {len(filters)} rules, Logic: {logic}")

        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            QMessageBox.critical(self, "Filter Error", str(e))
            self.status_label.setText("❌ Error applying filters")
        finally:
            self.progress_bar.setVisible(False)

    def _export_data(self):
        """Export filtered data to Excel."""
        if self.filter_engine is None or self.current_dataframe is None:
            QMessageBox.warning(self, "Warning", "No data loaded to export")
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel File",
            config_manager.get("default_export_dir", str(Path.home())),
            "Excel Files (*.xlsx)",
        )

        if output_path:
            try:
                self.status_label.setText("Exporting data...")
                self.progress_bar.setVisible(True)

                exporter = ExcelExporter(self.filter_engine.get_filtered_data())
                if exporter.export(output_path):
                    QMessageBox.information(
                        self, "Success", f"Data exported to:\n{output_path}"
                    )
                    self.status_label.setText(f"✅ Exported to {Path(output_path).name}")
                    logger.info(f"Export successful: {output_path}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to export data")
                    self.status_label.setText("❌ Export failed")
                    logger.error("Export failed")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export error: {str(e)}")
                logger.error(f"Export error: {e}")
                self.status_label.setText("❌ Export error")
            finally:
                self.progress_bar.setVisible(False)
