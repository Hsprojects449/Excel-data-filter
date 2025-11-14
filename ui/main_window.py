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
    QScrollArea,
    QSizePolicy,
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
    progress = pyqtSignal(int, str)  # percentage, status message

    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath

    def run(self):
        try:
            self.progress.emit(10, "Opening file...")
            reader = ExcelReader(self.filepath)
            
            self.progress.emit(30, "Reading sheet names...")
            sheet_names = reader.get_sheet_names()
            
            self.progress.emit(50, "Loading data...")
            df = reader.read_sheet(sheet_names[0] if sheet_names else None)
            
            self.progress.emit(80, "Processing data...")
            # Simulate processing time for user feedback
            self.msleep(200)
            
            self.progress.emit(100, "Complete!")
            self.finished.emit(df)
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Data Filter Pro")
        self.setGeometry(100, 100, 1700, 950)
        self.setMinimumSize(1200, 700)

        self.current_dataframe: pl.DataFrame = None
        self.filter_engine: FilterEngine = None
        self.current_filepath: str = None

        # Initialize UI
        self._init_ui()
        self._connect_signals()

        logger.info("Application started")

    def _init_ui(self):
        """Initialize the UI layout with sticky header and scrollable content."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout - vertical: header at top, scrollable content below
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === STICKY HEADER SECTION ===
        header_widget = self._create_header_widget()
        main_layout.addWidget(header_widget)

        # Progress bar (part of header section)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                text-align: center;
                height: 15px;
                font-size: 12px;
                font-weight: bold;
                background-color: #f8f9fa;
                color: #495057;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 5px;
            }
        """
        )
        main_layout.addWidget(self.progress_bar)

        # === SCROLLABLE CONTENT SECTION ===
        scrollable_content = self._create_scrollable_content()
        main_layout.addWidget(scrollable_content, 1)  # Takes remaining space

        central_widget.setLayout(main_layout)

    def _create_header_widget(self):
        """Create the sticky header widget with toolbar."""
        # Header container
        header_widget = QWidget()
        header_widget.setFixedHeight(55)  # Fixed height for sticky header
        header_widget.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-bottom: 3px solid #2e7d32;
            }
        """
        )

        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 8, 15, 8)
        header_layout.setSpacing(15)
        header_widget.setLayout(header_layout)

        # App Title with icon
        title = QLabel("📊 Excel Data Filter Pro")
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title.setStyleSheet(
            """
            QLabel {
                color: #ffffff;
                background: transparent;
                padding: 5px 0px;
                margin: 0px;
                font-weight: bold;
            }
        """
        )
        header_layout.addWidget(title)

        header_layout.addSpacing(20)

        # Open file button
        open_btn = QPushButton("📁 Open Excel File")
        open_btn.setFixedHeight(32)
        open_btn.setMinimumWidth(140)
        open_btn.clicked.connect(self._open_file)
        open_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34495e, stop:1 #2c3e50);
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e2833, stop:1 #2c3e50);
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
        """
        )
        header_layout.addWidget(open_btn)

        # Export button
        export_btn = QPushButton("💾 Export Filtered Data")
        export_btn.setFixedHeight(32)
        export_btn.setMinimumWidth(170)
        export_btn.clicked.connect(self._export_data)
        export_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #3498db);
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #21618c, stop:1 #2980b9);
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
        """
        )
        header_layout.addWidget(export_btn)

        header_layout.addStretch()

        # Status label
        self.status_label = QLabel("Ready to load Excel files")
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #ffffff;
                background: transparent;
                padding: 5px 8px;
                margin: 0px;
                border-radius: 4px;
                font-weight: 500;
            }
        """
        )
        header_layout.addWidget(self.status_label)

        return header_widget

    def _create_scrollable_content(self):
        """Create the scrollable content area containing filters and preview table."""
        # Create scrollable content area for filters and table
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Enable kinetic scrolling with smoother step sizes
        scroll_area.verticalScrollBar().setSingleStep(5)
        scroll_area.verticalScrollBar().setPageStep(150)
        scroll_area.horizontalScrollBar().setSingleStep(5)
        scroll_area.horizontalScrollBar().setPageStep(150)
        
        # Enable comprehensive touch gestures and kinetic scrolling
        scroll_area.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        scroll_area.setAttribute(Qt.WidgetAttribute.WA_TouchPadAcceptSingleTouchEvents, True)
        
        # Configure scroll area for better touch interaction
        scroll_area.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Enable momentum scrolling if available (Qt 6.2+)
        try:
            from PyQt6.QtWidgets import QScroller
            scroller = QScroller.scroller(scroll_area)
            if scroller:
                QScroller.grabGesture(scroll_area, QScroller.ScrollerGestureType.TouchGesture)
        except ImportError:
            pass  # QScroller not available in this Qt version
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget {
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 14px;
                border-radius: 7px;
                border: 1px solid #e0e0e0;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 30px;
                border: 1px solid #b0b0b0;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #808080;
            }
            QScrollBar:horizontal {
                background-color: #f5f5f5;
                height: 14px;
                border-radius: 7px;
                border: 1px solid #e0e0e0;
            }
            QScrollBar::handle:horizontal {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-width: 30px;
                border: 1px solid #b0b0b0;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::handle:horizontal:pressed {
                background-color: #808080;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: transparent;
                height: 0px;
                width: 0px;
            }
        """
        )

        # Content widget for scroll area
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        content_widget.setMinimumWidth(800)  # Set minimum width to trigger horizontal scroll if needed
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Filter Panel (top - expands as filters are added)
        self.filter_panel = FilterPanel()
        self.filter_panel.filters_applied.connect(self._on_filters_applied)
        self.filter_panel.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        self.filter_panel.setMinimumWidth(800)  # Ensure minimum width for horizontal scroll
        self.filter_panel.setStyleSheet(
            """
            FilterPanel {
                background-color: #ffffff;
                border-bottom: 2px solid #e9ecef;
            }
        """
        )
        content_layout.addWidget(self.filter_panel)

        # Preview table (below filters)
        self.preview_table = PreviewTable()
        self.preview_table.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        self.preview_table.setMinimumWidth(800)  # Ensure minimum width for horizontal scroll
        self.preview_table.setStyleSheet(
            """
            PreviewTable {
                background-color: #ffffff;
            }
        """
        )
        content_layout.addWidget(self.preview_table, 1)  # Give more space to table

        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        return scroll_area

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
        self.progress_bar.setValue(0)

        self.load_thread = LoadDataThread(filepath)
        self.load_thread.finished.connect(self._on_data_loaded)
        self.load_thread.error.connect(self._on_load_error)
        self.load_thread.progress.connect(self._on_load_progress)
        self.load_thread.start()

    def _on_load_progress(self, percentage: int, message: str):
        """Handle load progress updates."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(f"{message} ({percentage}%)")

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
